from functools import lru_cache
from langchain_openai import OpenAIEmbeddings
from app.config import settings


@lru_cache(maxsize=1)
def get_embeddings():
    """Returns a cached embeddings instance.

    Priority:
    1. EMBEDDING_API_KEY is set → use separate embedding API (e.g. DashScope)
    2. EMBEDDING_MODEL looks like HuggingFace model (contains '/') → local BGE
    3. Otherwise → reuse LLM API (OpenAI-compatible)
    """
    if settings.DASHSCOPE_API_KEY:
        return OpenAIEmbeddings(
            model=settings.EMBEDDING_MODEL,
            api_key=settings.DASHSCOPE_API_KEY,
            base_url=settings.EMBEDDING_BASE_URL,
        )

    if "/" in settings.EMBEDDING_MODEL:
        from langchain_community.embeddings import HuggingFaceBgeEmbeddings
        return HuggingFaceBgeEmbeddings(
            model_name=settings.EMBEDDING_MODEL,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )

    return OpenAIEmbeddings(
        model=settings.EMBEDDING_MODEL,
        api_key=settings.OPENAI_API_KEY,
        base_url=settings.OPENAI_BASE_URL,
    )
