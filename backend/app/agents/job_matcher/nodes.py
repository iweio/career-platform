"""LangGraph nodes for the Job Matcher agent."""

import asyncio
import json
from typing import Dict

from langchain_core.messages import HumanMessage, SystemMessage

from app.agents.llm_factory import get_llm
from app.agents.job_matcher.state import JobMatcherState
from app.agents.job_matcher.prompts import WEIGHT_PROMPT, MATCH_PROMPT, SELF_REFLECT_PROMPT
from app.agents.job_matcher import db_utils
from app.rag.retrievers import resume_job_matcher, resume_retriever


async def load_user_profile(state: JobMatcherState) -> Dict:
    uid = state["user_id"]
    profile = await db_utils.get_user_profile(uid)
    if profile:
        return {"user_profile": profile.get("profile_data", {})}

    # If no user profile yet, check if there's one in the state
    if state.get("user_profile"):
        profile_data = state["user_profile"]
        await db_utils.save_user_profile(uid, profile_data)
        return {"user_profile": profile_data}

    return {"user_profile": {"error": "No user profile found. Please complete resume extraction first."}}


async def retrieve_candidates(state: JobMatcherState) -> Dict:
    """RAG: use resume text to find top matching job categories via vector search.
    Returns category IDs (from job_categories table), not individual job IDs."""
    profile = state.get("user_profile", {})
    uid = state["user_id"]

    # Try stored resume vector first (better formatted text for embedding)
    stored = resume_retriever.get_vector(uid)
    profile_text = stored if stored else json.dumps(profile, ensure_ascii=False)

    category_ids = resume_job_matcher.retrieve_candidates(profile_text, top_k=10)
    return {"category_ids": category_ids}


async def load_job_details(state: JobMatcherState) -> Dict:
    ids = state.get("category_ids", [])
    if not ids:
        return {"job_details": [], "match_results": []}

    details = await db_utils.get_jobs_by_category([int(i) for i in ids])
    return {"job_details": details}


async def llm_match(state: JobMatcherState) -> Dict:
    """LLM-based dimension matching for each job."""
    profile = state.get("user_profile", {})
    jobs = state.get("job_details", [])

    if not jobs:
        return {"match_results": []}

    llm = get_llm(temperature=0.3)

    async def match_one(job: dict) -> dict:
        profile_text = json.dumps(profile, ensure_ascii=False)
        job_text = json.dumps(job, ensure_ascii=False)

        # Determine weights
        weight_msg = llm.invoke([
            SystemMessage(content="输出纯JSON，不要加任何前缀说明。"),
            HumanMessage(content=WEIGHT_PROMPT.format(job_info=job_text)),
        ])
        try:
            weights = _parse_json(weight_msg.content)
        except Exception:
            weights = {}

        # Match
        match_msg = llm.invoke([
            SystemMessage(content="输出纯JSON，不要加任何前缀说明。"),
            HumanMessage(content=MATCH_PROMPT.format(
                user_profile=profile_text,
                job_requirement=job_text,
                weights=json.dumps(weights, ensure_ascii=False),
            )),
        ])
        try:
            match_result = _parse_json(match_msg.content)
        except Exception:
            match_result = {"total_score": 0, "scores": {}, "summary": "匹配失败"}

        return {
            "job_id": job.get("id"),
            "job_title": job.get("job_title", ""),
            "company": job.get("company", ""),
            "industry": job.get("industry", ""),
            "city": job.get("city", ""),
            "salary_range": job.get("salary_range", ""),
            **match_result,
        }

    tasks = []
    for job in jobs:
        tasks.append(match_one(job))

    results = await asyncio.gather(*tasks)
    return {"match_results": list(results)}


async def rank_results(state: JobMatcherState) -> Dict:
    results = state.get("match_results", [])
    ranked = sorted(results, key=lambda r: r.get("total_score", 0), reverse=True)
    return {"ranked_results": ranked}


async def save_report(state: JobMatcherState) -> Dict:
    uid = state["user_id"]
    ranked = state.get("ranked_results", [])

    for r in ranked[:5]:  # Top 5
        await db_utils.save_match_report(
            user_id=uid,
            job_name=r.get("job_title", ""),
            match_score=float(r.get("total_score", 0)),
            report_data=r,
            industry=r.get("industry", ""),
            city=r.get("city", ""),
        )

    return {"report_id": 0}


async def self_reflect(state: JobMatcherState) -> Dict:
    results = state.get("ranked_results", [])
    if not results:
        return {}
    llm = get_llm(temperature=0.1)
    prompt = SELF_REFLECT_PROMPT.format(output=json.dumps(results, ensure_ascii=False))
    msg = llm.invoke([HumanMessage(content=prompt)])
    try:
        refined = _parse_json(msg.content)
        return {"ranked_results": refined if isinstance(refined, list) else results}
    except Exception:
        return {}


def _parse_json(content: str) -> dict:
    c = content.strip()
    for marker in ("```json", "```"):
        if marker in c:
            c = c.split(marker)[1].split("```")[0]
            break
    return json.loads(c)
