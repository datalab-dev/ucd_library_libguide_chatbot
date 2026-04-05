# LibBot: UC Davis LibGuide RAG Chatbot

> [!IMPORTANT]  
> This project originated as a group collaboration back during 2025 Spring Quarter. The original team prototype was primarily built in R, along with Ollama; team member acknowledgements, resources and data store, and documentation can be found in the [[**STS195-legacy-group-original**]](https://github.com/datalab-dev/2025_startup_libguide_chatbot/tree/STS195-legacy-group-original) branch of the LibBot repo.

> [!NOTE]
> LibBot's corpus is based on UC Davis LibGuides scraped February 20th, 2025.
> Updated library data will be incorporated in future iterations.

## Current Contributors

-   **Project Lead**: Dr. Carl Stahmer
-   **Lead Developer & Maintainer**: Federico Aprile

<br>

---

## Project Overview

**LibBot** is a virtual librarian chatbot designed to bring together scattered academic resources into a unified research tool. Developed to support the UC Davis Library, it connects researchers with relevant materials and expertise, maintaining high-quality research support even amidst institutional constraints like reduced librarian availability. _**LibBot is currently deployed on the UC Davis DataLab server and accessible to users on the university VPN.**_

### Technical Implementation

The system transforms the UC Davis library’s corpus of guides and resources into a conversational experience through a structured RAG (Retrieval-Augmented Generation) pipeline:

- **Data Ingestion & Cleaning**: Systematized scraping and preprocessing of heterogeneous library data to ensure a clean, searchable corpus.
- **Semantic Representation**: Uses Sentence-Transformer models to generate high-quality vector embeddings for documents and queries. These models were benchmarked to balance computational efficiency on CPU-only environments with retrieval accuracy.
- **Retrieval & Context Selection**: A Python/PyTorch-based retrieval engine that uses optimized pooling strategies to identify and rank the most relevant document chunks based on user queries, using cosine similarity.
- **Retrieval-Augmented Generation (RAG)**: A prompt engineering layer that synthesizes the retrieved context and passes it to a Large Language Model (LLM) to generate natural, cited responses and links.

<br>

---

## Getting Started with LibBot

> [!TIP]
> **Accessing and Interacting with LibBot:**
> 1. Connect to the **UC Davis Library VPN**
> 2. Go to http://datasci.library.ucdavis.edu:8075

> [!NOTE]
> If the page doesn't load, verify you are connected to the UC Davis Library VPN.

> [!NOTE]
> As with all large language model output, use your own critical reading and thinking skills to assess the validity and reliability of this response for your specific query.

> [!NOTE]
> - For maintainers needing to start or restart the server, see the [libbot_pkg README](https://github.com/datalab-dev/2025_startup_libguide_chatbot/tree/libbot/libbot_pkg).
> - To verify the package is working independently of the web server, run:
> ``` bash
> pixi run python test_retriever.py "your query here"
> ```

<br>

---
## Project Dependencies
This project uses Pixi for environment and dependency management on a Linux x86-64 server running Python 3.10. Pixi handles Python versioning, package installation, and task running — no manual pip install or conda environment setup needed. The full dependency list is defined in pixi.toml.

| Package | Purpose |
|--------|-------------|
| fastapi / uvicorn | REST API server and ASGI runtime |
| chromadb | Vector database for storing and querying embeddings |
| sentence-transformers / pytorch | Qwen3-Embedding model for query and document encoding |
| pydantic-settings | Request/response validation and .env-based configuration |
| httpx | Async HTTP client for communicating with Ollama |
| ollama | LLM inference (runs as a separate process — see Maintenance Guide) |

### For full environment setup and server operation, see the Maintenance Guide.

<br>

---

## GitHub File and Directory Structure

``` bash
2025_startup_libguide_chatbot/
  ├── README.md                          # This README
  ├── libbot_pkg/                        # Main package - see dedicated README
  │   ├── ...
  ├── test_retriever.py                  # Testing whether libbot_pkg module imports work on a simple script
  ├── .gitignore/.gitattributes          # What files Git should not track, and how Git should handle the files it does track
  ├── pixi.toml                          # Environment and dependency definitions
  └── research/                          # Model benchmarking — see dedicated README
      ├── ...
```
[**Dedicated libbot_pkg/ README**](https://github.com/datalab-dev/2025_startup_libguide_chatbot/tree/libbot/libbot_pkg)

[**Dedicated research/ README**](https://github.com/datalab-dev/2025_startup_libguide_chatbot/tree/libbot/research)

<br>

---
> [!WARNING]
> UNDER CONSTRUCTION
### Methodology
- A link to the docs/methodology.md once written
- how the corpus was built, how embeddings were generated, why you chose cosine similarity + deduplication.
---
> [!WARNING]
> UNDER CONSTRUCTION
### Examples of Work:
- 3-5 examples with a screenshot each, not exhaustive test logs, just the best ones.
