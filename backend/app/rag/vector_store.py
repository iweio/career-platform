from typing import Optional as _Optional
import chromadb
from chromadb.config import Settings as ChromaSettings
from app.config import settings
from app.rag.embedding import get_embedding_function

_client: _Optional[chromadb.PersistentClient] = None


def get_chroma_client() -> _Optional[chromadb.PersistentClient]:
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(
            path=settings.CHROMA_PERSIST_DIR,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
    return _client


def _build_collection(name: str):
    """Get or create a collection with DashScope embedding (1024-d, cosine)."""
    return get_chroma_client().get_or_create_collection(
        name=name,
        embedding_function=get_embedding_function(),
        metadata={"hnsw:space": "cosine"},
    )


def get_job_collection():
    return _build_collection(settings.CHROMA_COLLECTION_JOBS)


def get_learning_collection():
    return _build_collection(settings.CHROMA_COLLECTION_LEARNING)


def get_resume_collection():
    return _build_collection(settings.CHROMA_COLLECTION_RESUMES)


def reset_collections():
    """Drop and recreate all collections. Use with caution."""
    client = get_chroma_client()
    for name in [
        settings.CHROMA_COLLECTION_JOBS,
        settings.CHROMA_COLLECTION_LEARNING,
        settings.CHROMA_COLLECTION_RESUMES,
    ]:
        try:
            client.delete_collection(name)
        except Exception:
            pass
    # Clear the embedding function cache so it gets recreated fresh
    from app.rag.embedding import get_embedding_function as _gef
    _gef.cache_clear()
    global _client
    _client = None
