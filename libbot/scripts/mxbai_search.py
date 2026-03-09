import sys
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim, dot_score


# ---------- CONFIG ----------
CSV_PATH = "/dsl/libbot/data/text_full_libguide.csv"
EMB_PATH = "/dsl/libbot/data/embeddings_mxbai.npy"
TEXT_COL = "text"
TITLE_COL = "chunk_title"
LIB_TITLE_COL = "libguide_title"
URL_COL = "libguide_url"
MODEL_NAME = "mixedbread-ai/mxbai-embed-large-v1"
TOP_K = 3
# ----------------------------



def semantic_search(query, df, embeddings, model, top_k=TOP_K):
    # encode query
    query_emb = model.encode(
        query,
        normalize_embeddings=True,
        convert_to_numpy=True)

    # compute cosine similarity for all rows
    # util.cos_sim treats the first argument as a batch of 1 vector, so it interprets it as (1, 768)
    # so does the comparison with all the different embeddings
    scores = dot_score(query_emb, embeddings)[0].cpu().numpy() # util.cos_sim returns a PyTorch tensor ==> .numpy() can only be called on a CPU tensor


    # produces a list of row numbers, sorted by similarity
    top_idx = np.argsort(-scores)[:top_k]


    # making list of dictionaries
    # each dictionary is one of the top k returned texts, including title and url
    results = []
    for idx in top_idx:
        row = df.iloc[idx]
        results.append({
            "score": float(scores[idx]),
            "text": row[TEXT_COL],
            "libguide_title": row[LIB_TITLE_COL],
            "title": row[TITLE_COL],
            "url": row[URL_COL]
        })
    return results


if __name__ == "__main__":
    # --- get the prompt from the user ---
    if len(sys.argv) < 2:
        print("Usage: python search.py \"your query here\"")
        sys.exit(1)

    query = sys.argv[1]
    print(f"Query: {query}\n")

    # --- load resources ---
    print("Loading dataframe...")
    df = pd.read_csv(CSV_PATH, encoding='utf-8')

    print("Loading embeddings...")
    embeddings = np.load(EMB_PATH)

    print("Loading model:", MODEL_NAME)
    model = SentenceTransformer(MODEL_NAME, trust_remote_code=True)

    # --- perform search ---
    results = semantic_search(query, df, embeddings, model)

    # --- print results ---
    print("\nTop results:\n")
    for i, r in enumerate(results, 1): #loop through results (dictionaries) and give a counter for each starting at 1 (stored in i)
        print(f"----- Result {i} -----")
        print(f"Score: {r['score']:.4f}")
        print(f"Title: {r['title']}")
        print(f"Libguide: {r['libguide_title']}")
        print(f"URL:   {r['url']}")
        print("Text:")
        print(r["text"])
        print()
