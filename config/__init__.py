# ========================================
# config/__init__.py
# ========================================
"""
Módulo de Configuração
"""
from .settings import settings, get_settings, check_api_keys, validate_minimum_config
from .llm_config import (
    AVAILABLE_MODELS,
    LLMModel,
    get_all_providers,
    get_models_by_provider,
    get_model_by_name,
    get_recommended_models,
    estimate_cost
)

__all__ = [
    "settings",
    "get_settings",
    "check_api_keys",
    "validate_minimum_config",
    "AVAILABLE_MODELS",
    "LLMModel",
    "get_all_providers",
    "get_models_by_provider",
    "get_model_by_name",
    "get_recommended_models",
    "estimate_cost",
]