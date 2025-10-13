"""
Configuração de Modelos LLM Disponíveis (Outubro 2025)
"""
from typing import Dict, List
from dataclasses import dataclass


@dataclass
class LLMModel:
    """Representa um modelo LLM disponível"""
    name: str
    display_name: str
    provider: str
    context_window: int
    supports_streaming: bool = True
    cost_per_1m_input: float = 0.0
    cost_per_1m_output: float = 0.0
    description: str = ""


# ============================================
# DEFINIÇÃO DE MODELOS DISPONÍVEIS
# ============================================

AVAILABLE_MODELS: Dict[str, List[LLMModel]] = {
    
    # ----------------------------------------
    # ANTHROPIC (Claude)
    # ----------------------------------------
    "Anthropic": [
        LLMModel(
            name="claude-sonnet-4-5-20250929",
            display_name="Claude Sonnet 4.5",
            provider="anthropic",
            context_window=200000,
            cost_per_1m_input=3.0,
            cost_per_1m_output=15.0,
            description="Melhor modelo de coding do mundo. Excelente para agentes e construção."
        ),
        LLMModel(
            name="claude-opus-4-20250514",
            display_name="Claude Opus 4.1",
            provider="anthropic",
            context_window=200000,
            cost_per_1m_input=15.0,
            cost_per_1m_output=75.0,
            description="Máxima qualidade. Ideal para tarefas complexas e revisão crítica."
        ),
        LLMModel(
            name="claude-sonnet-4-20250514",
            display_name="Claude Sonnet 4",
            provider="anthropic",
            context_window=200000,
            cost_per_1m_input=3.0,
            cost_per_1m_output=15.0,
            description="Versão anterior, ainda muito capaz."
        ),
        LLMModel(
            name="claude-haiku-4-20250323",
            display_name="Claude Haiku 4",
            provider="anthropic",
            context_window=200000,
            cost_per_1m_input=0.8,
            cost_per_1m_output=4.0,
            description="Rápido e econômico. Bom para tarefas simples."
        ),
    ],
    
    # ----------------------------------------
    # OPENAI (GPT)
    # ----------------------------------------
    "OpenAI": [
        LLMModel(
            name="gpt-5",
            display_name="GPT-5",
            provider="openai",
            context_window=400000,
            cost_per_1m_input=1.25,
            cost_per_1m_output=10.0,
            description="Modelo flagship. Ótimo raciocínio, multimodal. Mais barato."
        ),
        LLMModel(
            name="gpt-5-codex",
            display_name="GPT-5 Codex",
            provider="openai",
            context_window=400000,
            cost_per_1m_input=1.25,
            cost_per_1m_output=10.0,
            description="Especializado em código. Alternativa ao Claude para coding."
        ),
        LLMModel(
            name="gpt-4.5",
            display_name="GPT-4.5",
            provider="openai",
            context_window=128000,
            cost_per_1m_input=75.0,
            cost_per_1m_output=150.0,
            description="Modelo premium. Excelente escrita e design. Muito caro."
        ),
        LLMModel(
            name="gpt-4o",
            display_name="GPT-4o",
            provider="openai",
            context_window=128000,
            cost_per_1m_input=2.5,
            cost_per_1m_output=10.0,
            description="Versão anterior rápida e multimodal."
        ),
        LLMModel(
            name="gpt-4o-mini",
            display_name="GPT-4o Mini",
            provider="openai",
            context_window=128000,
            cost_per_1m_input=0.15,
            cost_per_1m_output=0.60,
            description="Econômico e rápido. Ideal para tarefas simples."
        ),
    ],
    
    # ----------------------------------------
    # GOOGLE (Gemini)
    # ----------------------------------------
    "Google": [
        LLMModel(
            name="gemini-2.5-pro",
            display_name="Gemini 2.5 Pro",
            provider="google",
            context_window=2000000,
            cost_per_1m_input=1.25,
            cost_per_1m_output=10.0,
            description="Enorme context window (2M tokens). Excelente para documentos longos."
        ),
        LLMModel(
            name="gemini-2.0-flash",
            display_name="Gemini 2.0 Flash",
            provider="google",
            context_window=1000000,
            cost_per_1m_input=0.075,
            cost_per_1m_output=0.30,
            description="Rápido e barato. Menos alucinações."
        ),
        LLMModel(
            name="gemini-2.0-flash-lite",
            display_name="Gemini 2.0 Flash Lite",
            provider="google",
            context_window=1000000,
            cost_per_1m_input=0.04,
            cost_per_1m_output=0.15,
            description="Ultra econômico. Tarefas básicas."
        ),
    ],
    
    # ----------------------------------------
    # DEEPSEEK
    # ----------------------------------------
    "DeepSeek": [
        LLMModel(
            name="deepseek-chat",
            display_name="DeepSeek Chat",
            provider="deepseek",
            context_window=64000,
            cost_per_1m_input=0.14,
            cost_per_1m_output=0.28,
            description="Modelo chinês. Bom custo-benefício."
        ),
        LLMModel(
            name="deepseek-coder",
            display_name="DeepSeek Coder",
            provider="deepseek",
            context_window=64000,
            cost_per_1m_input=0.14,
            cost_per_1m_output=0.28,
            description="Especializado em código."
        ),
    ],
    
    # ----------------------------------------
    # XAI (Grok)
    # ----------------------------------------
    "xAI": [
        LLMModel(
            name="grok-2",
            display_name="Grok 2",
            provider="xai",
            context_window=128000,
            cost_per_1m_input=2.0,
            cost_per_1m_output=10.0,
            description="Modelo da xAI. Acesso a dados do X (Twitter)."
        ),
    ],
    
    # ----------------------------------------
    # QWEN (Alibaba)
    # ----------------------------------------
    "Qwen": [
        LLMModel(
            name="qwen-turbo",
            display_name="Qwen Turbo",
            provider="qwen",
            context_window=8000,
            cost_per_1m_input=0.3,
            cost_per_1m_output=0.6,
            description="Modelo da Alibaba. Econômico."
        ),
        LLMModel(
            name="qwen-plus",
            display_name="Qwen Plus",
            provider="qwen",
            context_window=32000,
            cost_per_1m_input=0.6,
            cost_per_1m_output=1.2,
            description="Versão mais capaz."
        ),
    ],
    
    # ----------------------------------------
    # OLLAMA (Local)
    # ----------------------------------------
    "Ollama": [
        LLMModel(
            name="llama3.3:70b",
            display_name="Llama 3.3 70B",
            provider="ollama",
            context_window=128000,
            cost_per_1m_input=0.0,
            cost_per_1m_output=0.0,
            description="Meta Llama local. Gratuito mas requer GPU potente."
        ),
        LLMModel(
            name="mistral:7b",
            display_name="Mistral 7B",
            provider="ollama",
            context_window=32000,
            cost_per_1m_input=0.0,
            cost_per_1m_output=0.0,
            description="Modelo local leve. Rápido."
        ),
        LLMModel(
            name="codellama:34b",
            display_name="CodeLlama 34B",
            provider="ollama",
            context_window=16000,
            cost_per_1m_input=0.0,
            cost_per_1m_output=0.0,
            description="Especializado em código. Local."
        ),
    ],
}


