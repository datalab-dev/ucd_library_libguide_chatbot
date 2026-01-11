import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import os


os.environ["HF_HOME"] = "/dsl/libbot/data/huggingface_cache"
os.environ["TRANSFORMERS_CACHE"] = "/dsl/libbot/data/huggingface_cache"

# ---------- CONFIG ----------
# CSV_PATH = "/dsl/libbot/data/text_full_libguide.csv"
P_PATH = "/dsl/libbot/data/combined_text_full_libguide.parquet"
COMB_TEXT_COL = "combined_text"
MODEL_NAME = "jinaai/jina-embeddings-v3"
OUT_NPY = "/dsl/libbot/data/embeddings_jina_code.npy"
BATCH_SIZE = 16   # adjust if needed
# ----------------------------

# Load text data
df = pd.read_parquet(P_PATH)

# prepare texts to embed
texts = df[COMB_TEXT_COL].astype(str).tolist()

print("Rows to embed:", len(texts))


# Load model
model = SentenceTransformer(
    MODEL_NAME,
    trust_remote_code=True,
    )
print("Model loaded:", MODEL_NAME)

# Encode in batches
all_embs = model.encode(
    texts,
    task="retrieval.passage", # jina requires this task specifier
    batch_size=BATCH_SIZE,
    show_progress_bar=True,
    convert_to_numpy=True,
    normalize_embeddings=True
)

print("Embedding matrix shape:", all_embs.shape)

# Save embeddings
np.save(OUT_NPY, all_embs)
print("Saved embeddings to:", OUT_NPY)

