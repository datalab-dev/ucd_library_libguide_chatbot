# In Python with Ollama's Python library
import ollama
import numpy as np
from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim

MODEL_NAME = "mixedbread-ai/mxbai-embed-large-v1"


# Get embeddings from Ollama
response = ollama.embeddings(
    model='mxbai-embed-large',
    prompt='CMN course'
)
ollama_emb = np.array(response['embedding'], dtype=np.float32)

# Compare with your Sentence Transformers versions
model = SentenceTransformer(MODEL_NAME, trust_remote_code=True)

# Test different prompt configurations
emb_no_prompt = model.encode("CMN course", normalize_embeddings=True)
emb_with_query = model.encode("CMN course", prompt_name="query", normalize_embeddings=True)
emb_with_passage = model.encode("CMN course", prompt_name="passage", normalize_embeddings=True)

# Compare all to Ollama
print("No prompt vs Ollama:", cos_sim(emb_no_prompt, ollama_emb).item())
print("Query prompt vs Ollama:", cos_sim(emb_with_query, ollama_emb).item())
print("Passage prompt vs Ollama:", cos_sim(emb_with_passage, ollama_emb).item())