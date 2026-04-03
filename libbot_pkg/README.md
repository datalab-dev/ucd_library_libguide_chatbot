# LibBot Package

A package for the semantic search chatbot for the UC Davis Library. LibBot lets users ask natural language questions and get back relevant resources from the library's LibGuides corpus, grounded by an LLM-generated summary. Built with FastAPI, ChromaDB, Qwen3-Embedding, and Ollama.

---

> [!TIP]
> **Accessing and Interacting with LibBot:**
> 1. Connect to the **UC Davis Library VPN**
> 2. Go to http://datasci.library.ucdavis.edu:8075

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

> [!NOTE]
> ## How It Works
> 1. User types a query in the browser and hits Send
> 2. `script.js` POSTs `{ message, top_k }` to `/chat`
> 3. FastAPI embeds the query using Qwen3-Embedding and searches ChromaDB
> 4. The top matching LibGuide documents are retrieved and deduplicated
> 5. A context-aware prompt (query + retrieved docs) is sent to Ollama
> 6. Ollama streams its response back through FastAPI to the browser
> 7. The browser renders the LLM summary, then displays the library sources below it

---

## Testing Retrieval

A standalone test script is included to verify the package works independently of the web server (can replace the example query with any query):

```bash
pixi run python test_retriever.py "how do I cite a journal article?"
```

This checks the config, loads the retriever, runs a real query against ChromaDB, and prints the full structured response.


