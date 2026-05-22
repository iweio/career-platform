from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select, delete
from app.db.mysql import get_db
from app.middleware.auth import get_current_user
from app.models.favorite import Favorite
from app.models.job import Job

router = APIRouter()


class FavoriteRequest(BaseModel):
    job_id: int


@router.get("")
async def list_favorites(user: dict = Depends(get_current_user), db=Depends(get_db)):
    result = await db.execute(
        select(Favorite, Job.job_title, Job.company, Job.industry, Job.city, Job.salary_range)
        .join(Job, Favorite.job_id == Job.id)
        .where(Favorite.user_id == user["user_id"])
        .order_by(Favorite.created_at.desc())
    )
    favorites = []
    for fav, title, company, industry, city, salary in result:
        favorites.append({
            "id": fav.id, "job_id": fav.job_id, "job_title": title,
            "company": company, "industry": industry, "city": city,
            "salary_range": salary, "created_at": str(fav.created_at),
        })
    return {"success": True, "data": favorites}


@router.post("")
async def add_favorite(req: FavoriteRequest, user: dict = Depends(get_current_user), db=Depends(get_db)):
    try:
        db.add(Favorite(user_id=user["user_id"], job_id=req.job_id))
        await db.commit()
    except Exception:
        raise HTTPException(400, "Already favorited or job not found")
    return {"success": True}


@router.delete("/{job_id}")
async def remove_favorite(job_id: int, user: dict = Depends(get_current_user), db=Depends(get_db)):
    await db.execute(
        delete(Favorite).where(Favorite.user_id == user["user_id"], Favorite.job_id == job_id)
    )
    await db.commit()
    return {"success": True}
