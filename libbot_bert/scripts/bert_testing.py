import torch
from transformers import AutoTokenizer, AutoModel
import pandas as pd
import numpy as np
import torch.nn.functional as F


# Directs where hugging face downloads the model (run in CLI)
# export HF_HOME=/dsl/libbot/data/huggingface_cache/ 



# ====== DATA ====================
CSV_PATH = "/dsl/libbot/data/text_full_libguide.csv"
text_col = "text"


df = pd.read_csv(CSV_PATH)
num_rows, num_cols = df.shape

print(num_rows, num_cols)

# ============ CONFIG ============
BERT_CHECKPOINT = "bert-base-uncased"

# loading tokenizer, model, and moving model to device (on server)
tokenizer = AutoTokenizer.from_pretrained(BERT_CHECKPOINT)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("Moved model to", device)

bert_model = AutoModel.from_pretrained(BERT_CHECKPOINT)
bert_model.to(device)
bert_model.eval() #model in evaluation mode


# ============ TESTING ============

# INPUT
text_chunk = df.loc[0, "text"]
inputs = tokenizer(
    text_chunk, return_tensors = "pt", truncation=True, padding=True)

"""
Context manager => will keep the model from collecting gradients when it processes.
Unless you are training a model or trying understand model internals, there’s no need for gradients.
With the context manager built, send the inputs to the model.

NOTE TO SELF:
'with': = “do this inside a special mode, then exit the mode when done.”
** is the keyword argument unpacker (takes a dictionary, unpacks the key pairs)
"""
with torch.no_grad(): #no gradient calculation, because we're not training
    outputs = bert_model(**inputs, output_hidden_states=False, return_dict=True)


"""
The pooler_output tensor corresponds to the hidden state of the [CLS] token.
Uses it as a summary representation of the entire sequence of text.

However, want to work with last_hidden_state pool actually. Gives you all token embeddings.
Then we do mean pooling over this last layer to get an average of token embeddings (smooth out noise).

Also remember to set the attention mask, which tells you where padding tokens are, so that we can
ignore these when averaging to get the mean pooling (can get the true mean of actual text tokens only).
Then we essentially multiply output by the mask. Every real token (with a mask of 1) keeps its embedding,
every padding token (with a mask of 0) becomes a vector of zeros.

We still retain the shape of the tensors though -> (batch_size, seq_len, hidden_size)


hidden state size = embedding dimensionality
"""

last_hidden = outputs.last_hidden_state
attention_mask = inputs["attention_mask"]

"""
Mean pooling:
1) unsqueeze(-1) -> make mask match the embedding/tensor shape
2) * -> multiply by the attention mask to zero out padding embeddings
3) .sum(dim=1) -> sum the embeddings with the real tokens
4) divide by this attention_mask sum -> divide by number of real tokens to get the mean
"""
mean_emb = (last_hidden * attention_mask.unsqueeze(-1)).sum(dim=1) / attention_mask.sum(dim=1, keepdim=True)

# remove the batch dimension from the tensor mean_emb -> turns into a 1D tensor that only contains the embeddings
mean_emb = mean_emb.squeeze(0)



# CONVERT TO NUMPY (for easy storage of embeddings in pandas df)
mean_emb_np = mean_emb.cpu().numpy()


# adding the array into a new df
emb_df = pd.DataFrame([mean_emb_np])
print(emb_df)

# # later can stack the embeddings into a matrix
# # X = np.stack(df_new["embedding"].values)  # shape: (num_texts, 768)


