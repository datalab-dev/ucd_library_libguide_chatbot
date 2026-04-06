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

<br>

---

## Research and Technical Notes on Key Models

### BERT

BERT (`bert-large-cased`) was the first model evaluated, tested in two configurations: extracting the last hidden layer only, and averaging across the last four hidden layers. Both configurations performed poorly for this task, and BERT is not recommended for semantic retrieval.

The core reason is architectural: BERT is trained using **Masked Language Modeling (MLM)**, which masks random tokens in a sentence and asks the model to predict them. This makes BERT good at understanding local token relationships, but it does not optimize the model to produce meaningful sentence or paragraph-level embeddings. The result is an **anisotropic** embedding space, where vectors cluster in a narrow cone rather than spreading evenly across the vector space; this severely limits the model's ability to distinguish between semantically different documents.

Mean pooling over the last hidden layer washes out salient information across long inputs, producing behavior closer to a bag-of-words model. Averaging across four layers compounds this problem further because it does not pool over the CLS token, which is the token BERT uses for sequence-level representation. BERT-large is also a 2019 model, and the field has moved significantly beyond it for retrieval tasks. Sentence-BERT models trained specifically for embedding-space alignment substantially outperform BERT-large on semantic search.

---

### Sentence Transformers (SBERT / MPNet)

After BERT, development moved to the Sentence Transformers library, which provides models explicitly trained for semantic similarity and retrieval tasks. Two SBERT models were evaluated: `all-MiniLM-L6-v2` and `multi-qa-mpnet-base-cos-v1`.

**`all-MiniLM-L6-v2`** was not selected. While it is fast and compact (384 dimensions), it truncates inputs longer than 256 tokens, which is a significant limitation for library guide content that frequently exceeds that length. Its embeddings are also noticeably less precise than larger models.

**`multi-qa-mpnet-base-cos-v1`** was the strongest SBERT candidate evaluated. It is based on MPNet (Masked and Permuted Pre-training), a transformer architecture from Microsoft that improves on BERT and XLNet by combining masked token prediction with permuted language modeling, giving it better language understanding than either predecessor. It was also explicitly fine-tuned on large-scale question-answering and search data, making it well-suited for asymmetric retrieval, where a short query is matched against longer documents.

Key practical properties of this model:
- Pooling and normalization are handled internally — `model.encode()` returns a single 768-dimensional embedding directly, with no additional pooling step required
- Outputs L2-normalized vectors (the `cos` variant ensures this), meaning they integrate directly with cosine similarity search without any preprocessing
- Handles full paragraphs (up to ~300 words) without degradation

Other strong SBERT candidates identified during research but not evaluated in full:
- `sentence-transformers/gtr-t5-base` — a T5-based dual-encoder trained on multi-domain queries, shown to significantly outperform prior retrievers; a strong choice if queries are phrased as questions
- `all-mpnet-base-v2` — the best general-purpose SBERT model for domains where neither of the above applies

---

### Jina

`jina-embeddings-v3` is a flexible embedding model that supports **task-specific encoding** through a `task` argument at inference time. This allows the same model to produce qualitatively different embeddings depending on the intended use:

| Task Argument | Use Case |
|---|---|
| `retrieval.query` | Query embeddings for asymmetric retrieval |
| `retrieval.passage` | Passage/document embeddings for asymmetric retrieval |
| `separation` | Clustering and re-ranking |
| `classification` | Classification tasks |
| `text-matching` | Symmetric retrieval and semantic textual similarity (STS) |

For this RAG pipeline, `retrieval.query` and `retrieval.passage` were used together, encoding queries and documents differently to better capture the asymmetric relationship between them. Jina also supports **Matryoshka embeddings** with flexible output dimensions (32 to 1024), making it adaptable to different computational constraints.

Jina was not selected as the final model primarily because Qwen3 outperformed it on retrieval quality for this corpus, but it remains a strong candidate for future iterations or use cases requiring task-specific flexibility.

---

### Qwen3-Embedding-0.6B

Qwen3-Embedding-0.6B was selected as the embedding model for the current LibBot implementation. It offered the best retrieval performance across all models evaluated, with the best trade-off between quality and computational feasibility on a CPU-only server.

#### Architecture: Dual Encoder

Qwen3 is a **dual encoder** — it uses separate encoding paths for queries and documents. This asymmetric design is important for retrieval: a user's short natural language query and a longer library guide passage are semantically different in structure, and encoding them separately allows the model to capture that relationship more accurately than a single shared encoder would.

For comparison, a **cross encoder** processes the query and document together in a single input with full attention across all tokens. Cross encoders are more precise but far slower, making them unsuitable for first-stage retrieval over large corpora. The standard pattern in high-quality RAG pipelines is:

