"""
Definição dos Estados do Grafo LangGraph
VERSÃO APRIMORADA - Com campos para refinamento de requisitos
"""
from typing import Annotated, Optional, Literal, Union
from typing_extensions import TypedDict
from pydantic import BaseModel, Field
from datetime import datetime
from langgraph.graph import add_messages
from langchain_core.messages import BaseMessage


# ============================================
# TIPOS DE DEMANDA
# ============================================

DemandType = Literal[
    "analysis",        # Análise / Research
    "software",        # Desenvolvimento de Software
    "data_pipeline",   # Pipeline de Dados
    "unknown"          # Não classificado ainda
]


# ============================================
# MODELOS DE DADOS
# ============================================

class Requirements(BaseModel):
    """Requisitos extraídos da demanda"""
    raw_demand: str
    demand_type: DemandType
    key_requirements: list[str] = Field(default_factory=list)
    technologies_mentioned: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    expected_outputs: list[str] = Field(default_factory=list)
    confidence_score: float = 0.0


class Plan(BaseModel):
    """Plano de execução da solução"""
    title: str
    summary: str
    steps: list[dict] = Field(default_factory=list)
    technologies: list[str] = Field(default_factory=list)
    estimated_complexity: Literal["low", "medium", "high", "very_high"] = "medium"
    risks: list[dict] = Field(default_factory=list)
    prerequisites: list[str] = Field(default_factory=list)


class Review(BaseModel):
    """Resultado de revisão"""
    is_approved: bool
    confidence_score: float
    issues_found: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)


class Solution(BaseModel):
    """Solução construída"""
    code: Optional[str] = None
    documentation: Optional[str] = None
    tests: Optional[str] = None
    dependencies: list[str] = Field(default_factory=list)
    files: dict[str, str] = Field(default_factory=dict)
    

class ValidationResult(BaseModel):
    """Resultado de validação"""
    is_valid: bool
    passed_checks: list[str] = Field(default_factory=list)
    failed_checks: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


# ============================================
# ESTADO DO GRAFO
# ============================================

class AgentState(TypedDict):
    """
    Estado principal que flui pelo grafo LangGraph
    VERSÃO APRIMORADA - Com suporte a refinamento de requisitos
    """
    
    # ----------------------------------------
    # Input do Usuário
    # ----------------------------------------
    user_demand: str
    """Demanda original do usuário em linguagem natural"""
    
    # ✅ NOVO: Refinamento de Requisitos
    refined_demand: Optional[str]
    """Demanda refinada pelo usuário após feedback dos requisitos"""
    
    requirements_approved_by_user: bool
    """Se o usuário aprovou os requisitos mesmo com issues"""
    
    requirements_refinement_iteration: int
    """Contador de iterações de refinamento de requisitos"""
    
    # ----------------------------------------
    # Classificação e Requisitos
    # ----------------------------------------
    demand_type: DemandType
    """Tipo de demanda identificado"""
    
    requirements: Optional[dict]
    """Requisitos extraídos (serialized Requirements)"""
    
    requirements_review: Optional[dict]
    """Revisão dos requisitos (serialized Review)"""
    
    # ----------------------------------------
    # Planejamento
    # ----------------------------------------
    planning_prompts: Optional[dict]
    """Prompts especializados para o planejador"""
    
    planning_prompts_review: Optional[dict]
    """Revisão dos prompts"""
    
    plan: Optional[dict]
    """Plano de execução (serialized Plan)"""
    
    plan_review: Optional[dict]
    """Revisão do plano (serialized Review)"""
    
    # ----------------------------------------
    # Feedback do Usuário (Plano)
    # ----------------------------------------
    user_feedback: Optional[str]
    """Feedback do usuário sobre o plano"""
    
    user_approved: bool
    """Se o usuário aprovou o plano"""
    
    feedback_iteration: int
    """Contador de iterações de feedback do plano"""
    
    # ----------------------------------------
    # Construção
    # ----------------------------------------
    solution: Optional[dict]
    """Solução construída (serialized Solution)"""
    
    solution_review: Optional[dict]
    """Revisão da solução (serialized Review)"""
    
    validation_result: Optional[dict]
    """Resultado da validação final (serialized ValidationResult)"""
    
    # ----------------------------------------
    # Controle de Fluxo
    # ----------------------------------------
    current_step: str
    """Step atual no fluxo"""
    
    errors: list[str]
    """Lista de erros encontrados"""
    
    warnings: list[str]
    """Lista de warnings"""
    
    # ----------------------------------------
    # Mensagens (para contexto LLM)
    # ----------------------------------------
    messages: Annotated[list[BaseMessage], add_messages]
    """Histórico de mensagens para contexto"""
    
    # ----------------------------------------
    # Metadados
    # ----------------------------------------
    session_id: str
    """ID único da sessão"""
    
    started_at: datetime
    """Timestamp de início"""
    
    completed_at: Optional[datetime]
    """Timestamp de conclusão"""
    
    total_tokens_used: int
    """Total de tokens consumidos"""
    
    total_cost: float
    """Custo total estimado em USD"""
    
    # ----------------------------------------
    # Configurações
    # ----------------------------------------
    selected_models: dict[str, str]
    """Modelos selecionados para cada função"""


# ============================================
# FUNÇÕES AUXILIARES PARA O ESTADO
# ============================================

def create_initial_state(
    user_demand: str,
    session_id: str,
    selected_models: dict[str, str]
) -> AgentState:
    """
    Cria o estado inicial do grafo
    
    Args:
        user_demand: Demanda do usuário
        session_id: ID da sessão
        selected_models: Modelos selecionados
        
    Returns:
        Estado inicial
    """
    return AgentState(
        # Input
        user_demand=user_demand,
        
        # ✅ NOVO: Refinamento de requisitos
        refined_demand=None,
        requirements_approved_by_user=False,
        requirements_refinement_iteration=0,
        
        # Classificação
        demand_type="unknown",
        requirements=None,
        requirements_review=None,
        
        # Planejamento
        planning_prompts=None,
        planning_prompts_review=None,
        plan=None,
        plan_review=None,
        
        # Feedback do plano
        user_feedback=None,
        user_approved=False,
        feedback_iteration=0,
        
        # Construção
        solution=None,
        solution_review=None,
        validation_result=None,
        
        # Controle
        current_step="classification",
        errors=[],
        warnings=[],
        
        # Mensagens
        messages=[],
        
        # Metadados
        session_id=session_id,
        started_at=datetime.now(),
        completed_at=None,
        total_tokens_used=0,
        total_cost=0.0,
        
        # Config
        selected_models=selected_models,
    )


def add_error(state: AgentState, error: str) -> AgentState:
    """Adiciona um erro ao estado"""
    state["errors"].append(error)
    return state


def add_warning(state: AgentState, warning: str) -> AgentState:
    """Adiciona um warning ao estado"""
    state["warnings"].append(warning)
    return state


def update_tokens_and_cost(
    state: AgentState,
    tokens: int,
    cost: float
) -> AgentState:
    """Atualiza contadores de tokens e custo"""
    state["total_tokens_used"] += tokens
    state["total_cost"] += cost
    return state


def get_requirements(state: AgentState) -> Optional[Requirements]:
    """Deserializa requirements do estado"""
    if state["requirements"]:
        return Requirements(**state["requirements"])
    return None


def get_plan(state: AgentState) -> Optional[Plan]:
    """Deserializa plan do estado"""
    if state["plan"]:
        return Plan(**state["plan"])
    return None


def get_solution(state: AgentState) -> Optional[Solution]:
    """Deserializa solution do estado"""
    if state["solution"]:
        return Solution(**state["solution"])
    return None