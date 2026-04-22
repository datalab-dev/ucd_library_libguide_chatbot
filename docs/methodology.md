# LibBot Methodology Notes
> by Federico G. Aprile

<br>

> [!NOTE]
> ### LLM Evaluated
> Information regarding the LLMs used in the document synthesis portion of the RAG system can be found in the [Ollama notes](https://github.com/datalab-dev/ucd_library_libguide_chatbot/blob/main/docs/ollama.md) doc.

<br>

## Embedding Models Evaluated

The following models were tested during development. Models are listed in the order they were evaluated. All retrieval examples below use the same query across models for direct comparison.

> [!WARNING]
> SECTION IS UNDER CONSTRUCTION; Image examples between models are missing. 2 Example Queries will be shown for each, to display the difference between weaker and stronger models.

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

> $\color{Red}\large{\textsf{BERT}}$

BERT (`bert-large-cased`) was the first model evaluated, tested in two configurations: extracting the last hidden layer only, and averaging across the last four hidden layers. Both configurations performed poorly for this task, and BERT is not recommended for semantic retrieval.

The core reason is architectural: BERT is trained using **Masked Language Modeling (MLM)**, which masks random tokens in a sentence and asks the model to predict them. This makes BERT good at understanding local token relationships, but it does not optimize the model to produce meaningful sentence or paragraph-level embeddings. The result is an **anisotropic** embedding space, where vectors cluster in a narrow cone rather than spreading evenly across the vector space; this severely limits the model's ability to distinguish between semantically different documents.

Mean pooling over the last hidden layer washes out salient information across long inputs, producing behavior closer to a bag-of-words model. Averaging across four layers compounds this problem further because it does not pool over the CLS token, which is the token BERT uses for sequence-level representation. BERT-large is also a 2019 model, and the field has moved significantly beyond it for retrieval tasks. Sentence-BERT models trained specifically for embedding-space alignment substantially outperform BERT-large on semantic search.

---

> $\color{Darkorange}\large{\textsf{Sentence Transformers (SBERT / MPNet)}}$

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

> $\color{Yellowgreen}\large{\textsf{JINA}}$

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

> $\color{Green}\large{\textsf{Qwen3-Embedding-0.6B}}$

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

<br>

---

## Similarity Measures and Normalization

All models in this project use **cosine similarity** as the retrieval metric. Cosine similarity measures the angle between two vectors rather than their magnitude, making it well-suited for semantic retrieval where the direction of a vector encodes meaning and the scale does not.

Regardless of whether a model already normalizes its output internally (as `multi-qa-mpnet-base-cos-v1` and Qwen3 do), `normalize_embeddings=True` is explicitly passed during all encoding calls. Normalization ensures that cosine similarity scores are always in the range [-1, 1] and that results are comparable across queries and documents, even if a model's internal normalization behavior changes across versions.

In the research phase, the `cos_sim` function from the Sentence Transformers `util` module and the `model.similarity()` functions, were both tested out. The distinction matters is that `cos_sim` operates on already-generated embedding vectors, while `model.similarity()` takes raw text as input and encodes it internally. Using `cos_sim` gives explicit control over the encoding step, which is important for applying prompt names, normalization flags, and other encoding parameters consistently across queries and documents; therefore it ended up being the one that was used most.

Once the corpus was moved over to the ChromaDB vector databse, the similarity search was performed the same way, explicitly configuring the ChromaDB collection with `{"hnsw:space": "cosine"}` and ensuring query embeddings are unit-normalized during ncoding. To provide standard similarity scores for ranking and deduplication, the system transforms ChromaDB’s output using the formula $1 - \text{distance}$.

<br>

---

## Handling Duplicate Text in the Corpus

The LibGuides corpus contains approximately 70% duplicate text chunks (the same passage appearing across multiple guides or sections). This creates a retrieval problem: a traditional top-k search will often return the same text multiple times under different source URLs, wasting retrieval slots and giving the LLM redundant context.

### Evolution of the Deduplication Approach

The final deduplication strategy went through several iterations before settling on its current form.

**First approach — no deduplication:** The initial implementation retrieved top-k results directly without any deduplication. This frequently returned the same text chunk multiple times, which was unhelpful for downstream LLM synthesis.

**Second approach — full deduplication:** Duplicates were removed entirely, keeping only the highest-scoring instance of each unique text. This resolved the redundancy problem but created a new one: when the same text chunk appeared across multiple guides, discarding the duplicates meant losing the additional source URLs associated with them. A user who would have benefited from being pointed to multiple relevant guides only received one.

**Third approach — deduplication with source aggregation**: The implementation retrieved top_k * 5 candidates and iterated through them, appending new source URLs to existing entries for exact text matches. This preserved source attribution while presenting unique text to the LLM.

**Fourth approach (current) — fuzzy deduplication and completion**: To account for redundancy in the corpus--where similar content often appears with slight variations in length, for example--the logic was expanded beyond exact matches. The current system uses the SequenceMatcher algorithm to identify "near-duplicates" with over 90% similarity or cases where one chunk is a complete substring of another. When a near-match is found, the system compares the length of the new text against the stored version; if the new text is longer, it replaces the existing entry to ensure the LLM receives the most complete information available. This ensures that even when guides have slightly different formatting or overlapping sections, the final context is both exhaustive and concise, while still aggregating all relevant source URLs across the similar chunks.

This approach also handles the LLM synthesis step cleanly because the model receives top_k unique, non-redundant text chunks as context, with source attribution preserved for citation in the response.

<br>

---

## Source Retrieval Reranking Pipeline

After ChromaDB returns candidates and fuzzy text deduplication runs, three sequential steps now refine the final ordering before results are returned:

- **Score-based sort** — results are sorted by cosine similarity score descending, as before.
- **Query-title boost** — each result's guide titles are compared against the query using simple word overlap. Results whose guide title shares words with the query receive a small score nudge (+0.05 per overlapping word). This corrects for cases where a topically-named guide (e.g. "Art, Architecture, Art History and Design") has highly relevant sources but whose text chunks happened to score lower than more generic guides (e.g. "Film & Media Studies") that also link to the same external resource. Results are re-sorted after the boost.
- **Source-level MMR** — walks the re-sorted list and tracks seen external_urls and libguide_titles. Any result that introduces at least one new guide or external resource is promoted; results that are entirely redundant are demoted to the back. This ensures that a guide introducing unique resources (e.g. Guggenheim, Kress Foundation) surfaces above a fourth or fifth guide that only repeats an already-seen resource (e.g. ARTstor).

> **Conclusion**: pure embedding score alone is insufficient for source ordering in a multi-guide corpus where generic guides broadly index the same popular databases. The boost + MMR combination gives topically specific guides the ranking they deserve. The final sources displayed by LibBot are the LibGuide section associated with the query, as well as any external resources it may point to.

<br>

---

## Final Model Parameter Size: Qwen3 0.6B vs. 4B

A counterintuitive finding emerged during model selection: `Qwen3-Embedding-0.6B` outperformed `Qwen3-Embedding-4B` in retrieval quality on this corpus, or at minimum matched itl, while being substantially faster.

### What Was Tested

Six configurations were evaluated systematically across both parameter sizes:

| Configuration | 0.6B | 4B |
|---|---|---|
| Standard retrieval, no preprocessing | + | — |
| Title-labeled text chunks + deduplication | + | + |
| Title-labeled chunks + deduplication + double query | + | + |

Title labeling refers to prepending each text chunk with its LibGuide section title before generating embeddings; this technique was identified during the Ollama vs. Sentence Transformers investigation that brings contextually related chunks closer together in the embedding space.

### Findings

Across these configurations, 0.6B and 4B typically retrieved the same documents. In cases where they differed, 0.6B occasionally retrieved slightly more relevant results. Given that 0.6B is also significantly faster on a CPU-only server, it was selected as the final model.

The double query technique was to append the user's query to itself before encoding, with the intention of amplifying the query signal in the attention window (technique specifically targets Decoder-only architectures like Qwen's); it produced very slight improvements for 0.6B. For 4B it made results the same or slightly worse.

