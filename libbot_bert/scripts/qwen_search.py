import sys
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer

# ---------- CONFIG ----------
CSV_PATH = "/dsl/libbot/data/combined_text_full_libguide.csv"
EMB_PATH = "/dsl/libbot/data/embeddings_qwen.npy"

LIB_TITLE_COL = "libguide_title"
TITLE_COL = "chunk_title"
TEXT_COL = "text"
URL_COL = "libguide_url"

MODEL_NAME = "Qwen/Qwen3-Embedding-0.6B"
TOP_K = 3
# ----------------------------

# filters out duplicates
def cleaned_semantic_search(query, df, embeddings, model, top_k=TOP_K):

    # encode query
    query_emb = model.encode(
        query,
        prompt_name="query",
        normalize_embeddings=True,
        convert_to_numpy=True)    
    
    # compute cosine similarity for all rows
    scores = np.dot(query_emb, embeddings.T)  # equivalent to cosine sim since embeddings are normalized


    # Get more candidates than needed to account for deduplication
    # Fetch 3x top_k as buffer (or all rows if corpus is small)
    candidate_count = min(top_k * 3, len(scores))
    top_idx = np.argsort(-scores)[:candidate_count]
    
    # Track seen texts and build deduplicated results
    seen_texts = set()
    results = []
    
    for idx in top_idx:
        row = df.iloc[idx]
        text = row[TEXT_COL]
        
        # Skip if we've already seen this exact text
        if text in seen_texts:
            continue
        
        seen_texts.add(text)
        results.append({
            "score": float(scores[idx]),
            "text": text,
            "title": row[TITLE_COL],
            "url": row[URL_COL],
            "libguide_title": row[LIB_TITLE_COL]
        })

        # Stop once we have enough unique results
        if len(results) == top_k:
            break
    
    return results


if __name__ == "__main__":
    # --- get the prompt from the user ---
    if len(sys.argv) < 2:
        print("Usage: python search.py \"your query here\"")
        sys.exit(1)

    query = sys.argv[1]
    print(f"\n\n\033[1;30mQuery:\033[0m {query}\n")

    # --- load resources ---
    print("\033[34mLoading dataframe...\033[0m")
    df = pd.read_csv(CSV_PATH, encoding='utf-8')

    print("\033[34mLoading embeddings...\033[0m")
    embeddings = np.load(EMB_PATH)

    print("\033[34mLoading model: \033[0m", MODEL_NAME)
    model = SentenceTransformer(
        MODEL_NAME,
        trust_remote_code=True)

    # --- perform search ---
    results = cleaned_semantic_search(query, df, embeddings, model)

    # --- print results ---
    print("\n\033[1;30mTop results:\033[0m\n")
    for i, r in enumerate(results, 1): #loop through results (dictionaries) and give a counter for each starting at 1 (stored in i)
        print(f"----- \033[1;32mResult {i} \033[0m-----")
        print(f"\033[32mScore: \033[0m{r['score']:.4f}")
        print(f"\033[32mLibguide: \033[0m{r['libguide_title']}")
        print(f"\033[32mTitle: \033[0m{r['title']}")
        print(f"\033[32mURL:   \033[0m{r['url']}")
        print("\033[32mText:\033[0m")
        print(r["text"])
        print()
