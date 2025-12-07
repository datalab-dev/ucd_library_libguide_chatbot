import torch
import numpy as np
import pandas as pd
import sys
from transformers import AutoTokenizer, AutoModel

# ================================
# CONFIG — update to your paths
# ================================
MEANLAST_PATH = "/dsl/libbot/data/embeddings_bert_meanpool.npy"
LAST4MEAN_PATH = "/dsl/libbot/data/embeddings_last4_meanpool.npy"
CSV_PATH = "/dsl/libbot/data/text_full_libguide.csv"
TEXT_COL = "text"
TITLE_COL = "chunk_title"
URL_COL = "libguide_url"
MODEL_NAME = "bert-large-cased"

# ======================================================
# Load embeddings & dataframe
# ======================================================
emb_meanlast = np.load(MEANLAST_PATH)
emb_last4mean = np.load(LAST4MEAN_PATH)
df = pd.read_csv(CSV_PATH)

n1, d1 = emb_meanlast.shape
n2, d2 = emb_last4mean.shape
assert n1 == n2, "Number of rows in the two embedding matrices should match."
n = n1
print("Loaded embeddings:", emb_meanlast.shape, emb_last4mean.shape)

# ======================================================
# Load model + tokenizer
# ======================================================
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModel.from_pretrained(MODEL_NAME, output_hidden_states=True).to(device)
model.eval()

# ======================================================
# Helper: mean pooling
# ======================================================
def mean_pool_tokens_from_hidden(last_hidden, attention_mask):
    mask = attention_mask.unsqueeze(-1).expand(last_hidden.size()).float()
    summed = (last_hidden * mask).sum(dim=1)
    denom = mask.sum(dim=1).clamp(min=1e-9)
    return summed / denom

# ======================================================
# Comparison function
# ======================================================
def compare_search(query, emb_a, emb_b, top_k=5):
    # L2 normalize row-wise
    A = emb_a / (np.linalg.norm(emb_a, axis=1, keepdims=True) + 1e-12)
    B = emb_b / (np.linalg.norm(emb_b, axis=1, keepdims=True) + 1e-12)

    # embed query using both pipelines
    inputs = tokenizer(query, truncation=True, return_tensors="pt").to(device)

    with torch.no_grad():
        outputs = model(**inputs, return_dict=True)
        hs = outputs.hidden_states  # tuple of 25 layers

    # ---- mean-last ----
    last = outputs.last_hidden_state
    q_last = mean_pool_tokens_from_hidden(last, inputs["attention_mask"]).squeeze(0)
    q_last = q_last.cpu().numpy()
    q_last = q_last / (np.linalg.norm(q_last) + 1e-12)

    # ---- last4-mean ----
    last4 = torch.stack(hs[-4:], dim=0).mean(dim=0)
    q_last4 = mean_pool_tokens_from_hidden(last4, inputs["attention_mask"]).squeeze(0)
    q_last4 = q_last4.cpu().numpy()
    q_last4 = q_last4 / (np.linalg.norm(q_last4) + 1e-12)

    simsA = A.dot(q_last)
    simsB = B.dot(q_last4)

    idxA = np.argsort(-simsA)[:top_k]
    idxB = np.argsort(-simsB)[:top_k]

    print(f"\n===== QUERY: {query!r} =====")

    print(f"\nTop {top_k} using mean-last:")
    for r, idx in enumerate(idxA, 1):
        print(f"{r}. idx={idx} score={simsA[idx]:.4f} title={df.loc[idx, TITLE_COL]!r} url={df.loc[idx, URL_COL]!r}")

    print(f"\nTop {top_k} using last4-mean:")
    for r, idx in enumerate(idxB, 1):
        print(f"{r}. idx={idx} score={simsB[idx]:.4f} title={df.loc[idx, TITLE_COL]!r} url={df.loc[idx, URL_COL]!r}")


# ======================================================
# CLI usage
# ======================================================
if __name__ == "__main__":
    # sys.argv[0] = script name
    # sys.argv[1:] = list of queries

    if len(sys.argv) < 2:
        print("Usage: python search.py \"your query here\" [more queries...]")
        sys.exit(1)

    queries = sys.argv[1:]

    for q in queries:
        compare_search(q, emb_meanlast, emb_last4mean, top_k=5)
