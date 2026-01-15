from pymilvus import MilvusClient, DataType
import numpy as np

# ---------- CONFIG ----------
P_PATH = "/dsl/libbot/data/combined_text_full_libguide.parquet"
LARGE_EMB_PATH = "/dsl/libbot/data/4B_embeddings_qwen.npy"

LIB_TITLE_COL = "libguide_title"
TITLE_COL = "chunk_title"
TEXT_COL = "text"
URL_COL = "libguide_url"

# Define your collection schema
COLLECTION_NAME = "libguide_embeddings"
DIMENSION = 1024  # Change this to match your embeddings

# -----------------------------

# Initialize Milvus Lite (stores data locally in a file)
client = MilvusClient("/dsl/libbot/data/milvus/milvus_demo.db")



# Create collection if it doesn't exist
if client.has_collection(collection_name=COLLECTION_NAME):
    client.drop_collection(collection_name=COLLECTION_NAME)

client.create_collection(
    collection_name=COLLECTION_NAME,
    dimension=DIMENSION,
    metric_type="COSINE",  # or "IP" for inner product, "L2" for Euclidean
    auto_id=False
)

# Load your embeddings
embeddings = np.load("your_embeddings.npy")  # Shape: (7300, 1024)

# Prepare your data
# You'll need IDs and any metadata you want to store
data = []
for i, embedding in enumerate(embeddings):
    data.append({
        "id": i,  # or use your existing document IDs
        "vector": embedding.tolist(),
        # Add any metadata fields here:
        # "text": your_documents[i],
        # "title": your_titles[i],
    })

# Insert data in batches (Milvus handles batches well)
BATCH_SIZE = 1000
for i in range(0, len(data), BATCH_SIZE):
    batch = data[i:i + BATCH_SIZE]
    client.insert(
        collection_name=COLLECTION_NAME,
        data=batch
    )

print(f"Inserted {len(data)} documents into Milvus")