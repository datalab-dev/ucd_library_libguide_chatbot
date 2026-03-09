# Check if tokenizers produce the same output
from transformers import AutoTokenizer

MODEL_NAME = "mixedbread-ai/mxbai-embed-large-v1"

# Load tokenizer
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

test_text = "CMN course"
tokens = tokenizer.tokenize(test_text)
token_ids = tokenizer.encode(test_text)

print(f"Tokens: {tokens}")
print(f"Token IDs: {token_ids}")
print(f"Vocab size: {len(tokenizer)}")

# Now compare with what Ollama might be doing
# You can also test with the prompt prefix
prefixed = "Represent this sentence for searching relevant passages: " + test_text
tokens_prefixed = tokenizer.tokenize(prefixed)
print(f"\nWith prefix tokens: {tokens_prefixed}")