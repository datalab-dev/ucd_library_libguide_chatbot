from sentence_transformers import SentenceTransformer
import torch

MODEL_NAME = "mixedbread-ai/mxbai-embed-large-v1"

model = SentenceTransformer(MODEL_NAME, trust_remote_code=True)

# Check model info
print("Model config:")
print(model[0].auto_model.config)

# Get first layer weights as a fingerprint
first_layer_weights = model[0].auto_model.embeddings.word_embeddings.weight
print(f"\nFirst layer shape: {first_layer_weights.shape}")
print(f"First layer mean: {first_layer_weights.mean().item()}")
print(f"First layer std: {first_layer_weights.std().item()}")
print(f"First 5 values: {first_layer_weights[0, :5]}")

# Check where the model was loaded from
print(f"\nModel loaded from: {model._model_card_vars}")