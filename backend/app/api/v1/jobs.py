from fastapi import APIRouter, Query, Depends
from sqlalchemy import select
from app.db.mysql import get_db
from app.models.job import Job
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
        results = job_retriever.search(keyword, top_k=page_size, industry=industry or None, city=city or None)
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

    # total count
    from sqlalchemy import func
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
    results = job_retriever.search(q, top_k=top_k)
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
