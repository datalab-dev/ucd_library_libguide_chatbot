# LibBot — Codebase Context for Pipeline Development

This document describes the full structure, data pipeline, schemas, and retriever logic of the LibBot project — a RAG chatbot for UC Davis Library Guides. It is written to brief a model session that will build new scraping, processing, and storage pipeline scripts.

**Project location**: `/Users/federicolupin/server_mount/ucd_library_libguide_chatbot/`
**Shared data directory**: `/Users/federicolupin/server_mount/data/`
**Corpus date**: LibGuides scraped February 2025 (7,442 text chunks from 204 guides)
**Deployed at**: `http://datasci.library.ucdavis.edu:8075` (UC Davis DataLab server, VPN required)

---

## 1. Directory Structure

```
server_mount/
├── data/                                   # Shared data (outside git repo)
│   ├── text_full_libguide.csv              # Original scraped corpus (7,442 rows)
│   ├── combined_text_full_libguide.csv     # Corpus + combined_text column
│   ├── combined_text_full_libguide.parquet # Same as above, parquet format (used for embeddings)
│   ├── url_list.csv                        # 204 LibGuide URLs (id, url)
│   ├── embeddings_qwen.npy                 # PRODUCTION embeddings: Qwen3-0.6B (7442 x 1024)
│   ├── embeddings_mxbai.npy               # Benchmark: mxbai-embed-large
│   ├── embeddings_sbert.npy               # Benchmark: Sentence-BERT MPNet
│   ├── embeddings_minilm.npy              # Benchmark: MiniLM L6
│   ├── embeddings_jina_code.npy           # Benchmark: Jina v3
│   ├── 4B_embeddings_qwen.npy             # Benchmark: Qwen3-Embedding-4B
│   ├── chroma_db/                          # ChromaDB persistent storage
│   │   └── chroma.sqlite3                  # (~34 MB)
│   ├── huggingface_cache/                  # Cached HuggingFace models
│   ├── ollama_cache/                       # Ollama model weights
│   └── nltk_data/                          # NLTK data (stopwords, tokenizers)
│
├── ucd_library_libguide_chatbot/           # Main project repo (git tracked)
│   ├── .env                                # Runtime configuration
│   ├── pixi.toml                           # Pixi environment + dependencies
│   ├── pixi.lock                           # Lockfile
│   ├── README.md
│   ├── test_retriever.py                   # Standalone retriever test script
│   │
│   ├── libbot_pkg/                         # Core application package
│   │   ├── __init__.py                     # Exports: Retriever, models, settings
│   │   ├── __main__.py                     # Entry point: `python -m libbot_pkg`
│   │   ├── config.py                       # Pydantic Settings (reads .env)
│   │   ├── models.py                       # Pydantic request/response schemas
│   │   ├── retriever.py                    # ChromaDB query + dedup + ranking
│   │   ├── api.py                          # FastAPI routes (/search, /chat, /health)
│   │   └── static/                         # Web UI
│   │       ├── index.html
│   │       ├── script.js
│   │       ├── style.css
│   │       ├── favicon.io
│   │       └── assets/                     # SVG logos (DataLab, LibBot)
│   │
│   ├── research/                           # Embedding model benchmarking & data prep
│   │   ├── corpus_update.py                # Creates combined_text column
│   │   ├── text_cleaning.py                # Normalizes unicode, whitespace, quotes
│   │   ├── chroma_db_creation.py           # Migrates embeddings + metadata → ChromaDB
│   │   ├── chroma_db_search.py             # Prototype retriever (before libbot_pkg)
│   │   ├── qwen_embedding_space.py         # Generates Qwen3-0.6B embeddings
│   │   ├── qwen_search.py                  # In-memory search using Qwen embeddings
│   │   ├── qwen_4B_embedding_space.py      # Qwen3-4B embedding generation
│   │   ├── qwen_4B_search.py              # Qwen3-4B search benchmark
│   │   ├── sbert_embedding_space.py        # Sentence-BERT embedding generation
│   │   ├── sbert_search.py                 # Sentence-BERT search benchmark
│   │   ├── mxbai_embedding_space.py        # mxbai-embed-large embeddings
│   │   ├── mxbai_search.py                 # mxbai search benchmark
│   │   ├── minilm_embedding_space.py       # MiniLM L6 embeddings
│   │   ├── minilm_search.py               # MiniLM search benchmark
│   │   ├── jina_embedding_space.py         # Jina v3 embeddings
│   │   ├── jina_search.py                 # Jina search benchmark
│   │   ├── bert_lastlayer_embedding_space.py  # BERT last-layer embeddings
│   │   ├── bert_lastlayer_search.py           # BERT last-layer search
│   │   ├── bert_4layer_embedding_space.py     # BERT last-4-layers embeddings
│   │   ├── bert_4layer_search.py              # BERT last-4-layers search
│   │   ├── bert_compared_search.py            # Side-by-side BERT variant comparison
│   │   ├── bert_testing.py                    # BERT diagnostic experiments
│   │   ├── prompts_embedding_space.py         # Test prompt embedding analysis
│   │   ├── threshold_vis.py                   # Similarity score decay visualization
│   │   ├── ollama_diagnosis.py                # Ollama vs SentenceTransformer comparison
│   │   ├── ollama_tokens.py                   # Ollama tokenization diagnostics
│   │   ├── ollama_weights.py                  # Ollama model weight inspection
│   │   ├── ollama_test.py                     # Ollama connectivity test
│   │   └── requirements.txt                   # Research-specific dependencies
│   │
│   ├── docs/
│   │   ├── methodology.md              # Embedding model research & selection rationale
│   │   ├── maintenance.md              # Server operation & deployment guide
│   │   └── ollama.md                   # LLM configuration notes
│   │
│   └── models/                         # Ollama Modelfiles (system prompts + params)
│       ├── Modelfile.gemma3n-4b-32     # Local: Gemma 3n 4B (32-ctx variant)
│       ├── Modelfile.gemma3-12b        # Local: Gemma 3 12B
│       ├── Modelfile.gemma4-cloud      # Cloud: Gemma 4 (via cloud Ollama)
│       └── Modelfile.gpt-oss-cloud     # Cloud: GPT-OSS (alternative)
```

