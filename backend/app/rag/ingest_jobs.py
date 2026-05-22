"""Ingest job categories into ChromaDB vector store.

Called at system startup (FastAPI lifespan) to keep vector index in sync.
Now indexes 10 big job categories (岗位族) instead of individual job postings.
"""
from sqlalchemy import select
from app.db.mysql import AsyncSessionLocal
from app.models.job_category import JobCategory
from app.rag.vector_store import get_job_collection


async def ingest_all_jobs():
    """Read all job categories from MySQL and upsert into ChromaDB (DashScope-embedded)."""
    collection = get_job_collection()

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(JobCategory))
        categories = result.scalars().all()

    if not categories:
        print("[RAG] No job categories found — skipping ingest.")
        return

    ids = [str(c.id) for c in categories]
    documents = []
    metadatas = []

    for c in categories:
        documents.append(c.description or c.name)
        metadatas.append({
            "name": c.name or "",
            "tag": c.tag or "",
            "scarcity": c.insight_scarcity or "",
        })

    # DashScope batch limit: 10 per request
    BATCH = 10
    for i in range(0, len(ids), BATCH):
        collection.upsert(
            ids=ids[i:i + BATCH],
            documents=documents[i:i + BATCH],
            metadatas=metadatas[i:i + BATCH],
        )

    print(f"[RAG] Ingested {len(categories)} job categories into ChromaDB (DashScope).")
