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

        print(f"Connecting to ChromaDB at: {settings.chroma_db_path}")
        self.client = chromadb.PersistentClient(path=settings.chroma_db_path)
        self.collection = self.client.get_collection(name=settings.collection_name)

        print(f"Loading embedding model: {settings.model_name}")
        self.model = SentenceTransformer(
            settings.model_name,
            device="cpu",
            model_kwargs={"torch_dtype": torch.float32},
            tokenizer_kwargs={"padding_side": "left"},
            trust_remote_code=True,
        )
        print("Retriever ready.")




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

            if text not in text_to_result:
                text_to_result[text] = {
                    "score": score,
                    "text": text,
                    "sources": [],
                }

            # Append source info regardless, since we want to aggregate all sources for the same text
            text_to_result[text]["sources"].append(
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