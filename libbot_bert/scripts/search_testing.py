# search_api.py
import numpy as np
import pandas as pd
import torch
from transformers import AutoTokenizer, AutoModel
import os

# -------- CONFIG (change paths if needed) --------
EMB_NPY_PATH = "/dsl/libbot/data/embeddings_bert_meanpool.npy"
CSV_PATH     = "/dsl/libbot/data/text_full_libguide.csv"
TEXT_COL     = "text"
TITLE_COL    = "chunk_title" 
URL_COL      = "libguide_url"
BERT_CHECKPOINT = "bert-base-uncased"
TOP_K = 2

# ------------------------------------------------

# ---- global runtime state (loaded once) ----
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# load embeddings + normalize (done once)
if not os.path.exists(EMB_NPY_PATH):
    raise FileNotFoundError(f"Embedding file not found: {EMB_NPY_PATH}")

emb_matrix = np.load(EMB_NPY_PATH)                     # (n, dim)
n_rows, emb_dim = emb_matrix.shape
# L2-normalize rows -> used to compute cosine similarity with dot product
emb_norms = np.linalg.norm(emb_matrix, axis=1, keepdims=True)
emb_norms = np.clip(emb_norms, 1e-9, None)
emb_matrix_normed = emb_matrix / emb_norms             # (n, dim)

# load original dataframe (for metadata retrieval)
df = pd.read_csv(CSV_PATH)
if len(df) != n_rows:
    # Not required but helpful for debugging; still proceed if lengths differ
    print(f"Warning: embedding rows ({n_rows}) != dataframe rows ({len(df)})")

# load model + tokenizer once
tokenizer = AutoTokenizer.from_pretrained(BERT_CHECKPOINT)
model = AutoModel.from_pretrained(BERT_CHECKPOINT).to(device)
model.eval()

# ---------- helper: mean pooling (same function used when embeddings were created) ----------
def mean_pool_from_model(outputs_last_hidden, attention_mask):
    """
    last_hidden: (batch, seq_len, dim)
    attention_mask: (batch, seq_len)
    returns: (batch, dim)
    """
    # make mask broadcastable to last_hidden: (batch, seq_len, 1) -> expand to (batch, seq_len, dim)
    attn = attention_mask.unsqueeze(-1).expand(outputs_last_hidden.size()).float()
    # zero out padding token vectors
    sum_hidden = (outputs_last_hidden * attn).sum(dim=1)       # (batch, dim)
    token_counts = attn.sum(dim=1)                            # (batch, dim) (same values across dim)
    token_counts = torch.clamp(token_counts, min=1e-9)        # avoid div0
    return sum_hidden / token_counts                          # (batch, dim)

# ---------- embed a single query text (returns L2-normalized numpy vector) ----------
def embed_query(text: str) -> np.ndarray:
    """
    Compute a mean-pooled embedding for the input text and return a L2-normalized numpy vector.
    Uses the same model + pooling logic used to create stored embeddings.
    """
    # handle None or NaN gracefully
    if text is None:
        text = ""
    text = str(text)

    # tokenize single example (no padding needed for single example)
    inputs = tokenizer(text, truncation=True, return_tensors="pt")
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model(**inputs, output_hidden_states=False, return_dict=True)

    last_hidden = outputs.last_hidden_state         # (1, seq_len, dim)
    attn_mask = inputs["attention_mask"]            # (1, seq_len)
    emb = mean_pool_from_model(last_hidden, attn_mask)  # (1, dim)
    emb = emb.squeeze(0).cpu().numpy()                 # -> (dim,)

    norm = np.linalg.norm(emb)
    if norm < 1e-9:
        return emb
    return emb / norm

# ---------- reusable search function ----------
def search(query: str, k: int = 10) -> pd.DataFrame:
    """
    Query the embedding index and return a DataFrame with top-k results.
    Columns returned: ['chunk_title','libguide_url','text','score'] sorted by descending score.
    """
    # compute normalized query embedding
    q_emb = embed_query(query)               # (dim,)
    if q_emb.shape[0] != emb_dim:
        raise ValueError(f"Query embedding dim {q_emb.shape[0]} != stored dim {emb_dim}")

    # fast cosine similarity via dot product with pre-normalized embeddings
    sims = emb_matrix_normed.dot(q_emb)      # (n,)

    # get top-k indices (descending by similarity)
    if k <= 0:
        return pd.DataFrame(columns=[TITLE_COL, URL_COL, TEXT_COL, "score"])
    k = min(k, len(sims))
    topk_idx = np.argsort(-sims)[:k]
    topk_scores = sims[topk_idx]

    # collect metadata and scores into a DataFrame
    # handle missing columns gracefully
    cols = []
    for col in [TITLE_COL, URL_COL, TEXT_COL]:
        if col in df.columns:
            cols.append(col)
        else:
            # create empty placeholder column if missing
            df[col] = ""
            cols.append(col)

    topk_rows = df.loc[topk_idx, cols].reset_index(drop=True).copy()
    topk_rows["score"] = topk_scores
    # ensure ordering by score descending
    topk_rows = topk_rows.sort_values("score", ascending=False).reset_index(drop=True)
    return topk_rows

# ---------- simple CLI example ----------
if __name__ == "__main__":
    example_query = "give me resources for architecture research"
    results = search(example_query, k=TOP_K)
    print(f"Top {len(results)} results for query: {example_query}\n")
    for i, row in results.iterrows():
        print(f"{i+1:2d}. score={row['score']:.4f}")
        print(f"    Title: {row.get(TITLE_COL, '')}")
        print(f"    URL:   {row.get(URL_COL, '')}")
        txt = row.get(TEXT_COL, "")
        print("    Text:", repr(txt[:200]) + ("..." if len(txt) > 200 else ""))
        print()
