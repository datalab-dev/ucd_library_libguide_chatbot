import numpy as np
import pandas as pd
import torch
from transformers import AutoTokenizer, AutoModel, logging
import os
import sys

logging.set_verbosity_error()

# -------- CONFIG (change paths if needed) --------
EMB_PATH = "/dsl/libbot/data/embeddings_last4_meanpool.npy"
CSV_PATH     = "/dsl/libbot/data/text_full_libguide.csv"
TEXT_COL     = "text"
TITLE_COL    = "chunk_title" 
URL_COL      = "libguide_url"
MODEL_NAME = "bert-large-cased"
TOP_K = 3
# ------------------------------------------------

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# ------------------------------------------------
# L2 normalization of rows removes magnitude so we only compare direction (semantic direction)
# and because cosine similarity is a NORMALIZED dot product
# NOTE: L2 normalization is basically about scaling a vector so that all that matters is
# direction, not lenght (as you are essentially placing the vector in the unit sphere)
#  --> keep in mind LLAMA-based embedding models already normalize the output vectors INTERNALLY

emb_matrix = np.load(EMB_PATH)
emb_norms = np.linalg.norm(emb_matrix, axis=1, keepdims=True)
emb_norms = np.clip(emb_norms, 1e-9, None)  # clipping norms that are too small (ensuring no vector has a norm 0)
emb_matrix_normed = emb_matrix / emb_norms            # (n, dim) --> unit vector length

df = pd.read_csv(CSV_PATH) # loading text df
# ------------------------------------------------


# load model + tokenizer
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModel.from_pretrained(MODEL_NAME, output_hidden_states=True).to(device)
model.eval()


# ---------- embed a single query text  ----------
def embed_query(text: str) -> np.ndarray:
    """
    Compute a mean-pooled embedding for the input text and return a L2-normalized numpy vector.
    Uses the same model + pooling logic used to create stored embeddings.
    """

    with torch.no_grad():
        outputs = model(**inputs)
        hidden = outputs.hidden_states[-4:]    # list of 4 tensors
        stacked = torch.stack(hidden).mean(0)  # (1, seq, dim)

    mask = inputs["attention_mask"].unsqueeze(-1).float()
    pooled = (stacked * mask).sum(1) / mask.sum(1)
    emb = pooled.squeeze(0).cpu().numpy()

    norm = np.linalg.norm(emb)
    return emb / max(norm, 1e-9)

# ---------- search function ----------
def search(query, k=TOP_K) -> pd.DataFrame:
    """
    Query the embedding index and return a df with top-k results.
    Columns returned: ['chunk_title','libguide_url','text','score'] sorted by descending score
    """
    q = embed_query(query)
    
    sims = emb_matrix_normed @ q
    idx = np.argsort(-sims)[:k]
    scores = sims[idx]

    out = df.loc[idx, [TITLE_COL, URL_COL, TEXT_COL]].copy()
    out["score"] = scores
    return out.sort_values("score", ascending=False).reset_index(drop=True)
    

# ---------- output  ----------
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python search_testing.py \"your query here\"")
        sys.exit(1)

    query = " ".join(sys.argv[1:])
    results = search(query)

    print(f"\nTop {len(results)} results for: {query}\n")
    for i, row in results.iterrows():
        print(f"{i+1}. score={row['score']:.4f}")
        print("   Title:", row[TITLE_COL])
        print("   URL:  ", row[URL_COL])
        print("   Text:", repr(row[TEXT_COL][:200]) + ("..." if len(row[TEXT_COL]) > 200 else ""))
        print()
