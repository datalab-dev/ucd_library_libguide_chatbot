import pandas as pd
import numpy as np

# ---------- CONFIG ----------
INPUT_CSV = "/dsl/libbot/data/text_full_libguide.csv"
OUTPUT_CSV = "/dsl/libbot/data/combined_text_full_libguide.csv"
OUTPUT_PARQUET = "/dsl/libbot/data/combined_text_full_libguide.parquet"

TEXT_COL = "text"
LIB_TITLE_COL = "libguide_title"
CHUNK_TITLE_COL = "chunk_title"
# ----------------------------

# Load data
df = pd.read_csv(INPUT_CSV, encoding="utf-8")

# Create combined text column
df["combined_text"] = (
    "Guide Title: " + df[LIB_TITLE_COL].fillna("").astype(str) + "\n"
    "Section Title: " + df[CHUNK_TITLE_COL].fillna("").astype(str) + "\n\n"
    + df[TEXT_COL].fillna("").astype(str)
)

# Save outputs
df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")
df.to_parquet(OUTPUT_PARQUET, index=False) # saving also as parquet for efficiency