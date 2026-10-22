from pathlib import Path
from typing import Literal

from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    TomlConfigSettingsSource,
)


class Settings(BaseSettings):
    # --- ChromaDB ---
    chroma_db_path: str
    collection_name: str

    # --- Embedding Model ---
    embedding_model_name: str
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

    guide_text_csv: str
    combined_text_csv: str

    #[scrape_guides]
    # ---------- Defaults ----------
    url_list_path: str
    request_delay: float
    request_timeout: float
    max_retries: int
    user_agent: str
    min_prose_chars: int  # ignore box prose shorter than this
    # ------------------------------



    #[build_chromadb]
    # ---------- Defaults ----------
    guide_text_csv: str
    combined_text_csv: str
    combined_text_parquet: str
    embeddings_file: str
    reuse_embeddings: bool
    chroma_db_path: str
    encode_batch_size: int
    chroma_batch_size: int
    device: str = "cpu"
    # ------------------------------


    #[validate_scrape]
    # ---------- Defaults ----------
    baseline_guide_text_csv: str
    min_text_chars: int      # texts shorter than this are flagged
    row_drop_warn: float      # warn if a guide lost >50% of its baseline rows
    # ------------------------------


    model_config = SettingsConfigDict(
        #env_prefix="APP_",
        env_file=".env",
        env_nested_delimiter="__",
        toml_file = Path(__file__).resolve().parent / "config.toml",
        # toml_file = "config.toml",
        extra = "allow"
    ) # __file__ is this current file, .parent is the package, and second .parent is where the .env lives

    # Dynamic property to get the currently desired model
    @property
    def ollama_model(self) -> str:
        if self.active_llm_mode == "cloud":
            return self.ollama_cloud_model
        return self.ollama_local_model


    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            file_secret_settings,
            TomlConfigSettingsSource(settings_cls),
        )


def load_settings(overrides = {}):
    return Settings(**overrides)