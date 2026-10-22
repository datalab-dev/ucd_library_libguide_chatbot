"""Build the ChromaDB collection from a scraped corpus CSV.

Consolidates the three post-scrape steps from PIPELINE_PLAN.md into one
script (matching research/corpus_update.py, qwen_embedding_space.py and
chroma_db_creation.py):

    1. Add the combined_text column and save CSV + Parquet
    2. Generate L2-normalized Qwen embeddings, save as .npy
    3. Create the ChromaDB collection (cosine, ids = str(local_id))

Model name and collection name come from .env (via libbot_pkg.config).
Defaults write to *_new paths so the production parquet/embeddings/
chroma_db are never touched; deploy by updating CHROMA_DB_PATH in .env
or swapping directories.

Usage:
    pixi run python pipeline/build_chromadb.py
    pixi run python pipeline/build_chromadb.py --reuse-embeddings
"""

import argparse
import logging
import os
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

os.environ.setdefault("HF_HOME", "/dsl/libbot/data/huggingface_cache")
os.environ.setdefault("SENTENCE_TRANSFORMERS_HOME", "/dsl/libbot/data/huggingface_cache")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from libbot_pkg.config import load_settings  # noqa: E402  (needs repo root on path)

# # ---------- Defaults ----------
# INPUT_CSV = "/dsl/libbot/data/text_full_libguide_new.csv"
# OUTPUT_CSV = "/dsl/libbot/data/combined_text_full_libguide_new.csv"
# OUTPUT_PARQUET = "/dsl/libbot/data/combined_text_full_libguide_new.parquet"
# OUTPUT_EMBEDDINGS = "/dsl/libbot/data/embeddings_qwen_new.npy"
# CHROMA_DB_PATH = "/dsl/libbot/data/chroma_db_new"
# ENCODE_BATCH_SIZE = 16
# CHROMA_BATCH_SIZE = 1000
# # ------------------------------

EXPECTED_COLUMNS = ["local_id", "parent_id", "text", "libguide_title",
                    "libguide_url", "chunk_title", "chunk_url", "external_url",
                    "authors"]

log = logging.getLogger("build_chromadb")


def add_combined_text(df: pd.DataFrame) -> pd.DataFrame:
    """Same formula as research/corpus_update.py."""
    df = df.copy()
    df["combined_text"] = (
        "Guide Title: " + df["libguide_title"].fillna("").astype(str) + "\n"
        "Section Title: " + df["chunk_title"].fillna("").astype(str) + "\n\n"
        + df["text"].fillna("").astype(str)
    )
    return df


def generate_embeddings(texts: list[str]) -> np.ndarray:
    import torch
    from sentence_transformers import SentenceTransformer

    torch.set_num_threads(settings.torch_num_threads)
    log.info("Loading embedding model %s ...", settings.model_name)
    model = SentenceTransformer(
        settings.model_name,
        device="cpu",
        model_kwargs={"torch_dtype": torch.float32},
        tokenizer_kwargs={"padding_side": "left"},
        trust_remote_code=True,
    )
    log.info("Encoding %d documents (batch_size=%d) ...", len(texts), ENCODE_BATCH_SIZE)
    started = time.monotonic()
    embeddings = model.encode(
        texts,
        batch_size=ENCODE_BATCH_SIZE,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )
    log.info("Encoded in %.0fs, shape=%s", time.monotonic() - started, embeddings.shape)
    return embeddings.astype(np.float32)


def build_collection(df: pd.DataFrame, embeddings: np.ndarray, db_path: str):
    import chromadb

    assert len(embeddings) == len(df), \
        f"Mismatch: {len(embeddings)} embeddings vs {len(df)} rows"

    client = chromadb.PersistentClient(path=db_path)
    try:
        client.delete_collection(settings.collection_name)
        log.info("Dropped existing collection %r in %s", settings.collection_name, db_path)
    except Exception:
        pass
    collection = client.create_collection(
        name=settings.collection_name,
        metadata={"hnsw:space": "cosine"},
    )

    def as_str(value) -> str:
        return str(value) if pd.notna(value) else ""

    ids, metadatas = [], []
    for row in df.itertuples(index=False):
        ids.append(str(int(row.local_id)))
        metadatas.append({
            "parent_id": str(int(row.parent_id)),
            "text": as_str(row.text),
            "libguide_title": as_str(row.libguide_title),
            "libguide_url": as_str(row.libguide_url),
            "chunk_title": as_str(row.chunk_title),
            "chunk_url": as_str(row.chunk_url),
            "external_url": as_str(row.external_url),
            "authors": as_str(row.authors),
            "combined_text": as_str(row.combined_text),
        })

    for i in range(0, len(ids), CHROMA_BATCH_SIZE):
        collection.add(
            ids=ids[i:i + CHROMA_BATCH_SIZE],
            embeddings=embeddings[i:i + CHROMA_BATCH_SIZE].tolist(),
            metadatas=metadatas[i:i + CHROMA_BATCH_SIZE],
        )
        log.info("Inserted %d/%d documents", min(i + CHROMA_BATCH_SIZE, len(ids)), len(ids))

    count = collection.count()
    assert count == len(ids), f"Collection has {count} documents, expected {len(ids)}"
    log.info("Collection %r in %s verified: %d documents",
             settings.collection_name, db_path, count)


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--input", default=None,
                        help="Scraped corpus CSV (8 columns)")
    parser.add_argument("--output-csv", default=None)
    parser.add_argument("--output-parquet", default=None)
    parser.add_argument("--embeddings", default=None,
                        help="Path to save (or reuse) the embeddings .npy")
    parser.add_argument("--chroma-path", default=None,
                        help="ChromaDB directory to (re)build")
    parser.add_argument("--reuse-embeddings", action="store_true",
                        help="Skip encoding and load --embeddings from disk")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s %(levelname)s %(message)s",
                        stream=sys.stderr)

    log.info("Reading %s", args.input)
    df = pd.read_csv(args.input, encoding="utf-8")
    missing = set(EXPECTED_COLUMNS) - set(df.columns)
    if missing:
        sys.exit(f"Input is missing required columns: {sorted(missing)}")
    log.info("%d rows, %d guides", len(df), df["parent_id"].nunique())

    df = add_combined_text(df)
    df.to_csv(args.output_csv, index=False, encoding="utf-8")
    df.to_parquet(args.output_parquet, index=False)
    log.info("Wrote %s and %s", args.output_csv, args.output_parquet)

    if args.reuse_embeddings:
        log.info("Reusing embeddings from %s", args.embeddings)
        embeddings = np.load(args.embeddings)
    else:
        embeddings = generate_embeddings(df["combined_text"].tolist())
        np.save(args.embeddings, embeddings)
        log.info("Saved embeddings to %s", args.embeddings)

    build_collection(df, embeddings, args.chroma_path)
    log.info("Done. To deploy, point CHROMA_DB_PATH in .env at %s "
             "(or swap it with the production chroma_db directory).", args.chroma_path)


if __name__ == "__main__":
    main()
