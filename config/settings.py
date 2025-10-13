"""
Configurações Gerais da Aplicação
"""
import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Configurações da aplicação carregadas do .env"""
    
    # Paths
    BASE_DIR: Path = Path(__file__).parent.parent
    PROMPTS_DIR: Path = BASE_DIR / "prompts"
    
    # API Keys - LLMs
    ANTHROPIC_API_KEY: Optional[str] = Field(None, env="ANTHROPIC_API_KEY")
    OPENAI_API_KEY: Optional[str] = Field(None, env="OPENAI_API_KEY")
    GOOGLE_API_KEY: Optional[str] = Field(None, env="GOOGLE_API_KEY")
    DEEPSEEK_API_KEY: Optional[str] = Field(None, env="DEEPSEEK_API_KEY")
    XAI_API_KEY: Optional[str] = Field(None, env="XAI_API_KEY")
    QWEN_API_KEY: Optional[str] = Field(None, env="QWEN_API_KEY")
    
    # API Keys - Web Search
    TAVILY_API_KEY: Optional[str] = Field(None, env="TAVILY_API_KEY")
    SERPER_API_KEY: Optional[str] = Field(None, env="SERPER_API_KEY")
    
    # Ollama Config
    OLLAMA_BASE_URL: str = Field("http://localhost:11434", env="OLLAMA_BASE_URL")
    
    # App Config
    LOG_LEVEL: str = Field("INFO", env="LOG_LEVEL")
    DEFAULT_TIMEOUT: int = Field(300, env="DEFAULT_TIMEOUT")
    MAX_CONTEXT_TOKENS: int = Field(200000, env="MAX_CONTEXT_TOKENS")
    
    # Streamlit Config
    STREAMLIT_SERVER_PORT: int = Field(8501, env="STREAMLIT_SERVER_PORT")
    STREAMLIT_THEME: str = Field("dark", env="STREAMLIT_THEME")
    
    # Configurações de Execução
    MAX_RETRIES: int = 3
    RETRY_DELAY: int = 2  # segundos
    
    # Guardrails
    MIN_CONFIDENCE_SCORE: float = 0.7
    ENABLE_STRICT_VALIDATION: bool = True
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Singleton da configuração
settings = Settings()


def get_settings() -> Settings:
    """Retorna a instância singleton de configurações"""
    return settings


def check_api_keys() -> dict[str, bool]:
    """
    Verifica quais API keys estão configuradas
    
    Returns:
        Dict com provider name e status (True se configurado)
    """
    return {
        "Anthropic": bool(settings.ANTHROPIC_API_KEY),
        "OpenAI": bool(settings.OPENAI_API_KEY),
        "Google": bool(settings.GOOGLE_API_KEY),
        "DeepSeek": bool(settings.DEEPSEEK_API_KEY),
        "xAI (Grok)": bool(settings.XAI_API_KEY),
        "Qwen": bool(settings.QWEN_API_KEY),
        "Tavily Search": bool(settings.TAVILY_API_KEY),
        "Serper Search": bool(settings.SERPER_API_KEY),
    }


def validate_minimum_config() -> tuple[bool, list[str]]:
    """
    Valida se há configuração mínima para rodar
    
    Returns:
        Tupla (is_valid, missing_items)
    """
    missing = []
    
    # Precisa de pelo menos 1 LLM configurado
    llms_available = any([
        settings.ANTHROPIC_API_KEY,
        settings.OPENAI_API_KEY,
        settings.GOOGLE_API_KEY,
        settings.DEEPSEEK_API_KEY,
        settings.XAI_API_KEY,
        settings.QWEN_API_KEY,
    ])
    
    if not llms_available:
        missing.append("Pelo menos 1 API Key de LLM deve ser configurada")
    
    return (len(missing) == 0, missing)