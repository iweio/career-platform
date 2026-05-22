"""Ingest all jobs from MySQL into ChromaDB vector store.

Called at system startup (FastAPI lifespan) to keep vector index in sync.
"""
from sqlalchemy import select
from app.db.mysql import AsyncSessionLocal
from app.models.job import Job
from app.rag.embedding import get_embeddings
from app.rag.vector_store import get_job_collection


async def ingest_all_jobs():
    """Read all jobs from MySQL and upsert into ChromaDB."""
    embeddings = get_embeddings()
    collection = get_job_collection()

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Job))
        jobs = result.scalars().all()

    if not jobs:
        return

    ids = [str(j.id) for j in jobs]
    documents = []
    metadatas = []

    for j in jobs:
        text_parts = [j.job_title or "", j.job_description or "", j.requirements or ""]
        documents.append("\n".join(text_parts))
        metadatas.append({
            "job_title": j.job_title or "",
            "company": j.company or "",
            "industry": j.industry or "",
            "city": j.city or "",
            "salary_range": j.salary_range or "",
        })

    collection.upsert(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
    )

    print(f"[RAG] Ingested {len(jobs)} jobs into ChromaDB.")


async def ingest_single_job(job_id: int, job_title: str, job_description: str,
                              requirements: str, **meta):
    """Add or update a single job in the vector index."""
    collection = get_job_collection()
    text = f"{job_title}\n{job_description}\n{requirements}"
    collection.upsert(
        ids=[str(job_id)],
        documents=[text],
        metadatas=[{k: v or "" for k, v in meta.items()}],
    )
