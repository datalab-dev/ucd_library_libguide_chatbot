import torch
from transformers import AutoTokenizer, AutoModel
import pandas as pd

# This directs where hugging face downloads the model
# export HF_HOME=/dsl/libbot/data/huggingface_cache/ 




df = pd.read_csv("/dsl/libbot/data/text_full_libguide.csv")
num_rows, num_cols = df.shape

checkpoint = "bert-base-uncased"

# loading tokenizer, model, and moving model to device (on server)
tokenizer = AutoTokenizer.from_pretrained(checkpoint)
device = 0 if torch.cuda.is_available() else "cpu"
print("Moved model to", device)
bert_model = AutoModel.from_pretrained(checkpoint, device = device)

bert_model.eval() #model in evaluation mode



# INPUT
inputs = tokenizer(
    sentence, return_tensors = "pt", return_attention_mask = True
)


"""
Context manager => will keep the model from collecting gradients when it processes.
Unless you are training a model or trying understand model internals, there’s no need for gradients.
With the context manager built, send the inputs to the model.
"""
with torch.no_grad():
    outputs = bert_model(**inputs, output_hidden_states = True)




