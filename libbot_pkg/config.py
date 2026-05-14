from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from typing import Literal

# Pydantic automatically matches field names case-insensitively

class Settings(BaseSettings):
    # --- ChromaDB ---
    chroma_db_path: str
    collection_name: str

    # --- Embedding Model ---
    model_name: str
    torch_num_threads: int = 16
    top_k: int = 3

    # --- Ollama LLM --- 
    ollama_url: str

    # Accept only "local" or "cloud" to prevent typos
    active_llm_mode: Literal["local", "cloud"] = "local"
    ollama_local_model: str
    ollama_cloud_model: str

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

    # Dynamic property to get the currently desired model
    @property
    def ollama_model(self) -> str:
        if self.active_llm_mode == "cloud":
            return self.ollama_cloud_model
        return self.ollama_local_model

settings = Settings()
