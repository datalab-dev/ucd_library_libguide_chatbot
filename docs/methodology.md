# LibBot Methodology

## Embedding Models Evaluated

The following models were tested during development. Models are listed in the order they were evaluated. All retrieval examples below use the same query across models for direct comparison.

| Model | Dimensions | Output Type | Pooling | Status | Example |
|---|---|---|---|---|---|
| `bert-large-cased` (last hidden layer) | 1024 | Last hidden state of final transformer layer | Mean pooling of last hidden layer | **Not recommended** — not a sentence model; trained for MLM, not embedding-space alignment | ![bert-last-hidden example](assets/bert_last_hidden_example.png) |
| `bert-large-cased` (last 4 hidden layers) | 1024 | Concatenated last 4 hidden states | Mean pooling across last 4 hidden layers | **Not recommended** — not a sentence model; multi-layer mean pooling further dilutes signal without CLS token | ![bert-last-4-hidden example](assets/bert_last_4_hidden_example.png) |
| `mxbai-embed-large` (legacy R + Ollama prototype) | 512 | Weighted multi-layer representation | Pooling + projection | **Legacy prototype** — good performance but used via Ollama in R; superseded by Python implementation | ![mxbai legacy example](assets/mxbai_legacy_example.png) |
| `multi-qa-mpnet-base-cos-v1` | 768 | Last hidden state of MPNet | Mean pooling of last hidden layer → dense projection + L2 normalization | **Strong candidate** — explicitly tuned on QA/search data; outputs normalized vectors; best among SBERT models tested | ![mpnet example](assets/mpnet_example.png) |
| `mxbai-embed-large` (Python + Sentence Transformers) | 512 | Weighted multi-layer representation | Pooling + projection | **Legacy prototype brought to Python** — same model as R prototype, used to validate consistency across implementations | ![mxbai python example](assets/mxbai_python_example.png) |
| `all-MiniLM-L6-v2` | 384 | Last hidden state | Mean pooling | **Not selected** — truncates inputs longer than 256 tokens; embeddings noticeably less precise than larger models | ![minilm example](assets/minilm_example.png) |
| `jina-embeddings-v3` | Matryoshka: 32, 64, 128, 256, 512, 768, 1024 | Task-specific contextual embeddings | Task-conditioned pooling | **Not selected but strong candidate** — flexible dimensions and task-specific encoding make it versatile | ![jina example](assets/jina_example.png) |
| `Qwen3-Embedding-0.6B` | Up to 4096 (user-defined: 32–4096) | EOS token hidden state (final transformer layer) | EOS pooling — hidden state of final [EOS] token; no mean pooling | 🟢 Selected — best retrieval performance; multilingual dual-encoder architecture; Matryoshka-compatible; supports query/document asymmetric encoding | ![qwen3 example](assets/qwen3_example.png) |

## Technical Notes on Key Models
### BERT
### Sentence Transformers (SBERT / MPNet)
### Jina
### Qwen3
### Ollama vs. Sentence Transformers






**Model comparison table** — Seeing which models were tested, their characteristics, and comparative results is genuinely useful to anyone doing similar work. The links to result images make it even better (no column on retrieval script)

**Normalization, similarity measures** — This is well-reasoned technical methodology that contextualizes your model choices.

**Duplicate text handling** —  This is a real methodological decision specific to your corpus (the ~70% duplication problem) and how you solved it is worth documenting. It directly affects retrieval quality.

**Ollama vs Sentence Transformers differences for the same model** —  This is a genuinely interesting and non-obvious finding that took work to figure out. Worth writing up as a short section.

**Performance differences between same model, different parameter sizes** — Directly informs the model choice and is useful context for anyone inheriting the project.

**Threshold investigation and visualizations** — The plots of docs vs. similarity scores are exactly the kind of thing that belongs in a public methodology doc. Shows your reasoning for top_k and retrieval depth decisions.

**Model-specific notes on Jina, Qwen, dual encoders, EOS, training differences** — yes, but selectively. The conceptual findings (dual encoders, EOS token behavior, how training affects results) are worth writing up. Specific raw notes about individual models are worth including only if they explain a decision you made.

**Image examples comparing models** — yes, a curated selection. Not all of them — pick the 3-5 that most clearly show the difference between a weaker and stronger model on the same query. Quality over quantity.
