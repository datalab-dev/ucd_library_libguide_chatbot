import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import torch
import os


os.environ["HF_HOME"] = "/dsl/libbot/data/huggingfce_cache"
os.environ["TRANSFORMERS_CACHE"] = "/dsl/libbot/data/huggingfce_cache"


# ---------- CONFIG ----------
# CSV_PATH = "/dsl/libbot/data/text_full_libguide.csv"
P_PATH = "/dsl/libbot/data/combined_text_full_libguide.parquet"
COMB_TEXT_COL = "combined_text"
MODEL_NAME = "Qwen/Qwen3-Embedding-4B"
OUT_NPY = "/dsl/libbot/data/4B_embeddings_qwen.npy"
BATCH_SIZE = 16   # adjust if needed
# ----------------------------

# Load text data
df = pd.read_parquet(P_PATH)

# prepare texts to embed
texts = df[COMB_TEXT_COL].astype(str).tolist()


print("Rows to embed:", len(texts))

# Load Sentence-BERT model
model = SentenceTransformer(
    MODEL_NAME,
    device="cpu",
    model_kwargs={
        "torch_dtype": torch.float32,
        "attn_implementation": "sdpa",
        "low_cpu_mem_usage": True,
    },
    tokenizer_kwargs={"padding_side": "left"}
)

print("Model loaded:", MODEL_NAME)

# Encode in batches
all_embs = model.encode(
    texts,
    batch_size=BATCH_SIZE,
    show_progress_bar=True,
    convert_to_numpy=True,
    normalize_embeddings=True
)

print("Embedding matrix shape:", all_embs.shape)

# Save embeddings
np.save(OUT_NPY, all_embs)
print("Saved embeddings to:", OUT_NPY)

