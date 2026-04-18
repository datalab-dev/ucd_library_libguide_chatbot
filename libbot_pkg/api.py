import httpx
import json
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import time
import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse
from pathlib import Path

from .config import settings
from .models import QueryRequest, QueryResponse, ChatRequest
from .retriever import Retriever



logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("libbot")

# --------------------------------------------------------------------------
# Lifespan: load the retriever once at startup, clean up on shutdown.
# --------------------------------------------------------------------------

retriever: Retriever | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global retriever
    
    # initialize RAG retriever
    retriever = Retriever()

    # Preload/Warm-up the LLM
    print(f"Preloading model: {settings.ollama_model}...")
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            # Sending an empty prompt to Ollama triggers the load into RAM
            await client.post(
                settings.ollama_url,
                json={"model": settings.ollama_model, "prompt": "", "keep_alive": -1}
            )
        print("Model preloaded successfully.")
    except Exception as e:
        print(f"Warning: Model preloading failed: {e}")
        
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

def build_context_prompt(user_message: str, rag_results: list, history: list) -> str:
    """
    Builds a context-rich prompt for the LLM by combining:
    - The current user message
    - The retrieved RAG results (merged into a single text blob)
    - A memory block of previous conversation turns (if any)
    """

    # Merge retrieved doc texts into a single blob
    doc_blob = "\n\n".join(r.text for r in rag_results)

    # Build memory block: always turn 1, plus up to 2 most recent turns
    # (excluding turn 1 to avoid duplication)
    memory_turns = []
    if history:
        memory_turns.append(history[0])           # always anchor turn 1
        recent = history[1:][-2:]                 # last 2 of the rest
        memory_turns.extend(recent)

    memory_block = ""
    if memory_turns:
        pairs = []
        for turn in memory_turns:
            pairs.append(f"User: {turn.prompt}\nAssistant: {turn.response}")
        memory_block = (
            "=== Previous Conversation ===\n"
            + "\n\n".join(pairs)
            + "\n\n"
        )


    return (
        f"{memory_block}"
        f"=== Library Documents ===\n{doc_blob}\n\n"
        f"=== Current User Query ===\n{user_message}"
    )


async def stream_ollama(prompt: str) -> AsyncGenerator[str, None]:
    """
    Streams the Ollama response token by token back to the browser.
    Each chunk is a plain text string as it arrives from the LLM.
    """
    timeout = httpx.Timeout(connect=10.0, read=300.0, write=10.0, pool=10.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
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

    # --- Server-side logging (scores/text never sent to frontend) ---
    logger.info(f"Query: {request.message!r}")
    logger.info(f"Retrieval time: {t1 - t0:.3f}s | Results: {len(rag_results)}")
    for i, r in enumerate(rag_results, 1):
        logger.info(f"  [{i}] score={r.score:.4f} | preview={r.text[:80]!r}")
        for s in r.sources:
            logger.info(f"       {s.libguide_title} → {s.section_title} | {s.url}")

    # --- 2. Build context-aware prompt ---
    prompt = build_context_prompt(request.message, rag_results, request.history)
    logger.info(f"Prompt length (chars): {len(prompt)} | approx tokens: {len(prompt)//4}")
    
    # --- 3. Sources payload — titles and URLs only, scores/text stripped ---
    sources_payload = [
        {
            "text": r.text,
            "sources": [s.model_dump() for s in r.sources]
        }
        for r in rag_results
    ]

    async def response_stream() -> AsyncGenerator[str, None]:
        yield f"SOURCES:{json.dumps(sources_payload)}\n"
        first_token = True
        t_stream_start = time.perf_counter()
        async for token in stream_ollama(prompt):
            if first_token:
                logger.info(f"First token from LLM: {time.perf_counter() - t_stream_start:.3f}s")
                first_token = False
            yield token

    return StreamingResponse(response_stream(), media_type="text/plain")

# --------------------------------------------------------------------------
# Static files — mounted LAST so it doesn't swallow API routes.
# html=True makes StaticFiles automatically serve index.html for GET /
# --------------------------------------------------------------------------

app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")