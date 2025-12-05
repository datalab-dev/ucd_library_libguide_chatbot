import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer

# ---------- CONFIG ----------
CSV_PATH = "/dsl/libbot/data/text_full_libguide.csv"
TEXT_COL = "text"
MODEL_NAME = "sentence-transformers/multi-qa-mpnet-base-cos-v1"
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




# import numpy as np
# import pandas as pd
# import torch
# from transformers import AutoTokenizer, AutoModel


# # ---------- CONFIG ----------
# CSV_PATH = "/dsl/libbot/data/text_full_libguide.csv"
# EMB_PATH = "/dsl/libbot/data/embeddings_sbert.npy"
# MODEL_NAME = "sentence-transformers/multi-qa-mpnet-base-cos-v1"
# # ----------------------------



# # Mean Pooling - average the token embeddings
# def mean_pooling(model_output, attention_mask):
#     token_embeddings = model_output.last_hidden_state
#     mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
#     return torch.sum(token_embeddings * mask_expanded, 1) / torch.clamp(mask_expanded.sum(1), min=1e-9)


# if __name__ == "__main__":
#     print("Loading CSV...")
#     df = pd.read_csv(CSV_PATH)

#     # Assumes your text column is the FIRST column; change if needed
#     texts = df.iloc[:, 0].astype(str).tolist()

#     print("Loading model:", MODEL_NAME)
#     tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
#     model = AutoModel.from_pretrained(MODEL_NAME)

#     print("Encoding", len(texts), "rows...")

#     all_embeddings = []
#     batch_size = 16  # low for safety; increase to 32–64 if GPU available

#     for i in range(0, len(texts), batch_size):
#         batch = texts[i : i + batch_size]

#         enc = tokenizer(batch, padding=True, truncation=True, return_tensors="pt")

#         with torch.no_grad():
#             output = model(**enc, return_dict=True)

#         embeddings = mean_pooling(output, enc["attention_mask"])
#         all_embeddings.append(embeddings.cpu().numpy())

#         if i % 200 == 0:
#             print(f"Encoded {i}/{len(texts)} rows...")

#     all_embeddings = np.vstack(all_embeddings)
#     print("Final embedding shape:", all_embeddings.shape)

#     print("Saving to:", EMB_PATH)
#     np.save(EMB_PATH, all_embeddings)

#     print("Done.")
