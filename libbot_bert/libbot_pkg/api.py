import httpx
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from .config import settings
from .models import QueryRequest, QueryResponse, ChatRequest, ChatResponse
from .retriever import Retriever

# --------------------------------------------------------------------------
# Lifespan: load the retriever once at startup, clean up on shutdown.
# --------------------------------------------------------------------------

retriever: Retriever | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global retriever
    retriever = Retriever()
    yield
    retriever = None


# --------------------------------------------------------------------------
# App
# --------------------------------------------------------------------------

app = FastAPI(
    title="LibBot",
    description="Semantic search over LibGuides using Qwen3-Embedding.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

STATIC_DIR = Path(__file__).parent / "static"


# --------------------------------------------------------------------------
# API Routes — must be defined BEFORE the static mount below,
# otherwise StaticFiles will intercept everything first.
# --------------------------------------------------------------------------

@app.get("/health", tags=["Meta"])
def health():
    """Simple liveness check."""
    return {"status": "ok"}


@app.post("/search", response_model=QueryResponse, tags=["Search"])
def search(request: QueryRequest):
    """
    Raw semantic search — returns ranked RAG results with no LLM involvement.

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


@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
def chat(request: ChatRequest):
    """
    Full chat endpoint — calls the LLM for a summary and the retriever for
    library resources, then returns both as structured JSON.

    - **message**: the user's chat message
    - **top_k**: how many RAG results to retrieve (1–20, default 3)
    """
    if retriever is None:
        raise HTTPException(status_code=503, detail="Retriever not initialized.")

    # --- 1. Call Ollama for LLM summary ---
    summary_prompt = (
        "Act as the user's librarian at an academic research library. "
        "Please summarize the user's query in one concise and informative paragraph. "
        "Briefly explain the topic the user is asking about, and then suggest reliable "
        "strategies or places to find more information, such as library databases, archives, "
        "or catalogs. Focus your answer on peer-reviewed and library materials; do not make up "
        "specific book titles or sources — only refer to general or commonly known resources, "
        "or give search strategies. If you cannot find resources/information for a specific "
        "prompt, it is okay to mention that. Keep everything in brief paragraph style.\n\n"
        f"{request.message}"
    )

    try:
        ollama_response = httpx.post(
            settings.ollama_url,
            json={"model": settings.ollama_model, "prompt": summary_prompt, "stream": False},
            timeout=120.0,
        )
        ollama_response.raise_for_status()
        llm_reply = ollama_response.json().get("response", "").strip()
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"Ollama error: {e}")

    # --- 2. Run RAG retrieval ---
    rag_results = retriever.search(query=request.message, top_k=request.top_k)

    return ChatResponse(
        message=request.message,
        llm_reply=llm_reply,
        rag_results=rag_results,
    )


# --------------------------------------------------------------------------
# Static files — mounted LAST so it doesn't swallow API routes.
# html=True makes StaticFiles automatically serve index.html for GET /
# --------------------------------------------------------------------------

app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")