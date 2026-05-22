from functools import lru_cache

from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction

from app.config import settings


@lru_cache(maxsize=1)
def get_embedding_function() -> OpenAIEmbeddingFunction:
    """Returns a cached ChromaDB-compatible embedding function.

    Uses DashScope (阿里云百炼) OpenAI-compatible API — text-embedding-v3, 1024 dims.
    """
    return OpenAIEmbeddingFunction(
        api_key=settings.DASHSCOPE_API_KEY,
        api_base=settings.EMBEDDING_BASE_URL,
        model_name=settings.EMBEDDING_MODEL,
    )
