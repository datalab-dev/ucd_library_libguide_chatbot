import torch
from transformers import AutoTokenizer, AutoModel
import pandas as pd
import numpy as np
import math
import os

# ---------- CONFIG ----------
CSV_PATH = "/dsl/libbot/data/text_full_libguide.csv"
TEXT_COL = "text"
BERT_CHECKPOINT = "bert-large-cased"   # or another local checkpoint
BATCH_SIZE = 16                        # tune if OOM
NUM_ROWS = None                         # None -> process all rows
OUT_NPY = "/dsl/libbot/data/embeddings_last4_meanpool.npy"
OUT_CSV = "/dsl/libbot/data/embeddings_last4_meanpool.csv"  # optional wide CSV
# ----------------------------

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("Device:", device)

# load text data
df = pd.read_csv(CSV_PATH, encoding='utf-8')
if NUM_ROWS is None:
    texts = df[TEXT_COL].fillna("").astype(str).tolist()
else:
    texts = df[TEXT_COL].fillna("").astype(str).tolist()[:NUM_ROWS]
n = len(texts)
print("Rows to embed:", n)

# load tokenizer + model
tokenizer = AutoTokenizer.from_pretrained(BERT_CHECKPOINT)
model = AutoModel.from_pretrained(BERT_CHECKPOINT).to(device)
model.eval()

def mean_pool_tokens_from_hidden(last_hidden, attention_mask):
    attn = attention_mask.unsqueeze(-1).expand(last_hidden.size()).float()
    sum_hidden = (last_hidden * attn).sum(dim=1)
    token_counts = attn.sum(dim=1)
    token_counts = torch.clamp(token_counts, min=1e-9)
    return sum_hidden / token_counts

all_embs = []
num_batches = math.ceil(n / BATCH_SIZE)
with torch.no_grad():
    for i in range(num_batches):
        start = i * BATCH_SIZE
        end = min(start + BATCH_SIZE, n)
        batch_texts = texts[start:end]

        inputs = tokenizer(batch_texts, padding=True, truncation=True, return_tensors="pt")
        inputs = {k: v.to(device) for k, v in inputs.items()}

        outputs = model(**inputs, output_hidden_states=True, return_dict=True)
        hidden_states = outputs.hidden_states  # tuple: (embeddings, layer1, ..., layerN)

        last4 = torch.stack(hidden_states[-4:], dim=0).mean(dim=0)  # (batch, seq_len, hidden)
        batch_emb = mean_pool_tokens_from_hidden(last4, inputs["attention_mask"])  # (batch, hidden)
        batch_emb = torch.nn.functional.normalize(batch_emb, p=2, dim=1)        # L2 normalize rows

        all_embs.append(batch_emb.cpu().numpy())

        if (i+1) % 10 == 0 or (i+1) == num_batches:
            print(f"Processed batch {i+1}/{num_batches} rows {start}:{end}")

emb_matrix = np.vstack(all_embs)
print("Emb matrix shape:", emb_matrix.shape)

# save binary .npy
np.save(OUT_NPY, emb_matrix)
print("Saved .npy to:", OUT_NPY)

# optionally save wide CSV for inspection (can be large)
hidden_dim = emb_matrix.shape[1]
if n <= 20000:   # only produce CSV for reasonable sizes
    col_names = [f"emb_{j}" for j in range(hidden_dim)]
    emb_df = pd.DataFrame(emb_matrix, columns=col_names)
    emb_df.to_csv(OUT_CSV, index=False)
    print("Saved CSV to:", OUT_CSV)
