"""
Definição do Grafo LangGraph Principal
VERSÃO APRIMORADA - Com checkpoint de requisitos
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
    # Checkpoint 1: Requisitos
    wait_requirements_approval,
    process_requirements_refinement,
    route_after_requirements_review,
    route_after_requirements_approval,
    # Checkpoint 2: Plano
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
    
    # Fase 1.5: Checkpoint de Requisitos (NOVO)
    workflow.add_node("wait_requirements_approval", wait_requirements_approval)
    workflow.add_node("process_requirements_refinement", process_requirements_refinement)
    
    # Fase 2: Planejamento
    workflow.add_node("create_planning_prompts", create_planning_prompts)
    workflow.add_node("create_plan", create_plan)
    workflow.add_node("review_plan", review_plan)
    
    # Fase 3: Feedback do Plano
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
    
    # ✅ NOVO: Após revisão de requisitos, decidir se precisa refinamento
    workflow.add_conditional_edges(
        "review_requirements",
        route_after_requirements_review,
        {
            "create_planning_prompts": "create_planning_prompts",
            "wait_requirements_approval": "wait_requirements_approval"
        }
    )
    
    # ✅ NOVO: Checkpoint de requisitos
    workflow.add_conditional_edges(
        "wait_requirements_approval",
        route_after_requirements_approval,
        {
            "create_planning_prompts": "create_planning_prompts",
            "process_requirements_refinement": "process_requirements_refinement",
            "wait": END
        }
    )
    
    # ✅ NOVO: Loop de refinamento de requisitos
    workflow.add_edge("process_requirements_refinement", "review_requirements")
    
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
    
    # Checkpoint de aprovação do plano
    workflow.add_conditional_edges(
        "wait_user_approval",
        route_after_user_approval,
        {
            "build_solution": "build_solution",
            "process_feedback": "process_feedback",
            "wait": END
        }
    )
    
    # Loop de feedback do plano
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
    │           GRAFO DE AGENTES - COM CHECKPOINT DE REQUISITOS   │
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
       ├─→ [SE APROVADO]
       │      ↓
       │   (prossegue para planejamento)
       │
       └─→ [SE REJEITADO OU AMBÍGUO]
              ↓
           ┌──────────────────────────┐
           │ wait_requirements_...    │  ← ⏸️ CHECKPOINT 1: Aguarda refinamento
           └──────────────────────────┘
              ↓
              ├─→ [USUÁRIO APROVA MESMO ASSIM]
              │      ↓
              │   (prossegue para planejamento)
              │
              ├─→ [USUÁRIO REFINA DEMANDA]
              │      ↓
              │   ┌──────────────────────────┐
              │   │ process_requirements_... │  ← Reclassifica com demanda refinada
              │   └──────────────────────────┘
              │      ↓
              │      (volta para review_requirements)
              │
              └─→ [AGUARDANDO DECISÃO]
                     ↓
                  [END] ← ⏸️ Grafo pausa aqui
    
    [APÓS APROVAÇÃO DOS REQUISITOS]
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
       │   │ wait_user_approval       │  ← ⏸️ CHECKPOINT 2: Aguarda usuário
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
    
    [APÓS APROVAÇÃO DO PLANO]
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
        "waiting_requirements_refinement": "⏸️ Aguardando refinamento da demanda...",
        "create_planning_prompts": "📝 Criando instruções para o planejador...",
        "create_plan": "📋 Elaborando plano de execução...",
        "review_plan": "🔎 Revisando plano criado...",
        "wait_user_approval": "⏸️ Aguardando sua aprovação do plano...",
        "waiting_approval": "⏸️ Aguardando sua decisão...",
        "process_feedback": "🔄 Processando seu feedback e ajustando...",
        "process_requirements_refinement": "🔄 Reprocessando requisitos...",
        "build_solution": "🔨 Construindo a solução...",
        "review_solution": "👀 Realizando code review...",
        "validate_solution": "✅ Validação final da solução...",
        "completed": "🎉 Processo concluído com sucesso!",
        "error": "❌ Erro no processamento"
    }
    
    return descriptions.get(step, f"Processando: {step}")