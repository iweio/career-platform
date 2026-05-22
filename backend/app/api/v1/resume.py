import json
import logging
import os
import uuid
from fastapi import APIRouter, Depends, UploadFile, File, Form
from app.agents.registry import get_agent
from app.middleware.auth import get_current_user
from app.schemas.resume import ResumeExtractRequest
from app.config import settings

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
    if "error" in result:
        return {"success": False, "error": result["error"]}
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
    if "error" in result:
        return {"success": False, "error": result["error"]}
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
    if "error" in result:
        return {"success": False, "error": result["error"]}
    return {"success": True, "data": result}