# ============================================
# FUNÇÕES AUXILIARES
# ============================================

def get_all_providers() -> List[str]:
    """Retorna lista de todos os providers disponíveis"""
    return list(AVAILABLE_MODELS.keys())


def get_models_by_provider(provider: str) -> List[LLMModel]:
    """Retorna modelos de um provider específico"""
    return AVAILABLE_MODELS.get(provider, [])


def get_model_by_name(model_name: str) -> LLMModel | None:
    """Busca um modelo pelo nome completo"""
    for models in AVAILABLE_MODELS.values():
        for model in models:
            if model.name == model_name:
                return model
    return None


def get_recommended_models() -> Dict[str, LLMModel]:
    """Retorna modelos recomendados para cada função"""
    return {
        "planning": get_model_by_name("claude-sonnet-4-5-20250929"),
        "building": get_model_by_name("claude-sonnet-4-5-20250929"),
        "reviewing": get_model_by_name("claude-opus-4-20250514"),
        "fast_tasks": get_model_by_name("gpt-4o-mini"),
    }


def estimate_cost(
    model_name: str, 
    input_tokens: int, 
    output_tokens: int
) -> float:
    """
    Estima o custo de uma chamada para um modelo
    
    Args:
        model_name: Nome do modelo
        input_tokens: Número de tokens de entrada
        output_tokens: Número de tokens de saída
        
    Returns:
        Custo estimado em USD
    """
    model = get_model_by_name(model_name)
    if not model:
        return 0.0
    
    cost_input = (input_tokens / 1_000_000) * model.cost_per_1m_input
    cost_output = (output_tokens / 1_000_000) * model.cost_per_1m_output
    
    return cost_input + cost_output