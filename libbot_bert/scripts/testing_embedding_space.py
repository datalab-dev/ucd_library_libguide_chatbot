# compare_300_embeddings.py
import torch
from transformers import AutoTokenizer, AutoModel
import pandas as pd
import numpy as np
import math
import os

# -------- CONFIG --------
CSV_PATH = "/dsl/libbot/data/text_full_libguide.csv"
TEXT_COL = "text"
TITLE_COL = "chunk_title"
URL_COL = "libguide_url"

BERT_CHECKPOINT = "bert-large-cased"
BATCH_SIZE = 16

NUM_ROWS = 500   # <--- set to 300 for your experiment (must be same for both methods)
OUT_MEANLAST_NPY = "/dsl/libbot/data/emb_meanlast_300.npy"
OUT_LAST4MEAN_NPY = "/dsl/libbot/data/emb_last4mean_300.npy"
# ------------------------

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("Device:", device)

# load data (first NUM_ROWS rows)
df = pd.read_csv(CSV_PATH)
texts = df[TEXT_COL].fillna("").astype(str).tolist()[:NUM_ROWS]
n = len(texts)
print("Embedding rows:", n)

# load model + tokenizer once
tokenizer = AutoTokenizer.from_pretrained(BERT_CHECKPOINT)
model = AutoModel.from_pretrained(BERT_CHECKPOINT).to(device)
model.eval()

def mean_pool_tokens_from_hidden(last_hidden, attention_mask):
    """Token-wise mean pooling (ignores padding)."""
    attn = attention_mask.unsqueeze(-1).expand(last_hidden.size()).float()
    sum_hidden = (last_hidden * attn).sum(dim=1)
    token_counts = attn.sum(dim=1)
    token_counts = torch.clamp(token_counts, min=1e-9)
    return sum_hidden / token_counts

def embed_mean_last(texts_batch_list):
    """
    Compute mean pooling over the LAST hidden layer for the given batch (list of strings).
    Returns numpy array shape (batch, hidden).
    """
    inputs = tokenizer(texts_batch_list, padding=True, truncation=True, return_tensors="pt")
    inputs = {k: v.to(device) for k, v in inputs.items()}
    with torch.no_grad():
        outputs = model(**inputs, output_hidden_states=False, return_dict=True)
    last_hidden = outputs.last_hidden_state  # (batch, seq_len, hidden)
    emb = mean_pool_tokens_from_hidden(last_hidden, inputs["attention_mask"])  # (batch, hidden)
    emb = torch.nn.functional.normalize(emb, p=2, dim=1)  # L2 normalize rows
    return emb.cpu().numpy()

def embed_last4_mean(texts_batch_list):
    """
    Compute token-wise average of last 4 layers, then mean-pool tokens.
    Returns numpy array shape (batch, hidden).
    """
    inputs = tokenizer(texts_batch_list, padding=True, truncation=True, return_tensors="pt")
    inputs = {k: v.to(device) for k, v in inputs.items()}
    with torch.no_grad():
        outputs = model(**inputs, output_hidden_states=True, return_dict=True)
    hidden_states = outputs.hidden_states  # tuple (embeddings + layers)
    # stack last 4 layers and average token-wise
    last4 = torch.stack(hidden_states[-4:], dim=0)   # (4, batch, seq_len, hidden)
    last4_mean = last4.mean(dim=0)                  # (batch, seq_len, hidden)
    emb = mean_pool_tokens_from_hidden(last4_mean, inputs["attention_mask"])  # (batch, hidden)
    emb = torch.nn.functional.normalize(emb, p=2, dim=1)
    return emb.cpu().numpy()

