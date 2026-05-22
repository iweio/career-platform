"""Three retrievers for the RAG system:
1. JobRetriever — semantic job search
2. ResumeJobMatcher — resume-to-job vector + LLM hybrid matching
3. LearningRetriever — learning resource search
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from app.rag.vector_store import get_job_collection, get_learning_collection, get_resume_collection


@dataclass
class JobResult:
    id: str
    job_title: str
    company: str
    industry: str
    city: str
    salary_range: str
    score: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ResourceResult:
    id: str
    title: str
    category: str
    level: str
    duration: str
    source: str
    score: float


class JobRetriever:
    """Semantic job search — finds matching categories via vector, then loads jobs from MySQL."""

    async def search(
        self,
        query: str,
        top_k: int = 10,
        industry: str = None,
        city: str = None,
    ) -> List[JobResult]:
        from sqlalchemy import select
        from app.db.mysql import AsyncSessionLocal
        from app.models.job import Job

        collection = get_job_collection()
        results = collection.query(query_texts=[query], n_results=top_k)

        category_scores = {}  # category_id -> score
        if results["ids"] and results["ids"][0]:
            for i, doc_id in enumerate(results["ids"][0]):
                dist = results["distances"][0][i] if results["distances"] else 0
                category_scores[int(doc_id)] = max(0.0, 1.0 - dist)

        if not category_scores:
            return []

        async with AsyncSessionLocal() as db:
            stmt = select(Job).where(Job.category_id.in_(category_scores.keys()))
            if industry:
                stmt = stmt.where(Job.industry == industry)
            if city:
                stmt = stmt.where(Job.city == city)
            result = await db.execute(stmt)
            jobs = result.scalars().all()

        out = []
        for j in jobs:
            score = category_scores.get(j.category_id, 0)
            out.append(JobResult(
                id=str(j.id),
                job_title=j.job_title,
                company=j.company,
                industry=j.industry or "",
                city=j.city or "",
                salary_range=j.salary_range or "",
                score=round(score, 4),
            ))

        return sorted(out, key=lambda r: r.score, reverse=True)


class ResumeJobMatcher:
    """Resume-to-job hybrid matching.

    Phase 1: Vector retrieval to get top-N candidate jobs.
    Phase 2: LLM-based 7-dimension scoring for each candidate.
    """

    def retrieve_candidates(self, resume_text: str, top_k: int = 20) -> list[str]:
        """Vector-only first pass: get top-k candidate job IDs."""
        collection = get_job_collection()
        results = collection.query(query_texts=[resume_text], n_results=top_k)
        if results["ids"] and results["ids"][0]:
            return results["ids"][0]
        return []

class LearningRetriever:
    """Learning resource search for the learning plan agent.

    Given a target job and skill gaps, finds relevant courses,
    tutorials, and documentation to recommend.
    """

    def search(self, target_job: str, skill_gaps: list[str], top_k: int = 5) -> List[ResourceResult]:
        collection = get_learning_collection()

        query = f"{target_job} {' '.join(skill_gaps)}"
        results = collection.query(query_texts=[query], n_results=top_k)

        resources = []
        if results["ids"] and results["ids"][0]:
            for i, doc_id in enumerate(results["ids"][0]):
                meta = results["metadatas"][0][i] if results["metadatas"] else {}
                dist = results["distances"][0][i] if results["distances"] else 0
                score = max(0.0, 1.0 - dist)

                resources.append(ResourceResult(
                    id=doc_id,
                    title=meta.get("title", ""),
                    category=meta.get("category", ""),
                    level=meta.get("level", ""),
                    duration=meta.get("duration", ""),
                    source=meta.get("source", ""),
                    score=round(score, 4),
                ))

        return sorted(resources, key=lambda r: r.score, reverse=True)


class ResumeRetriever:
    """Resume vector storage and semantic search.

    Stores user profile embeddings for persistent reuse:
    - After resume analysis, store the profile vector
    - Matching can load stored vector instead of re-embedding
    - Enables semantic search across all user profiles
    """

    def store(self, user_id: int, profile_text: str, metadata: dict | None = None) -> bool:
        """Upsert a user's profile embedding into ChromaDB."""
        collection = get_resume_collection()
        doc_id = str(user_id)
        meta = metadata or {}
        meta["user_id"] = user_id

        # Remove existing entry if present
        existing = collection.get(ids=[doc_id])
        if existing and existing["ids"]:
            collection.delete(ids=[doc_id])

        collection.add(
            ids=[doc_id],
            documents=[profile_text],
            metadatas=[meta],
        )
        return True

    def get_vector(self, user_id: int) -> str | None:
        """Get a stored resume document for a user, or None."""
        collection = get_resume_collection()
        results = collection.get(ids=[str(user_id)])
        if results and results["ids"] and results["documents"]:
            return results["documents"][0]
        return None

# Singleton instances
job_retriever = JobRetriever()
resume_job_matcher = ResumeJobMatcher()
learning_retriever = LearningRetriever()
resume_retriever = ResumeRetriever()
