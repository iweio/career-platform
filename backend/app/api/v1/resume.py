import json
import logging
import os
import uuid
from fastapi import APIRouter, Depends, UploadFile, File, Form
from app.agents.registry import get_agent
from app.middleware.auth import get_current_user
from app.schemas.resume import ResumeExtractRequest
from app.config import settings
from app.rag.retrievers import resume_retriever

logger = logging.getLogger(__name__)
router = APIRouter()


async def save_upload(upload: UploadFile | None) -> str:
    if not upload or not upload.filename:
        return ""
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    ext = os.path.splitext(upload.filename)[1]
    path = os.path.join(settings.UPLOAD_DIR, f"{uuid.uuid4().hex}{ext}")
    with open(path, "wb") as f:
        f.write(await upload.read())
    return path


def _profile_to_text(profile: dict) -> str:
    """Convert structured user_profile dict into a single text block for embedding."""
    parts = []
    for section, content in profile.items():
        if isinstance(content, dict):
            inner = content.get("content", "") or "，".join(f"{k}: {v}" for k, v in content.items())
            parts.append(f"{section}：{inner}")
        elif isinstance(content, list):
            parts.append(f"{section}：{'、'.join(str(c) for c in content)}")
        elif content:
            parts.append(f"{section}：{content}")
    return "\n".join(parts)


def _extract_name(profile: dict) -> str:
    basic = profile.get("基本信息", {})
    if isinstance(basic, dict):
        inner = basic.get("content", "")
        if "姓名" in str(inner):
            name_part = str(inner).split("姓名：")[-1].split("姓名:")[-1].strip()
            return name_part.split("，")[0].split(",")[0].split("；")[0].strip()
    return ""


def _extract_skills(profile: dict) -> str:
    skills = profile.get("技能清单", profile.get("技能", profile.get("技能标签", "")))
    if isinstance(skills, dict):
        skills = skills.get("content", skills)
    if isinstance(skills, str):
        return skills
    if isinstance(skills, list):
        return "、".join(str(s) for s in skills[:10])
    return ""


async def _store_resume_vector(user_id: int, profile_data: dict) -> None:
    """Store the user's profile embedding into ChromaDB RAG."""
    if not profile_data:
        return
    try:
        profile_text = _profile_to_text(profile_data)
        name = _extract_name(profile_data)
        skills = _extract_skills(profile_data)
        resume_retriever.store(user_id, profile_text, {
            "name": name,
            "top_skills": skills,
        })
        print("[RAG] Stored resume vector for user %d" % user_id, flush=True)
    except Exception:
        logger.exception("[RAG] Failed to store resume vector")


async def _run_resume_agent(input_data: dict) -> dict:
    try:
        agent = get_agent("resume_analyzer")
        return await agent.run(input_data)
    except Exception:
        logger.exception("resume_analyzer agent failed")
        return {"error": "Agent execution failed"}


@router.post("/extract")
async def extract_resume(
    input_text: str = Form(""),
    doc: UploadFile = File(None),
    image: UploadFile = File(None),
    user: dict = Depends(get_current_user),
):
    result = await _run_resume_agent({
        "input_text": input_text,
        "file_path": await save_upload(doc),
        "image_path": await save_upload(image),
        "user_id": user["user_id"],
    })
    if result.get("error"):
        return {"success": False, "error": result["error"]}
    await _store_resume_vector(user["user_id"], result.get("user_profile", {}))
    return {"success": True, "data": result}


@router.post("/supplement")
async def supplement_resume(
    req: ResumeExtractRequest,
    user: dict = Depends(get_current_user),
):
    result = await _run_resume_agent({
        "input_text": "",
        "supplement_text": req.supplement_text,
        "supplement_count": req.supplement_count,
        "user_profile": req.user_profile,
        "user_id": user["user_id"],
    })
    if result.get("error"):
        return {"success": False, "error": result["error"]}
    await _store_resume_vector(user["user_id"], result.get("user_profile", {}))
    return {"success": True, "data": result}


@router.post("/analyze")
async def analyze_resume(
    req: ResumeExtractRequest,
    user: dict = Depends(get_current_user),
):
    result = await _run_resume_agent({
        "input_text": json.dumps(req.user_profile or {}, ensure_ascii=False),
        "user_id": user["user_id"],
    })
    if result.get("error"):
        return {"success": False, "error": result["error"]}
    await _store_resume_vector(user["user_id"], result.get("user_profile", {}))
    return {"success": True, "data": result}