---

## 2. Existing Scraping and Data Collection

**Original scraping was done in R** (branch `v1.0b-STS195`), not Python. The R functions scraped `https://guides.library.ucdavis.edu/` and extracted HTML content. Related git commits: `504a0ec`, `878a4a1`.

**No Python scraping scripts exist in the current codebase.** The CSV was produced by the R pipeline and then cleaned/enhanced in Python. The Python side only handles:

- **Text cleaning** (`research/text_cleaning.py`): Normalizes unicode (smart quotes → ASCII, em/en dashes → hyphens, non-breaking spaces → regular), standardizes line breaks, collapses whitespace. Applied to the `text` column of `text_full_libguide.csv`.

- **Corpus enhancement** (`research/corpus_update.py`): Creates the `combined_text` column by prepending guide/section titles to the text. Output: CSV and Parquet formats.

**There are no CSS selectors, HTML parsers, or web scraping libraries (requests, BeautifulSoup, Selenium) in the Python codebase.** A new scraping pipeline would be built from scratch.

**Known HTML structure of LibGuides** (from the existing data's implied structure):
- Each LibGuide has a title, a base URL, and multiple sub-pages
- Each sub-page contains sections (called "chunks" in the data) with titles
- Sections contain text content and optionally link to external resources
- LibGuides uses SpringShare's platform — look for `s-lib-box`, `s-lib-box-content` CSS classes

---

## 3. Data Schema

### Primary dataset: `text_full_libguide.csv`
**Rows**: 7,442 | **Columns**: 8

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `local_id` | int | Unique row identifier (1-indexed, sequential) | `1` |
| `parent_id` | int | Groups rows by LibGuide. All chunks from one guide share the same `parent_id`. Links to `id` in `url_list.csv`. | `2` |
| `text` | str | The actual content text of a section/resource | `"Black Studies Center brings together..."` |
| `libguide_title` | str | Title of the parent LibGuide | `"African and African American Studies"` |
| `libguide_url` | str | URL to the LibGuide's main page | `"https://guides.library.ucdavis.edu/african-and-african-american-studies"` |
| `chunk_title` | str | Section/heading name within the guide | `"Black Studies Center"` |
| `chunk_url` | str | URL to the specific section (often empty/NaN) | NaN or a URL |
| `external_url` | str | URL to an external resource described by the text | `"https://www.proquest.com/bsc"` |

### Enhanced dataset: `combined_text_full_libguide.parquet`
**Rows**: 7,442 | **Columns**: 9 (same 8 + `combined_text`)

| Column | Type | Description |
|--------|------|-------------|
| `combined_text` | str | Formatted field used for embedding generation |

Format of `combined_text`:
```
Guide Title: {libguide_title}
Section Title: {chunk_title}

{text}
```

Created by `corpus_update.py`:
```python
df["combined_text"] = (
    "Guide Title: " + df["libguide_title"].fillna("").astype(str) + "\n"
    "Section Title: " + df["chunk_title"].fillna("").astype(str) + "\n\n"
    + df["text"].fillna("").astype(str)
)
```

### URL reference: `url_list.csv`
**Rows**: 204 | **Columns**: 2

| Column | Type | Description |
|--------|------|-------------|
| `id` | int | Parent guide ID (= `parent_id` in main CSV) |
| `url` | str | LibGuide base URL |

---

## 4. ChromaDB Creation and Storage

**Script**: `research/chroma_db_creation.py`

### Data flow
```
embeddings_qwen.npy + combined_text_full_libguide.parquet
  → chroma_db_creation.py
    → data/chroma_db/
```

### Collection configuration
```python
client = chromadb.PersistentClient(path="/dsl/libbot/data/chroma_db")
collection = client.create_collection(
    name="libguides",
    metadata={"hnsw:space": "cosine"}
)
```

### Metadata fields stored per document

These are the exact fields stored in ChromaDB metadata (all strings, NaN → empty string):

| Field | Source column | Notes |
|-------|-------------|-------|
| `parent_id` | `parent_id` | Cast to `str(int(...))` |
| `text` | `text` | The raw content chunk |
| `libguide_title` | `libguide_title` | Guide name |
| `libguide_url` | `libguide_url` | Guide URL |
| `chunk_title` | `chunk_title` | Section name |
| `chunk_url` | `chunk_url` | Section URL (often empty) |
| `external_url` | `external_url` | External resource URL (often empty) |
| `combined_text` | `combined_text` | Titles + text (stored but NOT used by retriever at query time) |

### Document IDs
`str(int(row['local_id']))` — e.g., `"1"`, `"2"`, ..., `"7442"`

### Batch processing
- Batch size: 1,000 documents
- Total: 7,442 documents in ~8 batches
- Uses `collection.add(ids, embeddings, metadatas)`

### Storage location
- Default: `/dsl/libbot/data/chroma_db` (production server path)
- Local mount: `/Users/federicolupin/server_mount/data/chroma_db`
- Size: ~34 MB (SQLite + HNSW index)

---

## 5. Embedding Generation

**Script**: `research/qwen_embedding_space.py`

### Model
- **Name**: `Qwen/Qwen3-Embedding-0.6B`
- **Library**: `sentence-transformers` (`SentenceTransformer`)
- **Dimensions**: 1024
- **Normalization**: L2-normalized (`normalize_embeddings=True`)
- **Tokenizer**: `padding_side="left"` (required by Qwen)

### Process
```python
model = SentenceTransformer("Qwen/Qwen3-Embedding-0.6B",
    tokenizer_kwargs={"padding_side": "left"})

all_embs = model.encode(
    texts,                      # df["combined_text"] as list of strings
    batch_size=16,
    show_progress_bar=True,
    convert_to_numpy=True,
    normalize_embeddings=True   # L2 normalization
)

np.save("/dsl/libbot/data/embeddings_qwen.npy", all_embs)
```

### Input
- Reads from `combined_text_full_libguide.parquet`
- Embeds the `combined_text` column (which includes titles prepended to the text)

### Output
- File: `embeddings_qwen.npy`
- Shape: `(7442, 1024)` — float32
- Size: ~30 MB

### Relationship to ChromaDB creation
These two scripts run independently and sequentially:
1. `qwen_embedding_space.py` → produces `embeddings_qwen.npy`
2. `chroma_db_creation.py` → reads `embeddings_qwen.npy` + parquet → writes to ChromaDB

Neither calls the other.

---

## 6. Configuration (.env)

**File**: `ucd_library_libguide_chatbot/.env`

```env
# --- ChromaDB ---
CHROMA_DB_PATH=/dsl/libbot/data/chroma_db
COLLECTION_NAME=libguides

# --- Embedding Model ---
MODEL_NAME=Qwen/Qwen3-Embedding-0.6B
TORCH_NUM_THREADS=16
TOP_K=3

# --- Ollama LLM ---
ACTIVE_LLM_MODE=cloud
OLLAMA_LOCAL_MODEL=libbot_gemma3n-4b-32
OLLAMA_CLOUD_MODEL=libbot-gemma4-cloud
OLLAMA_URL=http://127.0.0.1:11434/api/generate

# --- API Server ---
HOST=0.0.0.0
PORT=8075
```

Settings are loaded via Pydantic `BaseSettings` in `libbot_pkg/config.py`. The `.env` file lives in the repo root (parent of `libbot_pkg/`). Any setting can be overridden via environment variables.

---

## 7. The libbot_pkg Package

### Package structure

```
libbot_pkg/
├── __init__.py      # Exports: Retriever, QueryRequest, QueryResponse, SearchResult, Source, settings
├── __main__.py      # Entry: runs uvicorn on libbot_pkg.api:app
├── config.py        # Settings class (Pydantic BaseSettings, reads .env)
├── models.py        # Pydantic schemas
├── retriever.py     # Core RAG logic
├── api.py           # FastAPI routes
└── static/          # Web UI (HTML/CSS/JS)
```

### Pydantic models (`models.py`)

**Request models:**
```python
class QueryRequest(BaseModel):
    query: str
    top_k: int  # 1-20, default 3

class TurnMemory(BaseModel):
    prompt: str
    response: str

class ChatRequest(BaseModel):
    message: str
    top_k: int  # 1-20, default 3
    history: list[TurnMemory]
```

**Response models:**
```python
class Source(BaseModel):
    libguide_title: str
    section_title: str      # NOTE: maps FROM chunk_title in ChromaDB metadata
    libguide_url: str
    section_url: str        # NOTE: maps FROM chunk_url in ChromaDB metadata
    external_url: str

class SearchResult(BaseModel):
    score: float            # Cosine similarity (0-1, higher is better)
    text: str               # The retrieved text chunk
    sources: list[Source]   # All guides where this text appeared

class QueryResponse(BaseModel):
    query: str
    top_k: int
    results: list[SearchResult]

class ChatResponse(BaseModel):
    message: str
    llm_reply: str
    rag_results: list[SearchResult]
```

### The Retriever — Full Logic (`retriever.py`)

This is the most critical module for pipeline integration. The retriever defines what metadata fields the new pipeline MUST produce.

#### Initialization (lines 17-36)
```python
class Retriever:
    def __init__(self):
        torch.set_num_threads(settings.torch_num_threads)
        self.client = chromadb.PersistentClient(path=settings.chroma_db_path)
        self.collection = self.client.get_collection(name=settings.collection_name)
        self.model = SentenceTransformer(
            settings.model_name,
            device="cpu",
            model_kwargs={"torch_dtype": torch.float32},
            tokenizer_kwargs={"padding_side": "left"},
            trust_remote_code=True,
        )
```

#### Query embedding (lines 47-58)
- Repeats the query for better recall on short queries: `f"{query} {query}"`
- Encodes with `prompt_name="query"` (Qwen's asymmetric query encoding path)
- L2-normalized

#### ChromaDB query (lines 64-77)
```python
candidate_count = top_k * 5  # Over-fetch to handle ~70% duplicates
raw = self.collection.query(
    query_embeddings=[query_emb.tolist()],
    n_results=candidate_count,
    include=["metadatas", "distances"],
)
```

#### Metadata fields the retriever reads from each result (lines 83-124)
These are the **exact field names** the retriever accesses on each metadata dict:

```python
metadata["text"]            # Content text — used for dedup comparisons
metadata["libguide_title"]  # → Source.libguide_title
metadata["chunk_title"]     # → Source.section_title  (NOTE the name change)
metadata["libguide_url"]    # → Source.libguide_url
metadata["chunk_url"]       # → Source.section_url    (NOTE the name change)
metadata["external_url"]    # → Source.external_url
```

**Critical mapping**: ChromaDB field `chunk_title` → Pydantic `Source.section_title`, and `chunk_url` → `Source.section_url`. The retriever does this translation at line 117-122.

#### Fuzzy deduplication (lines 79-128)
The corpus has ~70% duplicate text (same text appears across multiple guides). The retriever:
1. Groups results by text using `SequenceMatcher` (>90% similarity threshold)
2. Handles exact substring matches (one text contains another)
3. Keeps the **longest** version of near-duplicate texts
4. Aggregates all `Source` objects for the same text
5. Stops once `top_k` unique texts are collected

#### Score transformation (line 85)
ChromaDB returns cosine **distance**. The retriever converts to **similarity**: `score = 1 - distance`

#### Post-ranking: Query-title boost (lines 137-147)
Compares query words with `libguide_title` words. Adds `+0.05` per overlapping word. Only applies to the first source of each result.

#### Post-ranking: Source-level MMR (lines 156-176)
Promotes results that introduce new `external_url`s or `libguide_title`s not yet seen. Demotes redundant results.

#### Source deduplication (lines 180-190)
Within each result, removes duplicate sources by `(libguide_title, section_title)` key.

#### Return value (lines 193-202)
Returns `list[SearchResult]` (max `top_k` items), each with `score`, `text`, and `sources`.

### API routes (`api.py`)

| Route | Method | Description |
|-------|--------|-------------|
| `/health` | GET | Liveness check |
| `/search` | POST | Raw retrieval (no LLM). Takes `QueryRequest`, returns `QueryResponse` |
| `/chat` | POST | Full RAG pipeline. Takes `ChatRequest`, streams response as plain text |

**Chat streaming protocol**:
1. First line: `SOURCES:<json>\n` — a JSON array of `{text, sources}` objects
2. Subsequent lines: LLM tokens streamed as they arrive
3. Fallback: If cloud model fails, falls back to local model

**Prompt construction** (`build_context_prompt`, lines 86-131):
```
[=== Previous Conversation === (optional)]
=== Library Documents ===
LibGuide Title: {sources[0].libguide_title}
Section Title: {sources[0].section_title}
{text}

[...more results...]

=== Current User Query ===
{user_message}
```

---

## 8. Test and Research Scripts

### Data preparation
| Script | Description |
|--------|-------------|
| `research/text_cleaning.py` | Normalizes unicode, whitespace, quotes in `text_full_libguide.csv` |
| `research/corpus_update.py` | Creates `combined_text` column, outputs CSV + Parquet |

### Embedding generation (one per model)
| Script | Model | Output |
|--------|-------|--------|
| `research/qwen_embedding_space.py` | Qwen3-Embedding-0.6B | `embeddings_qwen.npy` (PRODUCTION) |
| `research/qwen_4B_embedding_space.py` | Qwen3-Embedding-4B | `4B_embeddings_qwen.npy` |
| `research/sbert_embedding_space.py` | Sentence-BERT MPNet | `embeddings_sbert.npy` |
| `research/mxbai_embedding_space.py` | mxbai-embed-large | `embeddings_mxbai.npy` |
| `research/minilm_embedding_space.py` | MiniLM L6 | `embeddings_minilm.npy` |
| `research/jina_embedding_space.py` | Jina v3 | `embeddings_jina_code.npy` |
| `research/bert_lastlayer_embedding_space.py` | BERT last layer | `embeddings_bert_meanpool.npy` |
| `research/bert_4layer_embedding_space.py` | BERT last 4 layers | `embeddings_last4_meanpool.npy` |
| `research/prompts_embedding_space.py` | Embedding test prompts | `embeddings_testing_prompts.npy` |

### Search benchmarks (one per model)
| Script | Description |
|--------|-------------|
| `research/qwen_search.py` | In-memory cosine search with Qwen embeddings |
| `research/chroma_db_search.py` | ChromaDB-based search prototype (precursor to retriever.py) |
| `research/sbert_search.py` | Sentence-BERT search benchmark |
| `research/mxbai_search.py` | mxbai search benchmark |
| `research/minilm_search.py` | MiniLM search benchmark |
| `research/jina_search.py` | Jina search benchmark |
| `research/qwen_4B_search.py` | Qwen3-4B search benchmark |
| `research/bert_lastlayer_search.py` | BERT last-layer search |
| `research/bert_4layer_search.py` | BERT last-4-layers search |
| `research/bert_compared_search.py` | Side-by-side BERT variant comparison |

### Diagnostics
| Script | Description |
|--------|-------------|
| `research/threshold_vis.py` | Visualizes cosine similarity score decay across ranks |
| `research/ollama_diagnosis.py` | Compares Ollama vs SentenceTransformer embedding behavior |
| `research/ollama_tokens.py` | Ollama tokenization diagnostics |
| `research/ollama_weights.py` | Ollama model weight inspection |
| `research/ollama_test.py` | Ollama connectivity test |
| `research/bert_testing.py` | BERT pooling strategy experiments |

### Standalone test
| Script | Description |
|--------|-------------|
| `test_retriever.py` | Loads Retriever, runs a query, validates Pydantic response structure |

---

## Summary: Integration Contract for New Pipeline

Any new scraping/processing pipeline MUST produce data that satisfies these requirements:

### 1. CSV/Parquet output schema
The parquet file fed to `chroma_db_creation.py` must have these columns:
- `local_id` (int) — unique sequential ID
- `parent_id` (int) — groups chunks by guide
- `text` (str) — cleaned content text
- `libguide_title` (str)
- `libguide_url` (str)
- `chunk_title` (str)
- `chunk_url` (str, can be empty)
- `external_url` (str, can be empty)
- `combined_text` (str) — `"Guide Title: {title}\nSection Title: {section}\n\n{text}"`

### 2. ChromaDB metadata fields
The retriever reads these exact field names from ChromaDB metadata:
- `text`, `libguide_title`, `libguide_url`, `chunk_title`, `chunk_url`, `external_url`

It also stores but does NOT read at query time:
- `parent_id`, `combined_text`

### 3. Embedding requirements
- Model: `Qwen/Qwen3-Embedding-0.6B` via `sentence-transformers`
- Input: the `combined_text` column
- Output: L2-normalized numpy array, shape `(N, 1024)`, float32
- Saved as `.npy` file

### 4. ChromaDB collection
- Name: `libguides`
- Distance: cosine (`hnsw:space: cosine`)
- Document IDs: `str(int(local_id))`

### 5. Data pipeline order
```
1. Scrape → text_full_libguide.csv (8 columns)
2. corpus_update.py → combined_text_full_libguide.parquet (9 columns, adds combined_text)
3. qwen_embedding_space.py → embeddings_qwen.npy
4. chroma_db_creation.py → chroma_db/
```

### 6. Key dependencies
- Python 3.10 (via Pixi, `pixi.toml`)
- `chromadb >= 1.2.1`
- `sentence-transformers`
- `pytorch`
- `pandas`, `numpy`, `pyarrow`
- `fastapi`, `uvicorn`, `httpx`
- `pydantic >= 2.12.5`, `pydantic-settings >= 2.13.0`
- `ollama >= 0.20.4`

### 7. Path conventions
- Production server prefix: `/dsl/libbot/`
- Local development prefix: `/Users/federicolupin/server_mount/`
- Data always lives in `data/` (sibling to the repo directory, NOT inside it)
- ChromaDB path, model name, and other config are set in `.env` — don't hardcode them
