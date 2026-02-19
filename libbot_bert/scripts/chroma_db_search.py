import sys
import numpy as np
import chromadb
from sentence_transformers import SentenceTransformer
import torch

# ---------- CONFIG ----------
DB_PATH = "/dsl/libbot/data/chroma_db"
COLLECTION_NAME = "libguides"
MODEL_NAME = "Qwen/Qwen3-Embedding-0.6B"
TOP_K = 3

# set threads for faster querying
torch.set_num_threads(16)
# ----------------------------

# =============== DEDUPLICATION SEARCH FUNCTION ===============
# filters out duplicates and aggregates sources (because we still care about the different guides/sections)
def cleaned_semantic_search(base_query, collection, model, top_k=TOP_K):
    
    # Don't repeat query for 0.6B model
    query = base_query
    
    # encode query
    query_emb = model.encode(
        query,
        prompt_name="query",
        normalize_embeddings=True,
        convert_to_numpy=True
    )    
    
    # get enough candidates to ensure we have top_k unique texts
    # corpus has 70% duplicates, fetch top_k * 5 to be safe
    candidate_count = top_k * 5
    
    # Search ChromaDB
    results = collection.query(
        query_embeddings=[query_emb.tolist()],
        n_results=candidate_count,
        include=["metadatas", "distances"]
    )
    
    # group by text, keeping highest score and all sources; dictionary mapping text -> result + sources
    text_to_result = {}
    
    # ChromaDB returns results as lists
    metadatas = results['metadatas'][0]  # First query's metadata
    distances = results['distances'][0]  # First query's distances
    
    for metadata, distance in zip(metadatas, distances):
        text = metadata['text']
        # ChromaDB returns distance (lower is better), convert to similarity score
        # For cosine distance: similarity = 1 - distance
        score = 1 - distance
        
        if text not in text_to_result:
            # first time seeing this text - initialize
            text_to_result[text] = {
                "score": score,  # highest score (first encountered)
                "text": text,
                "sources": []
            }
        
        # Add this source (could be duplicate text from different guide)
        text_to_result[text]["sources"].append({
            "libguide_title": metadata['libguide_title'],
            "section_title": metadata['chunk_title'],
            "url": metadata['libguide_url']
        })
        
        # Stop once we have enough unique texts
        if len(text_to_result) >= top_k:
            break
    
    # Convert to list and sort by score
    final_results = sorted(
        text_to_result.values(), 
        key=lambda x: x["score"], 
        reverse=True
    )
    return final_results[:top_k]

# ============== MAIN  ==============
if __name__ == "__main__":
    # --- get the prompt from the user ---
    if len(sys.argv) < 2:
        print("Usage: python search.py \"your query here\"")
        sys.exit(1)
    
    base_query = sys.argv[1]
    print(f"\n\n\033[1;30mQuery:\033[0m {base_query}\n")
    
    # --- load resources ---
    print("\033[34mConnecting to ChromaDB database...\033[0m")
    client = chromadb.PersistentClient(path=DB_PATH)
    collection = client.get_collection(name=COLLECTION_NAME)
    
    print("\033[34mLoading model: \033[0m", MODEL_NAME)
    
    # QWEN-0.6B LOADING
    model = SentenceTransformer(
        MODEL_NAME,
        device="cpu",
        model_kwargs={
            "torch_dtype": torch.float32,
        },
        tokenizer_kwargs={"padding_side": "left"},
        trust_remote_code=True
    )
    
    # --- perform search ---
    results = cleaned_semantic_search(base_query, collection, model)
    
    # ---- print results with sources ----
    print("\n\033[1;30mTop results:\033[0m\n")
    for i, r in enumerate(results, 1):
        print(f"----- \033[1;32mRESULT {i} \033[0m-----")
        print(f"\033[32mScore: \033[0m{r['score']:.4f}")
        print(f"\033[32mText:\033[0m")
        print(r["text"])
        print(f"\n\033[32mFound in {len(r['sources'])} guide(s):\033[0m")
        for src in r['sources']:
            print(f"  • {src['libguide_title']} → {src['section_title']}")
            print(f"    {src['url']}")
        print()