1. Dual encoder retrieves the top N candidates quickly
2. Cross encoder reranks those candidates for precision

LibBot currently uses only the dual encoder stage. Cross-encoder reranking is a candidate for a future iteration.

#### EOS Pooling

Unlike SBERT models that use mean pooling, Qwen3 uses **EOS (End of Sequence) token pooling**. The embedding vector is produced by taking the hidden state of the final `[EOS]` token from
the last transformer layer. Essentially, internally:

1. Input text is tokenized
2. Tokens are passed through all transformer layers
3. The hidden state of the final `[EOS]` token is extracted from the last layer
4. A projection layer is applied if needed
5. The resulting vector is returned as the embedding

The `[EOS]` token's hidden state ends up being like a learned summary of the entire input sequence; it has attended to all other tokens and accumulated the full semantic content of the input. This is meaningfully different from mean pooling, where all token vectors from the last layer are averaged together regardless of their individual importance.

#### Training

Qwen3 was trained using a combination of approaches that contribute to its strong generalization:

- **LLM-generated query-document pairs** with contrastive learning — weak labels but cheap and large scale, giving broad retrieval ability across domains
- **Human supervised fine-tuning** for precision on specific retrieval tasks
- **Model merging** — multiple training variants are merged to eliminate overfitting from any single training run, improving generalization across domains

It also supports **Matryoshka Representation Learning (MRL)**: the embedding vector is structured so that its most important information is concentrated in the first dimensions, with subsequent dimensions adding refinements. This means the vector can be truncated from 4096 → 1024 → 256 → 64 dimensions and still produce meaningful results — useful if storage or compute constraints require smaller vectors in future iterations.

#### Known Limitations

- The multilingual tokenizer fragments acronyms badly, which can affect retrieval quality for queries or documents that rely heavily on abbreviations
- Qwen3 is not heavily trained on academic course code distributions, so queries involving course codes (e.g. "STS 195") may not retrieve as accurately as general natural language queries

---

### Ollama vs. Sentence Transformers

One of the more involved investigations during development was understanding why the same model — `mxbai-embed-large` — produced noticeably different retrieval results depending on whether it was loaded through Sentence Transformers or served through Ollama, as it had been in the original R prototype.

The investigation started by looking at the obvious candidates: tokenization differences (as shown in the `ollama_tokens.py` script in `research/`), pooling differences, and whether Ollama was applying any internal preprocessing that Sentence Transformers was not. One specific test involved regenerating the mxbai embedding space with an explicit prompt prepended during encoding: similar to a task specification, analogous to how models like Qwen3 use `prompt_name="query"` to activate a query-specific encoding path. The goal was to see whether adding this kind of instruction changed retrieval behavior, particularly queries involving course abbreviations where performance had been inconsistent. It turned out that Ollama does not actually support prompt types like `"query"` for mxbai, so this was not the source of the discrepancy.

To investigate further, Ollama and the mxbai model were installed directly on the datasci server and a dedicated comparison script (`ollama_diagnosis.py` in `research/`) was written to probe the differences between the two implementations. The first concrete difference found was that the two frameworks produced different tensor types: Ollama returned `float64` vectors while Sentence Transformers returned `float32`. This seemed like a likely culprit but turned out not to matter meaningfully for retrieval quality after normalization.

The actual source of the discrepancy was found eventually and had nothing to do with the frameworks themselves. In the original group prototype, document text chunks had their **LibGuide titles prepended** before generating embeddings with Ollama. These title prefixes acted as semantic labels — they pulled vague or ambiguous text chunks from the same LibGuide closer together in the embedding space, giving the embeddings more context about what each chunk was about. When the model was brought over to Sentence Transformers without replicating this preprocessing step, the embeddings were generated from raw text chunks only, producing a subtly but meaningfully different embedding space. Matching the preprocessing resolved the discrepancy.




**Normalization, similarity measures** — This is well-reasoned technical methodology that contextualizes your model choices.

**Duplicate text handling** —  This is a real methodological decision specific to your corpus (the ~70% duplication problem) and how you solved it is worth documenting. It directly affects retrieval quality.

**Performance differences between same model, different parameter sizes** — Directly informs the model choice and is useful context for anyone inheriting the project.

**Threshold investigation and visualizations** — The plots of docs vs. similarity scores are exactly the kind of thing that belongs in a public methodology doc. Shows your reasoning for top_k and retrieval depth decisions.

**Image examples comparing models** — yes, a curated selection. Not all of them — pick the 3-5 that most clearly show the difference between a weaker and stronger model on the same query. Quality over quantity.
