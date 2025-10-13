"""
Definição do Grafo LangGraph Principal
"""
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from core.state import AgentState
from core.nodes.classifier import (
    classify_and_extract_requirements,
    review_requirements
)
from core.nodes.planner import (
    create_planning_prompts,
    create_plan,
    review_plan
)
from core.nodes.builder import (
    build_solution,
    review_solution,
    validate_solution
)
from core.nodes.feedback import (
    wait_user_approval,
    process_feedback,
    route_after_plan_review,
    route_after_user_approval
)


def create_agent_graph():
    """
    Cria e configura o grafo de agentes
    
    Returns:
        Grafo compilado
    """
    # Criar grafo
    workflow = StateGraph(AgentState)
    
    # ========================================
    # ADICIONAR NÓS
    # ========================================
    
    # Fase 1: Classificação e Requisitos
    workflow.add_node("classify_and_extract", classify_and_extract_requirements)
    workflow.add_node("review_requirements", review_requirements)
    
    # Fase 2: Planejamento
    workflow.add_node("create_planning_prompts", create_planning_prompts)
    workflow.add_node("create_plan", create_plan)
    workflow.add_node("review_plan", review_plan)
    
    # Fase 3: Feedback do Usuário
    workflow.add_node("wait_user_approval", wait_user_approval)
    workflow.add_node("process_feedback", process_feedback)
    
    # Fase 4: Construção
    workflow.add_node("build_solution", build_solution)
    workflow.add_node("review_solution", review_solution)
    workflow.add_node("validate_solution", validate_solution)
    
    # ========================================
    # DEFINIR EDGES (FLUXO)
    # ========================================
    
    # Ponto de entrada
    workflow.set_entry_point("classify_and_extract")
    
    # Fluxo de Classificação
    workflow.add_edge("classify_and_extract", "review_requirements")
    
    # Após revisão de requisitos
    workflow.add_conditional_edges(
        "review_requirements",
        lambda state: "create_planning_prompts" if state.get("requirements_review", {}).get("is_approved", False) else END,
        {
            "create_planning_prompts": "create_planning_prompts",
            END: END
        }
    )
    
    # Fluxo de Planejamento
    workflow.add_edge("create_planning_prompts", "create_plan")
    workflow.add_edge("create_plan", "review_plan")
    
    # Após revisão do plano
    workflow.add_conditional_edges(
        "review_plan",
        route_after_plan_review,
        {
            "wait_user_approval": "wait_user_approval",
            "process_feedback": "process_feedback"
        }
    )
    
    # ✅ CORRIGIDO: Após aprovação do usuário (CHECKPOINT)
    workflow.add_conditional_edges(
        "wait_user_approval",
        route_after_user_approval,
        {
            "build_solution": "build_solution",
            "process_feedback": "process_feedback",
            "wait": END  # ✅ Adicionada opção de terminar e aguardar
        }
    )
    
    # Loop de feedback
    workflow.add_edge("process_feedback", "review_plan")
    
    # Fluxo de Construção
    workflow.add_edge("build_solution", "review_solution")
    
    # Após revisão da solução
    workflow.add_conditional_edges(
        "review_solution",
        lambda state: "validate_solution" if state.get("solution_review", {}).get("is_approved", False) else END,
        {
            "validate_solution": "validate_solution",
            END: END
        }
    )
    
    # Fim do fluxo
    workflow.add_edge("validate_solution", END)
    
    # ========================================
    # COMPILAR GRAFO
    # ========================================
    
    # Usar MemorySaver para checkpointing (Fase 1 - síncrono)
    memory = MemorySaver()
    
    app = workflow.compile(checkpointer=memory)
    
    return app


def get_graph_visualization() -> str:
    """
    Retorna uma visualização ASCII do grafo
    
    Returns:
        String com visualização
    """
    return """
    ┌─────────────────────────────────────────────────────────────┐
    │                  GRAFO DE AGENTES - FASE 1                  │
    └─────────────────────────────────────────────────────────────┘
    
    [START]
       ↓
    ┌──────────────────────────┐
    │ classify_and_extract     │  ← Classifica demanda e extrai requisitos
    └──────────────────────────┘
       ↓
    ┌──────────────────────────┐
    │ review_requirements      │  ← Revisa requisitos
    └──────────────────────────┘
       ↓
    ┌──────────────────────────┐
    │ create_planning_prompts  │  ← Cria prompts especializados
    └──────────────────────────┘
       ↓
    ┌──────────────────────────┐
    │ create_plan              │  ← Cria o plano de execução
    └──────────────────────────┘
       ↓
    ┌──────────────────────────┐
    │ review_plan              │  ← Revisa o plano
    └──────────────────────────┘
       ↓
       ├─→ [SE APROVADO]
       │      ↓
       │   ┌──────────────────────────┐
       │   │ wait_user_approval       │  ← ⏸️ CHECKPOINT: Aguarda usuário
       │   └──────────────────────────┘
       │      ↓
       │      ├─→ [APROVADO PELO USUÁRIO]
       │      │      ↓
       │      │   (continua para BUILD)
       │      │
       │      ├─→ [FEEDBACK DO USUÁRIO]
       │      │      ↓
       │      │   ┌──────────────────────────┐
       │      │   │ process_feedback         │  ← Processa feedback e ajusta
       │      │   └──────────────────────────┘
       │      │      ↓
       │      │      (volta para review_plan)
       │      │
       │      └─→ [AGUARDANDO DECISÃO]
       │             ↓
       │          [END] ← ⏸️ Grafo pausa aqui
       │
       └─→ [SE NÃO APROVADO]
              ↓
           (vai para process_feedback)
    
    [APÓS APROVAÇÃO]
       ↓
    ┌──────────────────────────┐
    │ build_solution           │  ← Constrói a solução
    └──────────────────────────┘
       ↓
    ┌──────────────────────────┐
    │ review_solution          │  ← Code review
    └──────────────────────────┘
       ↓
    ┌──────────────────────────┐
    │ validate_solution        │  ← Validação final
    └──────────────────────────┘
       ↓
    [END]
    """


def get_current_step_description(step: str) -> str:
    """
    Retorna descrição amigável do step atual
    
    Args:
        step: Nome do step
        
    Returns:
        Descrição formatada
    """
    descriptions = {
        "classification": "🔍 Analisando e classificando sua demanda...",
        "review_requirements": "✅ Revisando requisitos extraídos...",
        "create_planning_prompts": "📝 Criando instruções para o planejador...",
        "create_plan": "📋 Elaborando plano de execução...",
        "review_plan": "🔎 Revisando plano criado...",
        "wait_user_approval": "⏸️ Aguardando sua aprovação do plano...",
        "waiting_approval": "⏸️ Aguardando sua decisão...",
        "process_feedback": "🔄 Processando seu feedback e ajustando...",
        "build_solution": "🔨 Construindo a solução...",
        "review_solution": "👀 Realizando code review...",
        "validate_solution": "✅ Validação final da solução...",
        "completed": "🎉 Processo concluído com sucesso!",
        "error": "❌ Erro no processamento"
    }
    
    return descriptions.get(step, f"Processando: {step}")