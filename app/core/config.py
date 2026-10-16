from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI Production Debugging Copilot"
    app_version: str = "1.0.0"
    debug: bool = False

    ollama_model: str = "qwen3:8b"
    embedding_model: str = "all-MiniLM-L6-v2"
    retrieval_top_k: int = 5

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()