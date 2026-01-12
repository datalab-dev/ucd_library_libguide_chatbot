import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import torch
import os
import psutil
import time

# Set environment variables
os.environ["HF_HOME"] = "/dsl/libbot/data/huggingface_cache"
os.environ["TRANSFORMERS_CACHE"] = "/dsl/libbot/data/huggingface_cache"

# ---------- CONFIG ----------
P_PATH = "/dsl/libbot/data/combined_text_full_libguide.parquet"
COMB_TEXT_COL = "combined_text"
MODEL_NAME = "Qwen/Qwen3-Embedding-4B"
OUT_NPY = "/dsl/libbot/data/4B_embeddings_qwen.npy"

# OPTIMIZED FOR HARDWARE (144 threads, 103GB available RAM)
BATCH_SIZE = 128        
TORCH_THREADS = 16      

# set PyTorch thread count
torch.set_num_threads(TORCH_THREADS)
# ----------------------------

# Load text data
df = pd.read_parquet(P_PATH)

# prepare texts to embed
texts = df[COMB_TEXT_COL].astype(str).tolist()


print(f"Rows to embed: {len(texts):,}")

# Load Sentence-BERT model
print(f"\nLoading model: {MODEL_NAME}")
start_time = time.time()

model = SentenceTransformer(
    MODEL_NAME,
    device="cpu",
    model_kwargs={
        "torch_dtype": torch.float32,
        "low_cpu_mem_usage": True,
    },
    tokenizer_kwargs={"padding_side": "left"}
)


all_embs = model.encode(
    texts,
    batch_size=BATCH_SIZE,
    show_progress_bar=True,
    convert_to_numpy=True,
    normalize_embeddings=True,
)


print(f"Embedding matrix shape: {all_embs.shape}")

# Save embeddings
print(f"\nSaving embeddings to: {OUT_NPY}")
np.save(OUT_NPY, all_embs)
print("Embeddings saved successfully!")

# Final stats
print("\n" + "="*60)
print("SUMMARY")
print("="*60)
print(f"Total texts processed: {len(texts):,}")
print(f"Embedding dimension: {all_embs.shape[1]}")
print(f"Output file size: {os.path.getsize(OUT_NPY) / (1024**2):.2f} MB")