# ---------- compute embeddings in batches ----------
def compute_embeddings_for_texts(texts, batch_size, method="mean_last"):
    all_embs = []
    num_batches = math.ceil(len(texts) / batch_size)
    for i in range(num_batches):
        start = i * batch_size
        end = min(start + batch_size, len(texts))
        batch = texts[start:end]
        if method == "mean_last":
            batch_emb = embed_mean_last(batch)
        elif method == "last4_mean":
            batch_emb = embed_last4_mean(batch)
        else:
            raise ValueError("Unknown method")
        all_embs.append(batch_emb)
        if (i+1) % 10 == 0 or (i+1) == num_batches:
            print(f"[{method}] processed batch {i+1}/{num_batches} rows {start}:{end}")
    return np.vstack(all_embs)

# compute both embeddings (same text order)
print("Computing mean-last embeddings...")
emb_meanlast = compute_embeddings_for_texts(texts, BATCH_SIZE, method="mean_last")
print("Computing last4-mean embeddings...")
emb_last4mean = compute_embeddings_for_texts(texts, BATCH_SIZE, method="last4_mean")

print("Shapes:", emb_meanlast.shape, emb_last4mean.shape)

# save to disk
np.save(OUT_MEANLAST_NPY, emb_meanlast)
np.save(OUT_LAST4MEAN_NPY, emb_last4mean)
print("Saved:", OUT_MEANLAST_NPY, OUT_LAST4MEAN_NPY)

# ---------------- comparison helper ----------------
def compare_search(query, emb_a, emb_b, top_k=5):
    """
    emb_a, emb_b: numpy arrays (n, d) rows must correspond to same texts order.
    Prints top_k results for each.
    """
    # ensure L2-normalized rows (they already should be)
    A = emb_a / (np.linalg.norm(emb_a, axis=1, keepdims=True) + 1e-12)
    B = emb_b / (np.linalg.norm(emb_b, axis=1, keepdims=True) + 1e-12)

    # embed query using last4-mean pipeline so both are comparable (you can swap)
    inputs = tokenizer(query, truncation=True, return_tensors="pt")
    inputs = {k: v.to(device) for k, v in inputs.items()}
    with torch.no_grad():
        outputs = model(**inputs, output_hidden_states=True, return_dict=True)
    # query embeddings for each method:
    # - mean-last: use last_hidden_state and mean-pool tokens
    q_last = mean_pool_tokens_from_hidden(outputs.last_hidden_state, inputs["attention_mask"]).squeeze(0).cpu().numpy()
    q_last = q_last / (np.linalg.norm(q_last) + 1e-12)

    # - last4-mean: average last4 layers then mean-pool tokens
    hs = outputs.hidden_states
    last4 = torch.stack(hs[-4:], dim=0).mean(dim=0)  # (1, seq_len, hidden)
    q_last4 = mean_pool_tokens_from_hidden(last4, inputs["attention_mask"]).squeeze(0).cpu().numpy()
    q_last4 = q_last4 / (np.linalg.norm(q_last4) + 1e-12)

    simsA = A.dot(q_last)     # similarity of query using mean-last embedding space
    simsB = B.dot(q_last4)    # similarity of query using last4-mean embedding space

    idxA = np.argsort(-simsA)[:top_k]
    idxB = np.argsort(-simsB)[:top_k]

    print(f"\nTop {top_k} with mean-last:")
    for rank, idx in enumerate(idxA, 1):
        print(f"{rank}. idx={idx} score={simsA[idx]:.4f} title={df.loc[idx, TITLE_COL]!r} url={df.loc[idx, URL_COL]!r}")

    print(f"\nTop {top_k} with last4-mean:")
    for rank, idx in enumerate(idxB, 1):
        print(f"{rank}. idx={idx} score={simsB[idx]:.4f} title={df.loc[idx, TITLE_COL]!r} url={df.loc[idx, URL_COL]!r}")

# ---------- run a comparison example ----------
if __name__ == "__main__":
    sample_query = "American literature research guides"
    compare_search(sample_query, emb_meanlast, emb_last4mean, top_k=5)
    # you can change sample_query and re-run the script or import functions from here
