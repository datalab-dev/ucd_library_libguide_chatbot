from difflib import SequenceMatcher

import chromadb
import torch
from sentence_transformers import SentenceTransformer
import time
from .config import settings
from .models import SearchResult, Source


class Retriever:
    """
    Handles ChromaDB connection and semantic search.
    Loaded once at server startup and reused across requests.
    """

    def __init__(self):
        torch.set_num_threads(settings.torch_num_threads)

        print(f"\033[1;30m\nConnecting to ChromaDB at:\033[0m [\033[36m{settings.chroma_db_path}]\033[0m]")
        self.client = chromadb.PersistentClient(path=settings.chroma_db_path)
        self.collection = self.client.get_collection(name=settings.collection_name)

        print(f"\033[1;30mLoading embedding model:\033[0m [\033[36m{settings.model_name}\033[0m]")
        self.model = SentenceTransformer(
            settings.model_name,
            device="cpu",
            model_kwargs={"torch_dtype": torch.float32},
            tokenizer_kwargs={"padding_side": "left"},
            trust_remote_code=True,
        )
        
        print(f"\033[1;30mUsing LLM model:\033[0m [\033[36m{settings.ollama_model}\033[0m]\n")


        print(f"\033[1;30mRetriever ready.\033[0m\n")




    def search(self, query: str, top_k: int = settings.top_k) -> list[SearchResult]:
        """
        Embed the query, search ChromaDB, deduplicate results, and
        aggregate sources for texts that appear across multiple guides.
        """

        t0 = time.perf_counter()
        # Encode the query using the Qwen query prompt
        
        # Implemented a simple heuristic to improve recall for short queries by repeating them.
        repeated_query = f"{query} {query}"

        query_emb = self.model.encode(
            repeated_query,
            prompt_name="query",
            normalize_embeddings=True,
            convert_to_numpy=True,
        )

        t1 = time.perf_counter()
        print(f"[TIMING] Embedding: {t1 - t0:.3f}s")


        # Fetch more candidates than needed — corpus has ~70% duplicates
        candidate_count = top_k * 5

        raw = self.collection.query(
            query_embeddings=[query_emb.tolist()],
            n_results=candidate_count,
            include=["metadatas", "distances"],
        )

        t2 = time.perf_counter()
        print(f"[TIMING] ChromaDB query: {t2 - t1:.3f}s")

        metadatas = raw["metadatas"][0]
        distances = raw["distances"][0]

        # Deduplicate by text, keeping the highest score and all sources
        text_to_result: dict[str, dict] = {}

        # Iterate over results in order of ChromaDB's ranking (best first)
        for metadata, distance in zip(metadatas, distances):
            text = metadata["text"]
            score = 1 - distance  # cosine distance → similarity

            # Implemented New "Fuzzy" Deduplication Logic ---
            matched_key = None
            for existing_text in text_to_result.keys():
                # Check for exact substring overlap OR ~90% fuzzy similarity
                if (text in existing_text) or (existing_text in text) or (SequenceMatcher(None, text, existing_text).ratio() > 0.90):
                    matched_key = existing_text
                    break

            if matched_key:
                # If the new text is longer than the stored one, swap it out to keep the most complete version
                if len(text) > len(matched_key):
                    data = text_to_result.pop(matched_key)
                    data["text"] = text  # Upgrade to the longer text
                    text_to_result[text] = data
                    active_text = text
                else:
                    active_text = matched_key
            else:
                # Brand new, unique text
                text_to_result[text] = {
                    "score": score,
                    "text": text,
                    "sources": [],
                }
                active_text = text

            # Append source info to whichever version we are keeping
            text_to_result[active_text]["sources"].append(
                Source(
                    libguide_title=metadata["libguide_title"],
                    section_title=metadata["chunk_title"],
                    url=metadata["libguide_url"],
                )
            )
            
            # Stop once we have enough unique texts
            if len(text_to_result) >= top_k:
                break

        # Sort by score descending and return as SearchResult models
        ranked = sorted(
            text_to_result.values(),
            key=lambda x: x["score"],
            reverse=True,
        )

        
        print(f"[TIMING] search() total: {t2 - t0:.3f}s")
        # Convert to SearchResult Pydantic models for API response
        return [
            SearchResult(
                score=r["score"],
                text=r["text"],
                sources=r["sources"],
            )
            for r in ranked[:top_k]
        ]