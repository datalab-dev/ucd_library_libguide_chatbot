from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

# Pydantic automatically matches field names case-insensitively

class Settings(BaseSettings):
    # --- ChromaDB ---
    chroma_db_path: str
    collection_name: str

    # --- Embedding Model ---
    model_name: str
    torch_num_threads: int = 16
    top_k: int = 3

    # --- Ollama LLM --- (TEMPORARY)
    ollama_url: str
    ollama_model: str

    # --- API Server ---
    host: str
    port: int

    # Allows overriding any setting via a .env file or environment variables.
    # e.g. export CHROMA_DB_PATH=/new/path  or  echo "TOP_K=5" >> .env
    # e.g. export OLLAMA_MODEL=llama3:16b  or  echo "OLLAMA_MODEL=llama3:16b" >> .env
    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.parent / ".env",
        env_file_encoding="utf-8"
    ) # __file__ is this current file, .parent is the package, and second .parent is where the .env lives


settings = Settings()
