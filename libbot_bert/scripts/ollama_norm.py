# Test if normalization is the issue
import ollama
import numpy as np
from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim

MODEL_NAME = "mixedbread-ai/mxbai-embed-large-v1"
model = SentenceTransformer(MODEL_NAME, trust_remote_code=True)

query = "CMN"
doc = "Communications (CMN) department courses"

# Ollama embeddings
ollama_query = np.array(ollama.embeddings(model='mxbai-embed-large', prompt=query)['embedding'], dtype=np.float32)
ollama_doc = np.array(ollama.embeddings(model='mxbai-embed-large', prompt=doc)['embedding'], dtype=np.float32)

# ST embeddings WITHOUT normalization
st_query_raw = model.encode(query, normalize_embeddings=False)
st_doc_raw = model.encode(doc, normalize_embeddings=False)

# ST embeddings WITH normalization
st_query_norm = model.encode(query, normalize_embeddings=True)
st_doc_norm = model.encode(doc, normalize_embeddings=True)

# Check if Ollama normalizes
ollama_query_norm = np.linalg.norm(ollama_query)
ollama_doc_norm = np.linalg.norm(ollama_doc)
print(f"Ollama query L2 norm: {ollama_query_norm}")
print(f"Ollama doc L2 norm: {ollama_doc_norm}")

# Compare search results
print("\n=== Cosine Similarity Comparison ===")
print(f"Ollama: {np.dot(ollama_query, ollama_doc):.4f}")
print(f"ST (raw): {cos_sim(st_query_raw, st_doc_raw).item():.4f}")
print(f"ST (normalized): {cos_sim(st_query_norm, st_doc_norm).item():.4f}")