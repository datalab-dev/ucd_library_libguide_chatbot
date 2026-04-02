import torch
from transformers import AutoTokenizer, AutoModel
import pandas as pd
import numpy as np
import os
import math


# Directs where hugging face downloads the model (run in CLI)
# export HF_HOME=/dsl/libbot/data/huggingface_cache/ 



# ====== CONFIG ====================
CSV_PATH = "/dsl/libbot/data/text_full_libguide.csv"
TEXT_COL = "text"                           # text column in df
BERT_CHECKPOINT = "bert-large-cased"
BATCH_SIZE = 16                             # how many rows processed at once

SAVE_CSV_PATH = "/dsl/libbot/data/embeddings_bert_meanpool.csv"
SAVE_NPY_PATH = "/dsl/libbot/data/embeddings_bert_meanpool.npy"

# ==================================




# ------------- Load data ----------
df = pd.read_csv(CSV_PATH, encoding='utf-8')
text_chunks = df[TEXT_COL].fillna("").astype(str).tolist()
num_rows, num_cols = df.shape
n = len(text_chunks)
print("Rows to embed:", n) # logging
# ----------------------------------




# ------------------ Device and model -------------------
# loading tokenizer, model, and moving model to device (on server)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("Moved model to", device)
tokenizer = AutoTokenizer.from_pretrained(BERT_CHECKPOINT)
bert_model = AutoModel.from_pretrained(BERT_CHECKPOINT).to(device)
bert_model.eval() #model in evaluation mode
# ------------------------------------------------------




# ---------- Mean pooling ----------
# Compute mean-pooled sentence embeddings from token embeddings.
# had some help from chatgpt

def mean_pool(last_hidden, attention_mask):
    """
    last_hidden: (batch, seq_len, hidden) --> last layer embeddings
    attention_mask: (batch, seq_len) --> identifies padding
    returns: (batch, hidden) --> tensor of mean embeddings 
    """
    
    # getting an attention mask to be shaped (unsqueezed) like the last layer of embeddings, again, for checking where the padding is
    attn = attention_mask.unsqueeze(-1).expand(last_hidden.size()).float()
    
    # multiply embeddings by the mask -> zeros out padding token vectors
    sum_hidden = (last_hidden * attn).sum(dim=1)

    # count how many real tokens per batch
    token_counts = attn.sum(dim=1) # dim=1 has a shape (batch, hidden)

    # avoid division by zero in case of empty sequence
    token_counts = torch.clamp(token_counts, min=1e-9)

    # dividing summed embeddings by number of real tokens -> mean pooling
    return sum_hidden / token_counts


# ----------------- batch processing  -----------------
all_embeddings = []                     # list to collect (batch, hidden) numpy arrays
num_batches = math.ceil(n / BATCH_SIZE) # we're essentially splitting up the processing by 16 batches (over the ~7000 rows)

# again, like in the testing file, no gradients are needed because we're not training anything
with torch.no_grad():
    for i in range(num_batches):
        start = i * BATCH_SIZE
        end = min(start + BATCH_SIZE, n)
        batch_texts = text_chunks[start:end]   # list of strings for this batch

        # Tokenize: padding=True pads to the longest sequence in the current batch.
        # truncation=True ensures sequences longer than model max length are cut.
        inputs = tokenizer(
            batch_texts,
            padding=True,
            truncation=True,
            return_tensors="pt"
        )

        # move token tensors (input_ids, attention_mask, etc.) to the model device (GPU/CPU)
        inputs = {k: v.to(device) for k, v in inputs.items()}

        # forward pass to get last_hidden_state (token embeddings)
        outputs = bert_model(**inputs, output_hidden_states=False, return_dict=True)
        last_hidden = outputs.last_hidden_state         # (batch, seq_len, hidden)
        attention_mask = inputs["attention_mask"]       # (batch, seq_len)

        # compute mean-pooled embeddings (batch, hidden)
        batch_emb = mean_pool(last_hidden, attention_mask)

        # move to CPU and convert to numpy arrays
        batch_emb_np = batch_emb.cpu().numpy()
        all_embeddings.append(batch_emb_np)

        # logging progress
        if (i + 1) % 10 == 0 or (i + 1) == num_batches:
            print(f"Processed batch {i+1}/{num_batches}  rows {start}:{end}")

# stack all batches into one matrix of shape (n, hidden); ncols is length of an embedding
emb_matrix = np.vstack(all_embeddings)
print("Embeddings matrix shape:", emb_matrix.shape)  # expect (num_rows, hidden_size)
# ----------------------------------------------------------


# ---------------- saving df ---------------------------
np.save(SAVE_NPY_PATH, emb_matrix)
print("Saved .npy to:", SAVE_NPY_PATH)

# saving as CSV just in case?
hidden_dim = emb_matrix.shape[1]
col_names = [f"emb_{j}" for j in range(hidden_dim)]
emb_df = pd.DataFrame(emb_matrix, columns=col_names)
emb_df.to_csv(SAVE_CSV_PATH, index=False)
print("Saved CSV to:", SAVE_CSV_PATH)
# ----------------------------------------------------------
