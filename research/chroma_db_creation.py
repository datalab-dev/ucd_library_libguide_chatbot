import chromadb
from chromadb.config import Settings
import pandas as pd
import numpy as np

def migrate_to_chromadb(embeddings_path, metadata_path, db_path):
    """
    Migrate existing embeddings and metadata to ChromaDB
    
    Args:
        embeddings_path: Path to your .npy file (e.g., "data/embeddings.npy")
        metadata_path: Path to your parquet file
        db_path: Where to save the ChromaDB database (e.g., "./chroma_db")
    """
    # Load existing data
    print("Loading embeddings...")
    embeddings = np.load(embeddings_path)
    
    print("Loading metadata...")
    metadata_df = pd.read_parquet(metadata_path)
    
    # Verify alignment
    assert len(embeddings) == len(metadata_df), \
        f"Mismatch: {len(embeddings)} embeddings but {len(metadata_df)} metadata rows"
    
    print(f"Loaded {len(embeddings)} documents")
    print(f"Embedding dimension: {embeddings.shape[1]}")
    
    # Initialize ChromaDB
    client = chromadb.PersistentClient(path=db_path)
    
    # Drop existing collection if it exists
    try:
        client.delete_collection("libguides")
        print("Dropped existing collection...")
    except:
        pass
    
    # Create new collection
    print("Creating ChromaDB collection...")
    collection = client.create_collection(
        name="libguides",
        metadata={"hnsw:space": "cosine"}  # Use cosine similarity
    )
    
    # Prepare data for insertion
    print("Preparing data...")
    ids = []
    vectors = []
    metadatas = []
    
    for idx in range(len(embeddings)):
        row = metadata_df.iloc[idx]
        
        # ChromaDB requires string IDs
        ids.append(str(int(row['local_id'])))
        
        # Embeddings as list
        vectors.append(embeddings[idx].tolist())
        
        # Metadata - ChromaDB doesn't support None values well, so convert to strings
        metadata = {
            "parent_id": str(int(row['parent_id'])),
            "text": str(row['text']) if pd.notna(row['text']) else "",
            "libguide_title": str(row['libguide_title']) if pd.notna(row['libguide_title']) else "",
            "libguide_url": str(row['libguide_url']) if pd.notna(row['libguide_url']) else "",
            "chunk_title": str(row['chunk_title']) if pd.notna(row['chunk_title']) else "",
            "chunk_url": str(row['chunk_url']) if pd.notna(row['chunk_url']) else "",
            "external_url": str(row['external_url']) if pd.notna(row['external_url']) else "",
            "combined_text": str(row['combined_text']) if pd.notna(row['combined_text']) else "",
        }
        metadatas.append(metadata)
    
    # Insert in batches
    print("Inserting into ChromaDB...")
    BATCH_SIZE = 1000
    
    for i in range(0, len(ids), BATCH_SIZE):
        batch_ids = ids[i:i + BATCH_SIZE]
        batch_vectors = vectors[i:i + BATCH_SIZE]
        batch_metadatas = metadatas[i:i + BATCH_SIZE]
        
        collection.add(
            ids=batch_ids,
            embeddings=batch_vectors,
            metadatas=batch_metadatas
        )
        
        if (i + BATCH_SIZE) % 5000 == 0 or (i + BATCH_SIZE) >= len(ids):
            print(f"  Inserted {min(i + BATCH_SIZE, len(ids))}/{len(ids)} documents")
    
    print(f"\nMigration complete!")
    print(f"Database saved to: {db_path}")
    print(f"Collection name: libguides")
    print(f"Total documents: {len(ids)}")
    
    # Verify
    count = collection.count()
    print(f"Verification - Collection contains: {count} documents")

if __name__ == "__main__":
    migrate_to_chromadb(
        embeddings_path="/dsl/libbot/data/embeddings_qwen.npy",
        metadata_path="/dsl/libbot/data/combined_text_full_libguide.parquet",
        db_path="/dsl/libbot/data/chroma_db"
    )
