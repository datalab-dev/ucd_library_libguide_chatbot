# Expansion of LibBot: Library Guide RAG Project

> [!IMPORTANT]  
> - This project originated as a group collaboration back during 2025 Spring Quarter. The original team version (mainly built in R), team member agknowledgements, resources and data store, and documentation can be found in the $\color{Purple}\large{\textsf{STS195-legacy-group-original}}$ branch.
> - LibBot currently works with libguides based on a final scrape conducted on February 20th, 2025. The additional library data that has been updated since then will be incorporated in the next iterations of LibBot.

## Current Contributors

-   **Project Lead**: DataLab Director Dr. Carl Stahmer
-   **Lead Developer & Mantainer**: Federico Aprile

---

## Project Overview:

**LibBot** is a virtual librarian chatbot designed to unify scattered academic resources into a singular research ecosystem. Developed to support the UC Davis Library, it connects researchers with relevant materials and expertise, maintaining high-quality research support even amidst institutional constraints like reduced librarian availability.

### Technical Implementation

The system transforms the UC Davis library’s corpus of guides and resources into a conversational experience through a structured RAG (Retrieval-Augmented Generation) pipeline:

- **Data Ingestion & Cleaning**: Systematized scraping and preprocessing of heterogeneous library data to ensure a clean, searchable corpus.
- **Semantic Representation**: Utilization of Sentence-Transformer models to generate high-quality vector embeddings for documents and queries. These models were benchmarked to balance computational efficiency on CPU-only environments with retrieval accuracy.
- **Retrieval & Context Selection**: A Python/PyTorch-based retrieval engine that uses optimized pooling strategies to identify and rank the most relevant document chunks based on user queries, using cosine similarity.
- **Retrieval-Augmented Generation (RAG)**: A prompt engineering layer that synthesizes the retrieved context and passes it to a Large Language Model (LLM) to generate natural, cited responses and links.

### Current Capabilities & Roadmap

LibBot currently retrieves resources based on natural language queries and provides direct citations to library materials. Development is currently focused on:
- **Synthesis & Accessibility**: Enhancing the model's ability to summarize complex information for better user experience.
- **Deployment**: Transitioning to a server-based architecture for a fully deployable prototype.

---

## Getting Started with LibBot!


> [!TIP]  
> **If you wish to use and interact with LibBot:**
> 1. Connect to the UC Davis Library VPN
> 2. Go to http://server-hostname:8075 (replace temporary name with actual server name)

> [!NOTE]
> As with all large language model output, use your own critical reading and thinking skills to assess the validity and reliability of this response for your specific query.

<br>

------------------------------------------------------------------------

## Project Dependencies:

------------------------------------------------------------------------

## GitHub File and Directory Structure

The basic directory structure for the project is:

``` zsh
libbot Branch in 2025_startup_libguide_chatbot/
  ├── README.md                          # This README
  ├── libbot_pkg                         # Libbot package, with search/retrieval functionality, connection to vector database, and FastAPI for web server and interface
  │   ├── api.py
  │   ├── config.py
  │   ├── __init__.py
  │   ├── __main__.py
  │   ├── models.py
  │   ├── README.md
  │   ├── retriever.py
  │   └── static
  │       ├── assets
  │       │   ├── logo-dark.png
  │       │   └── logo-light.png
  │       ├── favicon.io
  │       ├── index.html
  │       ├── script.js
  │       └── style.css
  ├── test_retriever.py                  # Testing whether libbot_pkg module imports work on a simple script
  ├── .gitignore/.gitattributes          # What files Git should not track, and how Git should handle the files it does track
  ├── pixi.toml                          # Environment and dependency definitions
  └── research/                          # Benchmarking various embedding models, retrieval methods, visualizations, and database structures.
      ├── ...
```

### research/ Contents

```         

└── research/           
    ├── bert_4layer_embedding_space.py
    ├── bert_4layer_search.py
    ├── bert_compared_search.py
    ├── bert_lastlayer_embedding_space.py
    ├── bert_lastlayer_search.py
    ├── bert_testing.py
    ├── chroma_db_creation.py
    ├── chroma_db_search.py
    ├── corpus_classification_test
    │   ├── classification_project.ipynb
    │   ├── confusion_matrix.png
    │   └── corpus_with_domains.csv
    ├── corpus_update.py
    ├── df_url_crawl.py
    ├── jina_embedding_space.py
    ├── jina_search.py
    ├── minilm_embedding_space.py
    ├── minilm_search.py
    ├── mxbai_embedding_space.py
    ├── mxbai_search.py
    ├── ollama_diagnosis.py
    ├── ollama_test.py
    ├── ollama_tokens.py
    ├── ollama_weights.py
    ├── prompts_embedding_space.py
    ├── qwen_4B_embedding_space.py
    ├── qwen_4B_search.py
    ├── qwen_embedding_space.py
    ├── qwen_search.py
    ├── README.md
    ├── requirements.txt
    ├── sbert_embedding_space.py
    ├── sbert_search.py
    ├── sql_url_crawl.py
    ├── text_cleaning.py
    └── threshold_vis.py

```
---

### LibBot

A semantic search chatbot for the UC Davis Library. LibBot lets users ask natural language questions and get back relevant resources from the library's LibGuides corpus, grounded by an LLM-generated summary. Built with FastAPI, ChromaDB, Qwen3-Embedding, and Ollama. Accessible to anyone on the UC Davis Library VPN. Newest iteration of LibBot, transitioned from the R-based prototype and Ollama structure, to Python and its transformers and transformer-adjacent libraries. 


