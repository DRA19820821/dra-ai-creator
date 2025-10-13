"""
Nós de Classificação e Extração de Requisitos
"""
from typing import Dict, Any
from langchain_core.messages import HumanMessage, AIMessage

from core.state import AgentState, Requirements, Review
from core.schemas import ClassificationOutput, ReviewOutput
from utils.llm_factory import create_llm
from utils.logger import log_node_start, log_node_complete, log_node_error, log_llm_call
from prompts.classifier import CLASSIFIER_PROMPT, REQUIREMENTS_REVIEWER_PROMPT
from config.llm_config import estimate_cost


def classify_and_extract_requirements(state: AgentState) -> Dict[str, Any]:
    """
    Nó 1: Classifica a demanda e extrai requisitos
    
    Args:
        state: Estado atual do grafo
        
    Returns:
        Atualizações para o estado
    """
    log_node_start("classify_and_extract_requirements", {"demand": state["user_demand"][:100]})
    
    try:
        # Obter modelo configurado
        model_name = state["selected_models"].get("classifier", "claude-sonnet-4-5-20250929")
        llm = create_llm(model_name, temperature=0.3)
        
        # Usar with_structured_output para garantir JSON válido
        structured_llm = llm.with_structured_output(ClassificationOutput)
        
        # Formatar prompt
        prompt = CLASSIFIER_PROMPT.format(user_demand=state["user_demand"])
        
        # Chamar LLM com structured output
        log_llm_call("classifier", model_name)
        
        result: ClassificationOutput = structured_llm.invoke([HumanMessage(content=prompt)])
        
        # Criar objeto Requirements
        requirements = Requirements(
            raw_demand=state["user_demand"],
            demand_type=result.demand_type,
            key_requirements=result.key_requirements,
            technologies_mentioned=result.technologies_mentioned,
            constraints=result.constraints,
            expected_outputs=result.expected_outputs,
            confidence_score=result.confidence_score
        )
        
        # Estimar custo (aproximado, structured output pode usar mais tokens)
        tokens_in = len(prompt.split()) * 1.3
        tokens_out = 200  # Estimativa para structured output
        cost = estimate_cost(model_name, int(tokens_in), int(tokens_out))
        
        # Adicionar mensagens ao histórico
        new_messages = [
            HumanMessage(content=f"Demanda do usuário: {state['user_demand']}"),
            AIMessage(content=f"Classificação: {result.demand_type}\nRequisitos extraídos: {len(requirements.key_requirements)} itens")
        ]
        
        log_node_complete("classify_and_extract_requirements", {
            "type": requirements.demand_type,
            "confidence": requirements.confidence_score
        })
        
        return {
            "demand_type": requirements.demand_type,
            "requirements": requirements.model_dump(),
            "current_step": "review_requirements",
            "messages": new_messages,
            "total_tokens_used": state["total_tokens_used"] + int(tokens_in + tokens_out),
            "total_cost": state["total_cost"] + cost,
        }
        
    except Exception as e:
        log_node_error("classify_and_extract_requirements", e)
        return {
            "errors": state["errors"] + [f"Erro na classificação: {str(e)}"],
            "current_step": "error"
        }


def review_requirements(state: AgentState) -> Dict[str, Any]:
    """
    Nó 2: Revisa os requisitos extraídos
    
    Args:
        state: Estado atual do grafo
        
    Returns:
        Atualizações para o estado
    """
    log_node_start("review_requirements")
    
    try:
        # Obter modelo configurado
        model_name = state["selected_models"].get("reviewer", "claude-opus-4-20250514")
        llm = create_llm(model_name, temperature=0.2)
        
        # Usar with_structured_output
        structured_llm = llm.with_structured_output(ReviewOutput)
        
        # Formatar prompt
        import json
        prompt = REQUIREMENTS_REVIEWER_PROMPT.format(
            user_demand=state["user_demand"],
            requirements=json.dumps(state["requirements"], indent=2)
        )
        
        # Chamar LLM com structured output
        log_llm_call("requirements_reviewer", model_name)
        
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
        tokens_out = 150
        cost = estimate_cost(model_name, int(tokens_in), int(tokens_out))
        
        # Adicionar ao histórico
        new_messages = [
            AIMessage(content=f"Revisão de requisitos: {'✅ Aprovado' if review.is_approved else '⚠️ Requer atenção'}")
        ]
        
        log_node_complete("review_requirements", {
            "approved": review.is_approved,
            "confidence": review.confidence_score
        })
        
        # Decidir próximo passo
        next_step = "create_planning_prompts" if review.is_approved else "error"
        
        if not review.is_approved:
            error_msg = f"Requisitos não aprovados. Issues: {', '.join(review.issues_found)}"
            return {
                "requirements_review": review.model_dump(),
                "errors": state["errors"] + [error_msg],
                "current_step": next_step,
                "messages": new_messages,
                "total_tokens_used": state["total_tokens_used"] + int(tokens_in + tokens_out),
                "total_cost": state["total_cost"] + cost,
            }
        
        return {
            "requirements_review": review.model_dump(),
            "current_step": next_step,
            "messages": new_messages,
            "total_tokens_used": state["total_tokens_used"] + int(tokens_in + tokens_out),
            "total_cost": state["total_cost"] + cost,
        }
        
    except Exception as e:
        log_node_error("review_requirements", e)
        return {
            "errors": state["errors"] + [f"Erro na revisão de requisitos: {str(e)}"],
            "current_step": "error"
        }