### Why Might a Smaller Model Outperform a Larger One Here?

This remains an open question. The 4B model is more sensitive to subtle semantic differences between documents, which might be expected to help but in practice this sensitivity may work against it on a corpus where many chunks are structurally similar library guide passages. The 0.6B model's slightly coarser representations may produce a more stable ranking across similar documents, whereas the 4B model's finer-grained distinctions introduce more variability in edge cases.

It is also worth noting that all comparisons were conducted on a CPU-only server, where the 4B model operates under significantly more computational pressure than the 0.6B model. Whether the performance gap would persist on a GPU-accelerated setup is unknown at the moment.

The practical outcome is clear regardless: 0.6B matches or beats 4B on this corpus, runs faster, and was selected as the final model on that basis.

### Final Configuration

The final LibBot implementation uses:
- `Qwen3-Embedding-0.6B` via Sentence Transformers
- Title-labeled text chunks at **corpus embedding time** (preprocessing, not at query time)
- Deduplication with source aggregation — `top_k * 5` candidates, early exit at `top_k` unique texts, sources aggregated across duplicates
- Double query

<br>

---

## Retrieval Threshold Investigation

To inform the choice of `top_k` (documents to retrieve) a threshold analysis was conducted by plotting cosine similarity scores against document rank across a set of test queries.

### Method

The analysis used `threshold_vis.py` (in `research/`), which takes a set of query 
embeddings and the full corpus embeddings, computes cosine similarity between each 
query and every document in the corpus, sorts the results by descending similarity, 
and plots the decay curves. Two visualizations are produced for each run:

- **Left plot** — individual decay curves, one per query, overlaid on the same axes
- **Right plot** — the mean similarity curve averaged across all queries

Two runs were conducted:

- **Simulated queries** — corpus documents randomly sampled and used as proxy queries, plotted across the full corpus size (k = 7,442) to understand the global shape of similarity decay
- **Real queries** — a set of manually written test prompts, embedded and used as actual queries, plotted at k = 100 to zoom into the operationally relevant range

### Results

**Simulated queries (Full corpus view):**

![Threshold analysis — full corpus](assets/rag_threshold_analysis_extended.png)

The left plot shows all individual query curves decaying rapidly in the first few 
hundred documents and then flattening into a long tail above k = 1,000. The right 
plot confirms this pattern; in the mean curve — similarity drops steeply from ~0.65 
at k = 1 to around 0.30 by k = 1,000, then continues declining slowly.

**Top-100 view (real queries):**

![Threshold analysis — top 100](assets/rag_threshold_analysis.png)

For this one we have real queries zoomed into the top 100 documents. The individual curves show more spread than the simulated run. The mean curve shows a  steep initial drop from ~0.67 at k = 1 to ~0.56 at k = 10, and then a continued decline to ~0.50 at k = 100. The absence of a sharp drop reflects the natural 
variability of real user queries and the uneven coverage of topics across the LibGuides 
corpus.

### Conclusion

The analysis confirmed that meaningful similarity signal is concentrated in a small 
number of top-ranked documents. A value of `top_k = 3` was selected as the default for LibBot, retrieving enough context for the LLM to synthesize a grounded response without overwhelming it with low-signal documents. The `top_k * 5` candidate fetch used in the deduplication step (described above) is applied on top of this, ensuring that 3 unique, high-quality texts are returned even in a corpus with ~70% duplication.

<br>
