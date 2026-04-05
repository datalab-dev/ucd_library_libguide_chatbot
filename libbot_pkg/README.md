# LibBot Package

LibBot is a semantic search chatbot for the UC Davis Library. Users ask natural language questions and get back relevant resources from the LibGuides corpus, grounded by an LLM-generated summary. This README covers the package internals and how the system works.

> [!NOTE]
> For end-user access instructions, see the [main README](https://github.com/datalab-dev/2025_startup_libguide_chatbot/tree/libbot).
> For configuration, API reference, and server operation, see the [Maintenance Guide](https://github.com/datalab-dev/2025_startup_libguide_chatbot/blob/libbot/docs/maintenance.md).

<br>

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

<br>

---

## Architecture

```
Browser (VPN required)
   ↕  (port 8075)
FastAPI (libbot_pkg)           
   ├── serves frontend          (static/index.html)
   ├── POST /chat               → ChromaDB + Qwen embedding → retrieved docs
   │                            → Ollama LLM
   │                            → streamed response back to browser
   └── POST /search             → ChromaDB + Qwen embedding only (no LLM)
```

<br>

---

## How It Works
1. User types a query in the browser and hits Send
2. `script.js` POSTs `{ message, top_k }` to `/chat`
3. FastAPI embeds the query using Qwen3-Embedding and searches ChromaDB
4. The top matching LibGuide documents are retrieved and deduplicated
5. A context-aware prompt (query + retrieved docs) is sent to Ollama
6. Ollama streams its response back through FastAPI to the browser
7. The browser renders the LLM summary, then displays the library sources below it

<br>

---

## Testing Retrieval

A standalone test script verifies the package works independently of the web server:

```bash
pixi run python test_retriever.py "how do I cite a journal article?"
```

This checks the config, loads the retriever, runs a real query against ChromaDB, and prints the full structured response. Replace the example query with anything you want to test.

---

For server startup, configuration, and API reference, see the [Maintenance Guide](https://github.com/datalab-dev/2025_startup_libguide_chatbot/blob/libbot/docs/maintenance.md).
