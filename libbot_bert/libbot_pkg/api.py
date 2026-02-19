from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .models import QueryRequest, QueryResponse
from .retriever import Retriever



# Followed a Medium tutorial to set this up, and got a lot of help from Claude


# --------------------------------------------------------------------------
# Lifespan: load the retriever once at startup, clean up on shutdown.
# This is FastAPI's recommended way to manage shared resources.
# --------------------------------------------------------------------------

retriever: Retriever | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global retriever
    retriever = Retriever()  # loads ChromaDB + model — runs once
    yield
    # anything after yield runs on shutdown (nothing to clean up here)
    retriever = None


# --------------------------------------------------------------------------
# App
# --------------------------------------------------------------------------

app = FastAPI(
    title="LibBot RAG Retriever",
    description="Semantic search over LibGuides using Qwen3-Embedding.",
    version="0.1.0",
    lifespan=lifespan,
)

# --------------------------------------------------------------------------
# CORS — allows your web frontend to call this API from the browser.
# In production, replace allow_origins=["*"] with your actual frontend URL,
# e.g. allow_origins=["https://libbot.yourdomain.edu"]
# --------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


# --------------------------------------------------------------------------
# Routes
# --------------------------------------------------------------------------

@app.get("/health", tags=["Meta"])
def health():
    """Simple liveness check — returns ok if the server is running."""
    return {"status": "ok"}


@app.post("/search", response_model=QueryResponse, tags=["Search"])
def search(request: QueryRequest):
    """
    Perform semantic search over the LibGuides corpus.

    - **query**: the user's natural language question
    - **top_k**: how many unique results to return (1–20, default 3)
    """
    if retriever is None:
        raise HTTPException(status_code=503, detail="Retriever not initialized.")

    results = retriever.search(query=request.query, top_k=request.top_k)

    return QueryResponse(
        query=request.query,
        top_k=request.top_k,
        results=results,
    )