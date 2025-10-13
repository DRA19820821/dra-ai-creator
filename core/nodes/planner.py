"""
Nós de Planejamento
"""
import json
from typing import Dict, Any
from langchain_core.messages import HumanMessage, AIMessage

from core.state import AgentState, Plan, Review
from core.schemas import PlanningPromptsOutput, PlanOutput, ReviewOutput
from utils.llm_factory import create_llm
from utils.logger import log_node_start, log_node_complete, log_node_error, log_llm_call
from prompts.planner import (
    PLANNING_PROMPT_CREATOR,
    PLANNER_PROMPT_TEMPLATE,
    PLAN_REVIEWER_PROMPT
)
from config.llm_config import estimate_cost


def create_planning_prompts(state: AgentState) -> Dict[str, Any]:
    """
    Nó 3: Cria prompts especializados para o planejador
    
    Args:
        state: Estado atual do grafo
        
    Returns:
        Atualizações para o estado
    """
    log_node_start("create_planning_prompts")
    
    try:
        # Obter modelo configurado
        model_name = state["selected_models"].get("planner", "claude-sonnet-4-5-20250929")
        llm = create_llm(model_name, temperature=0.4)
        
        # Usar with_structured_output
        structured_llm = llm.with_structured_output(PlanningPromptsOutput)
        
        # Formatar prompt
        prompt = PLANNING_PROMPT_CREATOR.format(
            demand_type=state["demand_type"],
            requirements=json.dumps(state["requirements"], indent=2)
        )
        
        # Chamar LLM
        log_llm_call("prompt_creator", model_name)
        result: PlanningPromptsOutput = structured_llm.invoke([HumanMessage(content=prompt)])
        
        # Converter para dict
        planning_prompts = result.model_dump()
        
        # Estimar custo
        tokens_in = len(prompt.split()) * 1.3
        tokens_out = 200
        cost = estimate_cost(model_name, int(tokens_in), int(tokens_out))
        
        log_node_complete("create_planning_prompts")
        
        return {
            "planning_prompts": planning_prompts,
            "current_step": "create_plan",
            "total_tokens_used": state["total_tokens_used"] + int(tokens_in + tokens_out),
            "total_cost": state["total_cost"] + cost,
        }
        
    except Exception as e:
        log_node_error("create_planning_prompts", e)
        return {
            "errors": state["errors"] + [f"Erro ao criar prompts de planejamento: {str(e)}"],
            "current_step": "error"
        }


def create_plan(state: AgentState) -> Dict[str, Any]:
    """
    Nó 4: Cria o plano de execução
    
    Args:
        state: Estado atual do grafo
        
    Returns:
        Atualizações para o estado
    """
    log_node_start("create_plan")
    
    try:
        # Obter modelo configurado
        model_name = state["selected_models"].get("planner", "claude-sonnet-4-5-20250929")
        llm = create_llm(model_name, temperature=0.5, max_tokens=4000)
        
        # Usar with_structured_output
        structured_llm = llm.with_structured_output(PlanOutput)
        
        # Pegar instruções especializadas dos prompts criados
        specialized_instructions = state["planning_prompts"].get(
            "specialized_prompt",
            "Crie um plano detalhado e executável."
        )
        
        # Formatar prompt
        prompt = PLANNER_PROMPT_TEMPLATE.format(
            demand_type=state["demand_type"],
            specialized_instructions=specialized_instructions,
            requirements=json.dumps(state["requirements"], indent=2)
        )
        
        # Chamar LLM
        log_llm_call("planner", model_name)
        result: PlanOutput = structured_llm.invoke([HumanMessage(content=prompt)])
        
        # Converter para Plan
        plan = Plan(
            title=result.title,
            summary=result.summary,
            steps=[step.model_dump() for step in result.steps],
            technologies=result.technologies,
            estimated_complexity=result.estimated_complexity,
            risks=[risk.model_dump() for risk in result.risks],
            prerequisites=result.prerequisites
        )
        
        # Estimar custo
        tokens_in = len(prompt.split()) * 1.3
        tokens_out = 800
        cost = estimate_cost(model_name, int(tokens_in), int(tokens_out))
        
        # Adicionar ao histórico
        new_messages = [
            AIMessage(content=f"📋 Plano criado: {plan.title}\n{len(plan.steps)} passos | Complexidade: {plan.estimated_complexity}")
        ]
        
        log_node_complete("create_plan", {"steps": len(plan.steps)})
        
        return {
            "plan": plan.model_dump(),
            "current_step": "review_plan",
            "messages": new_messages,
            "total_tokens_used": state["total_tokens_used"] + int(tokens_in + tokens_out),
            "total_cost": state["total_cost"] + cost,
        }
        
    except Exception as e:
        log_node_error("create_plan", e)
        return {
            "errors": state["errors"] + [f"Erro ao criar plano: {str(e)}"],
            "current_step": "error"
        }


def review_plan(state: AgentState) -> Dict[str, Any]:
    """
    Nó 5: Revisa o plano criado
    
    Args:
        state: Estado atual do grafo
        
    Returns:
        Atualizações para o estado
    """
    log_node_start("review_plan")
    
    try:
        # Verificar se o plano existe
        if not state.get("plan"):
            log_node_error("review_plan", Exception("Plano não encontrado no estado"))
            return {
                "errors": state["errors"] + ["Plano não encontrado no estado"],
                "current_step": "error"
            }
        
        # Obter modelo configurado (pode ser diferente do planejador)
        model_name = state["selected_models"].get("reviewer", "claude-opus-4-20250514")
        llm = create_llm(model_name, temperature=0.2)
        
        # Usar with_structured_output
        structured_llm = llm.with_structured_output(ReviewOutput)
        
        # Formatar prompt
        prompt = PLAN_REVIEWER_PROMPT.format(
            demand_type=state["demand_type"],
            requirements=json.dumps(state["requirements"], indent=2),
            plan=json.dumps(state["plan"], indent=2)
        )
        
        # Chamar LLM
        log_llm_call("plan_reviewer", model_name)
        result: ReviewOutput = structured_llm.invoke([HumanMessage(content=prompt)])
        
        # Criar objeto Review
        review = Review(
            is_approved=result.is_approved,
            confidence_score=result.confidence_score,
            issues_found=result.issues_found,
            suggestions=result.suggestions,
            strengths=result.strengths
        )
        
        # Estimar custo
        tokens_in = len(prompt.split()) * 1.3
        tokens_out = 200
        cost = estimate_cost(model_name, int(tokens_in), int(tokens_out))
        
        # Adicionar ao histórico
        status = "✅ Aprovado" if review.is_approved else "⚠️ Requer ajustes"
        new_messages = [
            AIMessage(content=f"Revisão do plano: {status} (Confiança: {review.confidence_score:.0%})")
        ]
        
        log_node_complete("review_plan", {
            "approved": review.is_approved,
            "issues": len(review.issues_found)
        })
        
        # Decidir próximo passo
        next_step = "wait_user_approval" if review.is_approved else "process_feedback"
        
        return {
            "plan_review": review.model_dump(),
            "current_step": next_step,
            "messages": new_messages,
            "total_tokens_used": state["total_tokens_used"] + int(tokens_in + tokens_out),
            "total_cost": state["total_cost"] + cost,
        }
        
    except Exception as e:
        log_node_error("review_plan", e)
        return {
            "errors": state["errors"] + [f"Erro na revisão do plano: {str(e)}"],
            "current_step": "error"
        }