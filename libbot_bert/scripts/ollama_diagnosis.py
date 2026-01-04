import numpy as np
from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim
import ollama

MODEL_NAME = "mixedbread-ai/mxbai-embed-large-v1"

model = SentenceTransformer(MODEL_NAME, trust_remote_code=True)

# Test cases
test_queries = ["CMN course", "CMN", "communications course"]
test_doc = "This is about the Communications (CMN) department courses."


print("=== QUERY TESTS ===")
for query in test_queries:
    # Get Ollama embedding
    ollama_emb = np.array(ollama.embeddings(model='mxbai-embed-large', prompt=query)['embedding'], dtype=np.float32)
    
    # Get ST embeddings with different methods
    st_no_prompt = model.encode(query, normalize_embeddings=True)
    st_query_prompt = model.encode(query, prompt_name="query", normalize_embeddings=True)
    
    print(f"\nQuery: '{query}'")
    print(f"  ST (no prompt) vs Ollama: {cos_sim(st_no_prompt, ollama_emb).item():.4f}")
    print(f"  ST (query prompt) vs Ollama: {cos_sim(st_query_prompt, ollama_emb).item():.4f}")

print("\n=== DOCUMENT TEST ===")
ollama_doc = np.array(ollama.embeddings(model='mxbai-embed-large', prompt=test_doc)['embedding'], dtype=np.float32)
st_doc_no_prompt = model.encode(test_doc, normalize_embeddings=True)
st_doc_passage = model.encode(test_doc, prompt_name="passage", normalize_embeddings=True)

print(f"ST (no prompt) vs Ollama: {cos_sim(st_doc_no_prompt, ollama_doc).item():.4f}")
print(f"ST (passage prompt) vs Ollama: {cos_sim(st_doc_passage, ollama_doc).item():.4f}")