import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import os


# ---------- ENV ----------
os.environ["HF_HOME"] = "/dsl/libbot/data/huggingfce_cache"
os.environ["TRANSFORMERS_CACHE"] = "/dsl/libbot/data/huggingfce_cache"


# ---------- CONFIG ----------
CSV_PATH = "/dsl/libbot/data/plots_testing/prompt_texts_extended.csv"
TEXT_COL = "prompt_texts"
MODEL_NAME = "Qwen/Qwen3-Embedding-0.6B"
OUT_NPY = "/dsl/libbot/data/embeddings_testing_prompts_extended.npy"
BATCH_SIZE = 16
# ----------------------------

# Load CSV data
df = pd.read_csv(CSV_PATH)

# Prepare texts to embed
texts = df[TEXT_COL].astype(str).tolist()

print("Rows to embed:", len(texts))

# Load SentenceTransformer model
model = SentenceTransformer(
    MODEL_NAME,
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