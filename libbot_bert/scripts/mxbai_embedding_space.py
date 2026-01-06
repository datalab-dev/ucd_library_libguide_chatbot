import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import os


os.environ["HF_HOME"] = "/dsl/libbot/data/huggingface_cache"
os.environ["TRANSFORMERS_CACHE"] = "/dsl/libbot/data/huggingface_cache"


# ---------- CONFIG ----------
CSV_PATH = "/dsl/libbot/data/text_full_libguide.csv"
TEXT_COL = "text"
LIB_TITLE_COL = "libguide_title"
MODEL_NAME = "mixedbread-ai/mxbai-embed-large-v1"
OUT_NPY = "/dsl/libbot/data/embeddings_mxbai.npy"
BATCH_SIZE = 16   # adjust if needed
# ----------------------------

# Load text data
df = pd.read_csv(CSV_PATH, encoding='utf-8')

# prepare texts + titles to embed
lib_titles = df[LIB_TITLE_COL].fillna("").astype(str).tolist()
text_chunks = df[TEXT_COL].fillna("").astype(str).tolist()

texts = []   # combined strings

for i in range(len(df)):
    title = lib_titles[i]
    text_chunk = text_chunks[i]

    if title.strip() == "":
        combined = text_chunk
    else:
        combined = title + ": " + text_chunk

    texts.append(combined)


print("Rows to embed:", len(texts))

# Load Sentence-BERT model
model = SentenceTransformer(MODEL_NAME)
print("Model loaded:", MODEL_NAME)

# Encode in batches
all_embs = model.encode(
    texts,
    prompt_name="passage",
    batch_size=BATCH_SIZE,
    show_progress_bar=True,
    convert_to_numpy=True,
    normalize_embeddings = True
)

print("Embedding matrix shape:", all_embs.shape)

# Save embeddings
np.save(OUT_NPY, all_embs)
print("Saved embeddings to:", OUT_NPY)

