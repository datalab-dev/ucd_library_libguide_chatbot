"""
libbot_pkg
=============
A semantic search package over LibGuides using ChromaDB and Qwen3-Embedding,
served via a FastAPI REST API.

Usage
-----
Run the API server:
    python -m libbot_pkg

Use the retriever directly in Python:
    from libbot_pkg import Retriever
    r = Retriever()
    results = r.search("how do I cite a journal article?")
"""

from .retriever import Retriever
from .models import QueryRequest, QueryResponse, SearchResult, Source
from .config import settings

__all__ = [
    "Retriever",
    "QueryRequest",
    "QueryResponse",
    "SearchResult",
    "Source",
    "settings",
]