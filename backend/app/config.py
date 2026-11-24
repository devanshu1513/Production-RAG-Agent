
"""
Application configuration using pydantic-settings.

All sensitive values are loaded from environment variables
or a local .env file. Never hardcode API keys or passwords.
"""

from functools import lru_cache
from urllib.parse import quote_plus, urlsplit

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ---------------------------------------------------------
    # Application
    # ---------------------------------------------------------

    APP_NAME: str = "RAG Agent API"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # ---------------------------------------------------------
    # Google Gemini
    # ---------------------------------------------------------

    GOOGLE_API_KEY: str

    GEMINI_MODEL: str = "gemini-2.5-flash"
    GEMINI_EMBEDDING_MODEL: str = "models/gemini-embedding-001"

    EMBEDDING_DIMENSION: int = 3072
    EMBEDDING_BATCH_SIZE: int = 5

    # ---------------------------------------------------------
    # RAG Retrieval
    # ---------------------------------------------------------

    RETRIEVAL_TOP_K: int = 5
    RETRIEVAL_MIN_SCORE: float = 0.63
    RETRIEVAL_MAX_GAP: float = 0.05
    MAX_HISTORY_PAIRS: int = 3

    # ---------------------------------------------------------
    # Embedding Resiliency
    # ---------------------------------------------------------

    MAX_EMBED_RETRIES: int = 5
    INITIAL_BACKOFF: float = 1.0
    MAX_BACKOFF: float = 16.0
    ENABLE_JITTER: bool = True
    MAX_CONCURRENT_EMBEDDINGS: int = 1

    # ---------------------------------------------------------
    # PostgreSQL
    # ---------------------------------------------------------

    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "raguser"
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str = "ragdb"

    @property
    def postgres_dsn(self) -> str:
        """Async PostgreSQL connection string with SSL."""

        user = quote_plus(self.POSTGRES_USER)
        password = quote_plus(self.POSTGRES_PASSWORD)
        database = quote_plus(self.POSTGRES_DB)

        return (
            f"postgresql+asyncpg://{user}:{password}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{database}"
            f"?ssl=require"
        )

    @property
    def postgres_dsn_sync(self) -> str:
        """Synchronous PostgreSQL connection string with SSL."""

        user = quote_plus(self.POSTGRES_USER)
        password = quote_plus(self.POSTGRES_PASSWORD)
        database = quote_plus(self.POSTGRES_DB)

        return (
            f"postgresql://{user}:{password}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{database}"
            f"?sslmode=require"
        )

    # ---------------------------------------------------------
    # Qdrant Vector Database
    # ---------------------------------------------------------

    QDRANT_HOST: str = "qdrant"
    QDRANT_PORT: int = 6333
    QDRANT_API_KEY: str | None = None
    QDRANT_COLLECTION: str = "documents"

    @property
    def qdrant_url(self) -> str:
        """
        Build the Qdrant URL.

        Production:
            Qdrant Cloud over HTTPS.

        Development:
            Local Docker Qdrant over HTTP.

        Accepts either a hostname or a complete URL.
        """

        host = self.QDRANT_HOST.strip().rstrip("/")

        # Use an explicitly supplied URL without modifying it.
        if host.startswith(("http://", "https://")):
            return host

        # Select protocol based on environment.
        scheme = (
            "https"
            if self.ENVIRONMENT.lower() == "production"
            else "http"
        )

        # Avoid appending the port if the hostname already has one.
        parsed = urlsplit(f"//{host}")

        if parsed.port is not None:
            return f"{scheme}://{host}"

        return f"{scheme}://{host}:{self.QDRANT_PORT}"

    # ---------------------------------------------------------
    # Upload Limits
    # ---------------------------------------------------------

    MAX_UPLOAD_SIZE_MB: int = 50
    MAX_FILES_PER_UPLOAD: int = 10

    # ---------------------------------------------------------
    # PDF Chunking
    # ---------------------------------------------------------

    MIN_CHUNK_SIZE: int = 500
    MAX_CHUNK_SIZE: int = 2000
    CHUNK_OVERLAP: int = 200

    # ---------------------------------------------------------
    # CORS
    # ---------------------------------------------------------

    CORS_ORIGINS: list[str] = ["*"]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached singleton of Settings."""

    return Settings()  # type: ignore[call-arg]
