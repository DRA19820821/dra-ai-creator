"""
Factory para criação de instâncias de LLMs
"""
from typing import Optional
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama
from langchain_core.language_models.chat_models import BaseChatModel

from config.settings import settings
from config.llm_config import get_model_by_name, LLMModel


class LLMFactory:
    """Factory para criação de LLMs baseado em configuração"""
    
    @staticmethod
    def create_llm(
        model_name: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        streaming: bool = True,
        **kwargs
    ) -> BaseChatModel:
        """
        Cria uma instância de LLM baseado no nome do modelo
        
        Args:
            model_name: Nome do modelo (ex: 'claude-sonnet-4-5-20250929')
            temperature: Temperatura para geração (0.0 - 1.0)
            max_tokens: Máximo de tokens na resposta
            streaming: Se deve usar streaming
            **kwargs: Argumentos adicionais específicos do provider
            
        Returns:
            Instância do LLM configurada
            
        Raises:
            ValueError: Se o modelo não for encontrado ou API key não configurada
        """
        model_info = get_model_by_name(model_name)
        
        if not model_info:
            raise ValueError(f"Modelo '{model_name}' não encontrado na configuração")
        
        provider = model_info.provider
        
        # Configuração base
        base_config = {
            "temperature": temperature,
            "streaming": streaming,
        }
        
        if max_tokens:
            base_config["max_tokens"] = max_tokens
        
        # Merge com kwargs adicionais
        base_config.update(kwargs)
        
        # Cria LLM baseado no provider
        if provider == "anthropic":
            return LLMFactory._create_anthropic(model_name, base_config)
        
        elif provider == "openai":
            return LLMFactory._create_openai(model_name, base_config)
        
        elif provider == "google":
            return LLMFactory._create_google(model_name, base_config)
        
        elif provider == "ollama":
            return LLMFactory._create_ollama(model_name, base_config)
        
        elif provider == "deepseek":
            return LLMFactory._create_deepseek(model_name, base_config)
        
        elif provider == "xai":
            return LLMFactory._create_xai(model_name, base_config)
        
        elif provider == "qwen":
            return LLMFactory._create_qwen(model_name, base_config)
        
        else:
            raise ValueError(f"Provider '{provider}' não suportado")
    
    @staticmethod
    def _create_anthropic(model_name: str, config: dict) -> ChatAnthropic:
        """Cria instância do Claude"""
        if not settings.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY não configurada")
        
        return ChatAnthropic(
            model=model_name,
            api_key=settings.ANTHROPIC_API_KEY,
            timeout=settings.DEFAULT_TIMEOUT,
            **config
        )
    
    @staticmethod
    def _create_openai(model_name: str, config: dict) -> ChatOpenAI:
        """Cria instância do GPT"""
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY não configurada")
        
        return ChatOpenAI(
            model=model_name,
            api_key=settings.OPENAI_API_KEY,
            timeout=settings.DEFAULT_TIMEOUT,
            **config
        )
    
    @staticmethod
    def _create_google(model_name: str, config: dict) -> ChatGoogleGenerativeAI:
        """Cria instância do Gemini"""
        if not settings.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY não configurada")
        
        return ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=settings.GOOGLE_API_KEY,
            **config
        )
    
    @staticmethod
    def _create_ollama(model_name: str, config: dict) -> ChatOllama:
        """Cria instância de modelo local via Ollama"""
        return ChatOllama(
            model=model_name,
            base_url=settings.OLLAMA_BASE_URL,
            **config
        )
    
    @staticmethod
    def _create_deepseek(model_name: str, config: dict) -> ChatOpenAI:
        """Cria instância do DeepSeek (API compatível com OpenAI)"""
        if not settings.DEEPSEEK_API_KEY:
            raise ValueError("DEEPSEEK_API_KEY não configurada")
        
        return ChatOpenAI(
            model=model_name,
            api_key=settings.DEEPSEEK_API_KEY,
            base_url="https://api.deepseek.com/v1",
            timeout=settings.DEFAULT_TIMEOUT,
            **config
        )
    
    @staticmethod
    def _create_xai(model_name: str, config: dict) -> ChatOpenAI:
        """Cria instância do Grok (API compatível com OpenAI)"""
        if not settings.XAI_API_KEY:
            raise ValueError("XAI_API_KEY não configurada")
        
        return ChatOpenAI(
            model=model_name,
            api_key=settings.XAI_API_KEY,
            base_url="https://api.x.ai/v1",
            timeout=settings.DEFAULT_TIMEOUT,
            **config
        )
    
    @staticmethod
    def _create_qwen(model_name: str, config: dict) -> ChatOpenAI:
        """Cria instância do Qwen (API compatível com OpenAI)"""
        if not settings.QWEN_API_KEY:
            raise ValueError("QWEN_API_KEY não configurada")
        
        return ChatOpenAI(
            model=model_name,
            api_key=settings.QWEN_API_KEY,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            timeout=settings.DEFAULT_TIMEOUT,
            **config
        )
    
    @staticmethod
    def validate_model_availability(model_name: str) -> tuple[bool, str]:
        """
        Valida se um modelo pode ser usado
        
        Returns:
            Tupla (is_available, error_message)
        """
        model_info = get_model_by_name(model_name)
        
        if not model_info:
            return False, f"Modelo '{model_name}' não encontrado"
        
        provider = model_info.provider
        
        # Verifica API key para providers que precisam
        if provider == "anthropic" and not settings.ANTHROPIC_API_KEY:
            return False, "ANTHROPIC_API_KEY não configurada"
        
        if provider == "openai" and not settings.OPENAI_API_KEY:
            return False, "OPENAI_API_KEY não configurada"
        
        if provider == "google" and not settings.GOOGLE_API_KEY:
            return False, "GOOGLE_API_KEY não configurada"
        
        if provider == "deepseek" and not settings.DEEPSEEK_API_KEY:
            return False, "DEEPSEEK_API_KEY não configurada"
        
        if provider == "xai" and not settings.XAI_API_KEY:
            return False, "XAI_API_KEY não configurada"
        
        if provider == "qwen" and not settings.QWEN_API_KEY:
            return False, "QWEN_API_KEY não configurada"
        
        # Ollama sempre disponível (assume que está rodando)
        return True, ""


# Funções de conveniência
def create_llm(model_name: str, **kwargs) -> BaseChatModel:
    """Atalho para LLMFactory.create_llm"""
    return LLMFactory.create_llm(model_name, **kwargs)


def validate_model(model_name: str) -> tuple[bool, str]:
    """Atalho para LLMFactory.validate_model_availability"""
    return LLMFactory.validate_model_availability(model_name)