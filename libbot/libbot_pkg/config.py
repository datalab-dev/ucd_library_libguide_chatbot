from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- ChromaDB ---
    chroma_db_path: str = CHROMA_DB_PATH
    collection_name: str = COLLECTION_NAME

    # --- Embedding Model ---
    model_name: str = MODEL_NAME
    torch_num_threads: int = 16

    # --- Search ---
    top_k: int = 3

    # --- Ollama LLM --- (TEMPORARY)
    ollama_url: str = OLLAMA_URL
    ollama_model: str = OLLAMA_MODEL

    # --- API Server ---
    host: str = HOST
    port: int = PORT

    # Allows overriding any setting via a .env file or environment variables.
    # e.g. export CHROMA_DB_PATH=/new/path  or  echo "TOP_K=5" >> .env
    # e.g. export OLLAMA_MODEL=llama3:16b  or  echo "OLLAMA_MODEL=llama3:16b" >> .env
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
