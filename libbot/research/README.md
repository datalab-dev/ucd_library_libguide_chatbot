# Scripts

Testing out different embedding models, search scripts, visualizations, and database structures.

## Prerequisites

Everything is run through Pixi package management tool. Once Pixi is installed, to ensure reproducibility, also install the Pixi environment (based on the existing, examinable, pixi.toml file) with :
```bash
# bash/zsh
pixi install
```

## Usage
```bash
# bash/zsh

# General Pattern for Creation of Embedding Space(s)
pixi run python scripts/<script_name_embedding_space>.py

# General Pattern for Search Scripts
pixi run python scripts/<script_name_search>.py [query/prompt]
```

## Embedding Scripts

| Script | Description |
|--------|-------------|
| `bert_lastlayer_embedding_space.py` | Creates corpus embedding vector space using a mean pool over the last hidden layer of base-BERT model |
| `bert_4layer_embedding_space.py` | Creates corpus embedding vector space using a mean pool over the last 4 hidden layers of base-BERT model |
| `sbert_embedding_space.py` | Creates corpus embedding vector space using Sentence BERT model multi-qa-mpnet-base-cos-v1 |
| `mxbai_embedding_space.py` | Creates corpus embedding vector space using Sentence Transformer model mxbai-embed-large |
| `minilm_embedding_space.py` | Creates corpus embedding vector space using Sentence Transformer model all-MiniLM-L6-v2 |
| `jina_embedding_space.py` | Creates corpus embedding vector space using Sentence Transformer model jina-embeddings-v3 |
| `qwen_embedding_space.py` | Creates corpus embedding vector space using Sentence Transformer model Qwen3-Embedding-0.6B |
| `qwen_4B_embedding_space.py` | Creates corpus embedding vector space using Sentence Transformer model Qwen3-Embedding-4B |
| `prompts_embedding_space.py` | Creates embedding vector space using Sentence Transformer model Qwen3-Embedding-0.6B, specifically for selected prompts, testing for general retrieval performance |

## Search Scripts

| Script | Description |
|--------|-------------|
| `bert_lastlayer_search.py` | Search script for the base-BERT last-layer embedding space |
| `bert_4layer_search.py` | Search script for the base-BERT last-4-layers embedding space |
| `bert_compared_search.py` | Search script that uses both embeddings from base-BERT (last hidden layer, and the last 4 hidden layers) and compares ouputs |
| `sbert_search.py` | Search script for the Sentence BERT multi-qa-mpnet-base-cos-v1 embedding space |
| `mxbai_search.py` | Search script for the Sentence Transformer mxbai-embed-large embedding space |
| `minilm_search.py` | Search script for the Sentence Transformer all-MiniLM-L6-v2 embedding space |
| `jina_search.py` | Search script for the Sentence Transformer jina-embeddings-v3 embedding space |
| `qwen_search.py` | Search script for the Sentence Transformer Qwen3-Embedding-0.6B embedding space |
| `qwen_4B_search.py` | Search script for the Sentence Transformer Qwen3-Embedding-4B embedding space |
| `chroma_db_search.py` | Search script for the Sentence Transformer Qwen3-Embedding-0.6B embedding space stored in ChromaDB vector database |

## Other Scripts

| Script | Description |
|--------|-------------|
| `bert_testing.py` | Experimentation with BERT and using transformers and pytorch libraries |
| `chroma_db_creation.py` | Migration of Qwen3-Embedding-0.6B embedding space into ChromaDB vector database |
| `corpus_update.py` | Created new corpus column for combined text (appending libguide and section title, to text chunks) |
| `df_url_crawl.py` | Getting the links to all the updated libguides and storing into a df (unused) |
| `milvus_db_creation.py` | Attempted migration of Qwen3-Embedding-0.6B embedding space into Milvus vector database; unsuccessful due to server architecture |
| `ollama_diagnosis.py` | Experimentation to look for differences in embedding generation and retrieval, using Ollama vs. Sentence Transformers with the same model and text; also checking whether using an encoding label (e.g. "query") makes any difference |
| `ollama_tokens.py` | Experimentation to see whether giving the model a prompt prefix (which Ollama does automatically, but has to be done manually when using Sentence Transformers), makes a difference in tokenization |
| `sql_url_crawl.py` | Getting the links to all the libguides and storing into SQLite (unused) |
| `text_cleaning.py` | Newly cleaned corpus to deal with formatting issues that arose when bringing data over from R to Python |
| `threshold_vis.py` | Visualization of how many documents are worth actually using/keeping in retrieval, based on similarity measure (using prompts_embedding_space) |


