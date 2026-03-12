import httpx
import json
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import time

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse
from pathlib import Path

from .config import settings
from .models import QueryRequest, QueryResponse, ChatRequest
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
# Helpers
# --------------------------------------------------------------------------

def build_context_prompt(user_message: str, rag_results: list) -> str:
    """
    Builds a context-aware prompt by injecting the retrieved documents
    into the LLM's system instructions so it can ground its response.
    """
    context_blocks = []
    for i, result in enumerate(rag_results, 1):
        sources = "; ".join(
            f"{s.libguide_title} → {s.section_title} ({s.url})"
            for s in result.sources
        )
        context_blocks.append(
            f"[Document {i}]\n{result.text}\nSources: {sources}"
        )

    context_str = "\n\n".join(context_blocks)

    return (
        "You are a knowledgeable librarian at an academic research library. "
        "Using the library documents provided below, write one concise and informative paragraph "
        "that directly addresses the user's query. Suggest reliable strategies or places to find "
        "more information, such as library databases, archives, or catalogs. "
        "Focus on peer-reviewed and library materials. Do not make up specific book titles or "
        "sources — only refer to general or commonly known resources, or give search strategies. "
        "Keep everything in brief paragraph style.\n\n"
        f"=== Library Documents ===\n{context_str}\n\n"
        f"=== User Query ===\n{user_message}"
    )


async def stream_ollama(prompt: str) -> AsyncGenerator[str, None]:
    """
    Streams the Ollama response token by token back to the browser.
    Each chunk is a plain text string as it arrives from the LLM.
    """
    async with httpx.AsyncClient(timeout=120.0) as client:
        async with client.stream(
            "POST",
            settings.ollama_url,
            json={"model": settings.ollama_model, "prompt": prompt, "stream": True},
        ) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line:
                    try:
                        chunk = json.loads(line)
                        token = chunk.get("response", "")
                        if token:
                            yield token
                        if chunk.get("done", False):
                            break
                    except json.JSONDecodeError:
                        continue


# --------------------------------------------------------------------------
# API Routes — defined BEFORE static mount so they aren't swallowed.
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


@app.post("/chat", tags=["Chat"])
async def chat(request: ChatRequest):
    """
    Full chat endpoint — retrieves relevant library documents, builds a
    context-aware prompt, and streams the LLM response back token by token.

    - **message**: the user's chat message
    - **top_k**: how many RAG results to retrieve (1–20, default 3)

    Returns a plain text stream. The browser receives tokens as they are
    generated rather than waiting for the full response.
    """

    t0 = time.perf_counter()

    if retriever is None:
        raise HTTPException(status_code=503, detail="Retriever not initialized.")

    # --- 1. Retrieve relevant documents ---
    rag_results = retriever.search(query=request.message, top_k=request.top_k)

    t1 = time.perf_counter()
    print(f"[TIMING] Retrieval done: {t1 - t0:.3f}s")

    # --- 2. Build context-aware prompt ---
    prompt = build_context_prompt(request.message, rag_results)
    
    print(f"[TIMING] Prompt length (chars): {len(prompt)}, approx tokens: {len(prompt)//4}")

    # --- 3. Build the RAG sources block to send before the LLM stream ---
    # We send sources as a special JSON line first, then stream LLM tokens.
    # The browser uses a simple prefix convention to tell them apart:
    #   Lines starting with "SOURCES:" carry the JSON sources payload.
    #   All other lines are plain LLM text tokens.
    sources_payload = [
        {
            "score": r.score,
            "text": r.text,
            "sources": [s.model_dump() for s in r.sources],
        }
        for r in rag_results
    ]

    async def response_stream() -> AsyncGenerator[str, None]:
        # First yield the sources block so the frontend can render it immediately
        yield f"SOURCES:{json.dumps(sources_payload)}\n"
        first_token = True
        t_stream_start = time.perf_counter()
        # Then stream LLM tokens
        async for token in stream_ollama(prompt):
            if first_token:
                print(f"[TIMING] First token from LLM: {time.perf_counter() - t_stream_start:.3f}s")
                first_token = False
            yield token

    return StreamingResponse(response_stream(), media_type="text/plain")


# --------------------------------------------------------------------------
# Static files — mounted LAST so it doesn't swallow API routes.
# html=True makes StaticFiles automatically serve index.html for GET /
# --------------------------------------------------------------------------

app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")