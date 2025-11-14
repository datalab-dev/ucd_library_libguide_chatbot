import torch
from transformers import AutoTokenizer, AutoModel
import pandas as pd

df = pd.read_csv("/dsl/libbot/data/text_full_libguide.csv")

checkpoint = "google-bert/bert-base-uncased"

tokenizer = AutoTokenizer.from_pretrained(checkpoint)
bert = AutoModel.from_pretrained(checkpoint)

sentence = "Then I tried to find some way of embracing my mother's ghost."

inputs = tokenizer(inputs, return_tensors = "pt", return_attention_mask = True, padding = "longest"
)