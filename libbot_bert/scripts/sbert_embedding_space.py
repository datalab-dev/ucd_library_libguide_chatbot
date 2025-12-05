from sentence_transformers import SentenceTransformer, util
import pandas as pd
import numpy as np

# ---------- CONFIG ----------
CSV_PATH = "/dsl/libbot/data/text_full_libguide.csv"
TEXT_COL = "text"
MODEL_NAME = "https://huggingface.co/sentence-transformers/multi-qa-mpnet-base-cos-v1"
OUT_NPY = "/dsl/libbot/data/embeddings_sbert.npy"
BATCH_SIZE = 16   # adjust if needed
# ----------------------------

# Load text data
df = pd.read_csv(CSV_PATH)
texts = df[TEXT_COL].fillna("").astype(str).tolist()
print("Rows to embed:", len(texts))

# Load Sentence-BERT model
model = SentenceTransformer(MODEL_NAME)
print("Model loaded:", MODEL_NAME)

# Encode in batches
all_embs = model.encode(
    texts,
    batch_size=BATCH_SIZE,
    show_progress_bar=True,
    convert_to_numpy=True
)

print("Embedding matrix shape:", all_embs.shape)

# Save embeddings
np.save(OUT_NPY, all_embs)
print("Saved embeddings to:", OUT_NPY)
