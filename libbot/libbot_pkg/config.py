from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- ChromaDB ---
    chroma_db_path: str = "/dsl/libbot/data/chroma_db"
    collection_name: str = "libguides"

    # --- Embedding Model ---
    model_name: str = "Qwen/Qwen3-Embedding-0.6B"
    torch_num_threads: int = 16

    # --- Search ---
    top_k: int = 3

    # --- Ollama LLM --- (TEMPORARY)
    ollama_url: str = "http://127.0.0.1:11434/api/generate"
    ollama_model: str = "llama3:8b"

    # --- API Server ---
    host: str = "0.0.0.0"
    port: int = 8075

    # Allows overriding any setting via a .env file or environment variables.
    # e.g. export CHROMA_DB_PATH=/new/path  or  echo "TOP_K=5" >> .env
    # e.g. export OLLAMA_MODEL=llama3:16b  or  echo "OLLAMA_MODEL=llama3:16b" >> .env
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()