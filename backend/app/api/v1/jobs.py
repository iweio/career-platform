from fastapi import APIRouter, Query, Depends
from sqlalchemy import select, func
from app.db.mysql import get_db
from app.models.job import Job
from app.models.job_category import JobCategory
from app.models.matching import PromotionTransition
from app.rag.retrievers import job_retriever

router = APIRouter()


@router.get("")
async def list_jobs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, le=100),
    keyword: str = Query(""),
    industry: str = Query(""),
    city: str = Query(""),
    db=Depends(get_db),
):
    if keyword:
        results = await job_retriever.search(keyword, top_k=page_size, industry=industry or None, city=city or None)
        return {
            "success": True,
            "data": {
                "jobs": [
                    {"id": int(r.id), "job_title": r.job_title, "company": r.company,
                     "industry": r.industry, "city": r.city, "salary_range": r.salary_range,
                     "score": r.score}
                    for r in results
                ],
                "source": "vector",
            },
        }

    offset = (page - 1) * page_size
    base = select(Job)
    if industry:
        base = base.where(Job.industry == industry)
    if city:
        base = base.where(Job.city == city)

    count_result = await db.execute(select(func.count()).select_from(base.subquery()))
    total = count_result.scalar() or 0

    stmt = base.order_by(Job.publish_date.desc()).limit(page_size).offset(offset)
    result = await db.execute(stmt)
    jobs = []
    for j in result.scalars():
        jobs.append({
            "id": j.id,
            "job_title": j.job_title,
            "company": j.company,
            "industry": j.industry,
            "city": j.city,
            "salary_range": j.salary_range,
            "publish_date": str(j.publish_date) if j.publish_date else None,
        })
    return {"success": True, "data": {"jobs": jobs, "total": total, "page": page, "page_size": page_size, "source": "sql"}}


@router.get("/search")
async def search_jobs(q: str = Query(""), top_k: int = Query(10)):
    results = await job_retriever.search(q, top_k=top_k)
    return {
        "success": True,
        "data": {
            "results": [
                {"id": int(r.id), "job_title": r.job_title, "company": r.company,
                 "industry": r.industry, "city": r.city, "salary_range": r.salary_range,
                 "score": r.score}
                for r in results
            ],
        },
    }


@router.get("/hot")
async def hot_jobs(db=Depends(get_db)):
    result = await db.execute(
        select(Job).order_by(Job.publish_date.desc()).limit(10)
    )
    jobs = []
    for j in result.scalars():
        jobs.append({
            "id": j.id, "job_title": j.job_title, "company": j.company,
            "industry": j.industry, "city": j.city, "salary_range": j.salary_range,
        })
    return {"success": True, "data": jobs}


@router.get("/categories")
async def list_categories(db=Depends(get_db)):
    result = await db.execute(
        select(JobCategory).order_by(JobCategory.sort_order)
    )
    categories = []
    for c in result.scalars():
        categories.append({
            "id": c.id, "name": c.name, "icon": c.icon,
            "tag": c.tag, "scarcity": c.insight_scarcity,
            "description": c.description,
            "core_skills": c.core_skills,
            "promotion_path": c.promotion_path,
            "transition_to": c.transition_to,
        })
    return {"success": True, "data": categories}


@router.get("/hot-tags")
async def hot_tags(db=Depends(get_db)):
    result = await db.execute(
        select(Job.job_title).order_by(Job.publish_date.desc()).limit(6)
    )
    tags = [row[0] for row in result.all()]
    return {"success": True, "data": tags}


@router.get("/{job_id}/graph")
async def get_job_graph(job_id: int, db=Depends(get_db)):
    job_result = await db.execute(select(Job).where(Job.id == job_id))
    job = job_result.scalar_one_or_none()
    if not job:
        return {"success": False, "error": "Job not found"}

    trans_result = await db.execute(
        select(PromotionTransition).where(PromotionTransition.job_id == job_id)
    )
    transitions = trans_result.scalars().all()

    nodes = [{"id": f"job_{job.id}", "name": job.job_title, "label": "Job", "color": "#409EFF", "val": 25}]
    links = []

    seen_skills = set()
    for t in transitions:
        skills = t.required_skills or []
        for skill in skills:
            if skill not in seen_skills:
                seen_skills.add(skill)
                nodes.append({
                    "id": f"skill_{skill}", "name": skill, "label": "Skill",
                    "color": "#67C23A", "val": 16,
                })
            links.append({"source": f"job_{job.id}", "target": f"skill_{skill}"})

    return {"success": True, "data": {"nodes": nodes, "links": links}}


@router.get("/{job_id}/promotion")
async def get_job_promotion(job_id: int, db=Depends(get_db)):
    job_result = await db.execute(select(Job).where(Job.id == job_id))
    job = job_result.scalar_one_or_none()
    if not job:
        return {"success": False, "error": "Job not found"}

    trans_result = await db.execute(
        select(PromotionTransition).where(PromotionTransition.job_id == job_id)
    )
    transitions = trans_result.scalars().all()

    paths = []
    for t in transitions:
        paths.append({
            "from": t.current_role,
            "to": t.next_role,
            "skills": t.required_skills,
            "years": t.years_exp,
            "type": t.transition_type,
        })

    return {"success": True, "data": {"current_role": job.job_title, "paths": paths}}


@router.get("/{job_id}")
async def get_job_detail(job_id: int, db=Depends(get_db)):
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        return {"success": False, "error": "Job not found"}
    return {"success": True, "data": {
        "id": job.id, "job_title": job.job_title, "company": job.company,
        "industry": job.industry, "city": job.city, "salary_range": job.salary_range,
        "job_description": job.job_description, "requirements": job.requirements,
        "publish_date": str(job.publish_date) if job.publish_date else None,
    }}
