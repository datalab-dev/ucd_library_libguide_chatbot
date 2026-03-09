# LibBot Package

A package for the semantic search chatbot for the UC Davis Library. LibBot lets users ask natural language questions and get back relevant resources from the library's LibGuides corpus, grounded by an LLM-generated summary.
Built with FastAPI, ChromaDB, Qwen3-Embedding, and Ollama. Accessible to anyone on the UC Davis Library VPN.

---

## Architecture

```
Browser (VPN required)
   ↕ 
FastAPI (libbot_pkg)           
   ├── serves frontend          (static/index.html)
   ├── POST /chat               → ChromaDB + Qwen embedding → retrieved docs
   │                            → Ollama LLM
   │                            → streamed response back to browser
   └── POST /search             → ChromaDB + Qwen embedding only (no LLM)
```

---

## Package Structure

```
libbot_pkg/
├── __init__.py          # public package API
├── __main__.py          # entry point: python -m libbot_pkg
├── config.py            # all settings, overridable via .env or env vars
├── models.py            # Pydantic request/response schemas
├── retriever.py         # ChromaDB connection + Qwen embedding + search logic
├── api.py               # FastAPI app: routes, Ollama streaming, static serving
└── static/
    ├── index.html       # chat UI
    ├── script.js        # handles streaming response, renders results
    ├── style.css        # light/dark mode styles
    └── assets/
        ├── logo-light.png
        └── logo-dark.png
```

---

## How It Works

1. User types a query in the browser and hits Send
2. `script.js` POSTs `{ message, top_k }` to `/chat`
3. FastAPI embeds the query using Qwen3-Embedding and searches ChromaDB
4. The top matching LibGuide documents are retrieved and deduplicated
5. A context-aware prompt (query + retrieved docs) is sent to Ollama
6. Ollama streams its response back through FastAPI to the browser
7. The browser renders the LLM summary, then displays the library sources below it


---

## Running the Server

### Prerequisites

Install pixi environment:
```bash
pixi install
```

Make sure Ollama is installed and the right model is pulled:
```bash
ollama pull <model>
```

### Start

Open two terminals on the server:

**Terminal 1 — start Ollama:**
```bash
pixi run ollama serve
```

**Terminal 2 — start LibBot:**
```bash
pixi run python -m libbot_pkg
```

---

## Accessing LibBot

Anyone on the **UC Davis Library VPN** can visit:
```
http://server-hostname:8075
```

---

## Testing Retrieval

A standalone test script is included to verify the package works independently of the web server:

```bash
pixi run python test_retriever.py "how do I cite a journal article?"
```

This checks the config, loads the retriever, runs a real query against ChromaDB, and prints the full structured response.

---

## Notes
- To swap Ollama for `llama.cpp` in the future, update `ollama_url` and `ollama_model` in `config.py` and adjust the request format in `stream_ollama()` in `api.py`.
