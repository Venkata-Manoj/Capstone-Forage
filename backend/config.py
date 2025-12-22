"""
Configuration management for CapstoneForge
Loads environment variables and provides application settings
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
import os
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Ollama Configuration
    ollama_base_url: str = Field("http://localhost:11434", env="OLLAMA_BASE_URL")
    ollama_model: str = Field("llama3.2", env="OLLAMA_MODEL")
    
    # Fallback Models (Optional)
    ollama_model_fallback_1: Optional[str] = Field(None, env="OLLAMA_MODEL_FALLBACK_1")
    ollama_model_fallback_2: Optional[str] = Field(None, env="OLLAMA_MODEL_FALLBACK_2")
    
    # Application Settings
    app_name: str = Field("CapstoneForge", env="APP_NAME")
    app_version: str = Field("1.0.0", env="APP_VERSION")
    debug: bool = Field(False, env="DEBUG")
    secret_key: str = Field(..., env="SECRET_KEY")
    
    # File Upload Settings
    max_upload_size: int = Field(52428800, env="MAX_UPLOAD_SIZE")  # 50MB
    upload_dir: str = Field("./uploads", env="UPLOAD_DIR")
    generated_dir: str = Field("./generated", env="GENERATED_DIR")
    
    # AI Settings
    embedding_model: str = Field("sentence-transformers/all-MiniLM-L6-v2", env="EMBEDDING_MODEL")
    max_tokens: int = Field(8000, env="MAX_TOKENS")
    temperature: float = Field(0.7, env="TEMPERATURE")
    
    # Vector Store
    faiss_index_dir: str = Field("./faiss_indexes", env="FAISS_INDEX_DIR")
    
    # LibreOffice Path
    libreoffice_path: str = Field(
        "C:\\Program Files\\LibreOffice\\program\\soffice.exe",
        env="LIBREOFFICE_PATH"
    )
    
    # CORS Settings
    allowed_origins: str = Field(
        "http://localhost:3000,http://localhost:5173",
        env="ALLOWED_ORIGINS"
    )
    
    # Tesseract OCR Path
    tesseract_cmd: str = Field(
        "C:\\Program Files\\Tesseract-OCR\\tesseract.exe",
        env="TESSERACT_CMD"
    )
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"
    
    def get_allowed_origins_list(self) -> list[str]:
        """Parse allowed origins from comma-separated string"""
        return [origin.strip() for origin in self.allowed_origins.split(",")]
    
    def ensure_directories(self):
        """Create necessary directories if they don't exist"""
        Path(self.upload_dir).mkdir(parents=True, exist_ok=True)
        Path(self.generated_dir).mkdir(parents=True, exist_ok=True)
        Path(self.faiss_index_dir).mkdir(parents=True, exist_ok=True)
    
    def get_primary_ai_provider(self) -> str:
        """Get the primary AI provider"""
        return "ollama"


# Global settings instance
settings = Settings()

# Ensure directories exist
settings.ensure_directories()
