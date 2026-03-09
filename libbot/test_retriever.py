
# Verifying the libbot_pkg package is working correctly.

import json
import sys
from libbot_pkg import Retriever, settings, QueryResponse

if __name__ == "__main__":
    # --- get the prompt from the user ---
    if len(sys.argv) < 2:
        print("Usage: python test_retriever.py \"your query here\"")
        sys.exit(1)

    base_query = sys.argv[1]
    print(f"\n\033[1;30mQuery:\033[0m {base_query}\n")

    print("=== Config ===")
    print(f"  ChromaDB path:    {settings.chroma_db_path}")
    print(f"  Collection name:  {settings.collection_name}")
    print(f"  Model:            {settings.model_name}")
    print(f"  Top-K:            {settings.top_k}")

    # -------------------------------------------------------
    # loadin the retriever (connects to ChromaDB + loads model)

    print("\n=== Loading Retriever ===")
    retriever = Retriever()

    # -------------------------------------------------------
    # running test

    TOP_K = 3

    print(f"\n=== Running Test Query ===")
    print(f"  Query: \"{base_query}\"")
    print(f"  Top-K: {TOP_K}\n")

    results = retriever.search(query=base_query, top_k=TOP_K)

    # -------------------------------------------------------
    # results

    if not results:
        print("No results returned — check your ChromaDB collection has data.")
    else:
        for i, r in enumerate(results, 1):
            print(f"----- RESULT {i} -----")
            print(f"  Score: {r.score:.4f}")
            print(f"  Text:  {r.text[:200]}{'...' if len(r.text) > 200 else ''}")
            print(f"  Sources ({len(r.sources)}):")
            for src in r.sources:
                print(f"    • {src.libguide_title} → {src.section_title}")
                print(f"      {src.url}")
            print()

    # -------------------------------------------------------
    # verify the result structure matches the Pydantic models

    print("=== Validating Response Structure ===")
    response = QueryResponse(query=base_query, top_k=TOP_K, results=results)
    print(json.dumps(response.model_dump(), indent=2))
