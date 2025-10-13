"""
Nós de Construção da Solução
"""
import json
from typing import Dict, Any
from langchain_core.messages import HumanMessage, AIMessage

from core.state import AgentState, Solution, Review, ValidationResult
from core.schemas import SolutionOutput, CodeReviewOutput, ValidationOutput
from utils.llm_factory import create_llm
from utils.logger import log_node_start, log_node_complete, log_node_error, log_llm_call
from prompts.builder import (
    BUILDER_PROMPT_TEMPLATE,
    CODE_REVIEWER_PROMPT,
    FINAL_VALIDATOR_PROMPT
)
from config.llm_config import estimate_cost


def build_solution(state: AgentState) -> Dict[str, Any]:
    """
    Nó 6: Constrói a solução conforme o plano aprovado
    
    Args:
        state: Estado atual do grafo
        
    Returns:
        Atualizações para o estado
    """
    log_node_start("build_solution")
    
    try:
        # Obter modelo configurado
        model_name = state["selected_models"].get("builder", "claude-sonnet-4-5-20250929")
        llm = create_llm(model_name, temperature=0.3, max_tokens=8000)
        
        # Usar with_structured_output
        structured_llm = llm.with_structured_output(SolutionOutput)
        
        # Formatar prompt
        prompt = BUILDER_PROMPT_TEMPLATE.format(
            demand_type=state["demand_type"],
            plan=json.dumps(state["plan"], indent=2),
            requirements=json.dumps(state["requirements"], indent=2)
        )
        
        # Chamar LLM
        log_llm_call("builder", model_name)
        result: SolutionOutput = structured_llm.invoke([HumanMessage(content=prompt)])
        
        # Criar objeto Solution
        solution = Solution(
            code=result.code,
            documentation=result.documentation,
            tests=result.tests,
            dependencies=result.dependencies,
            files=result.files
        )
        
        # Estimar custo
        tokens_in = len(prompt.split()) * 1.3
        tokens_out = 2000  # Estimativa para código
        cost = estimate_cost(model_name, int(tokens_in), int(tokens_out))
        
        # Adicionar ao histórico
        files_count = len(solution.files)
        new_messages = [
            AIMessage(content=f"🔨 Solução construída: {files_count} arquivo(s) gerado(s)")
        ]
        
        log_node_complete("build_solution", {"files": files_count})
        
        return {
            "solution": solution.model_dump(),
            "current_step": "review_solution",
            "messages": new_messages,
            "total_tokens_used": state["total_tokens_used"] + int(tokens_in + tokens_out),
            "total_cost": state["total_cost"] + cost,
        }
        
    except Exception as e:
        log_node_error("build_solution", e)
        return {
            "errors": state["errors"] + [f"Erro ao construir solução: {str(e)}"],
            "current_step": "error"
        }


def review_solution(state: AgentState) -> Dict[str, Any]:
    """
    Nó 7: Revisa a solução construída (code review)
    
    Args:
        state: Estado atual do grafo
        
    Returns:
        Atualizações para o estado
    """
    log_node_start("review_solution")
    
    try:
        # Obter modelo configurado
        model_name = state["selected_models"].get("reviewer", "claude-opus-4-20250514")
        llm = create_llm(model_name, temperature=0.2, max_tokens=4000)
        
        # Usar with_structured_output
        structured_llm = llm.with_structured_output(CodeReviewOutput)
        
        # Formatar prompt
        prompt = CODE_REVIEWER_PROMPT.format(
            requirements=json.dumps(state["requirements"], indent=2),
            plan=json.dumps(state["plan"], indent=2),
            solution=json.dumps(state["solution"], indent=2)
        )
        
        # Chamar LLM
        log_llm_call("solution_reviewer", model_name)
        result: CodeReviewOutput = structured_llm.invoke([HumanMessage(content=prompt)])
        
        # Criar objeto Review (simplificado do CodeReviewOutput)
        review = Review(
            is_approved=result.is_approved,
            confidence_score=result.confidence_score,
            issues_found=[issue.issue for issue in result.issues_found],
            suggestions=[sug.suggestion for sug in result.suggestions],
            strengths=result.strengths
        )
        
        # Estimar custo
        tokens_in = len(prompt.split()) * 1.3
        tokens_out = 800
        cost = estimate_cost(model_name, int(tokens_in), int(tokens_out))
        
        # Adicionar ao histórico
        status = "✅ Aprovado" if review.is_approved else "⚠️ Issues encontrados"
        new_messages = [
            AIMessage(content=f"Code Review: {status} (Score: {review.confidence_score:.0%})")
        ]
        
        log_node_complete("review_solution", {
            "approved": review.is_approved,
            "issues": len(review.issues_found)
        })
        
        # Decidir próximo passo
        next_step = "validate_solution" if review.is_approved else "error"
        
        if not review.is_approved:
            error_msg = f"Solução não aprovada na revisão. Issues: {len(review.issues_found)}"
            return {
                "solution_review": review.model_dump(),
                "warnings": state["warnings"] + [error_msg],
                "current_step": next_step,
                "messages": new_messages,
                "total_tokens_used": state["total_tokens_used"] + int(tokens_in + tokens_out),
                "total_cost": state["total_cost"] + cost,
            }
        
        return {
            "solution_review": review.model_dump(),
            "current_step": next_step,
            "messages": new_messages,
            "total_tokens_used": state["total_tokens_used"] + int(tokens_in + tokens_out),
            "total_cost": state["total_cost"] + cost,
        }
        
    except Exception as e:
        log_node_error("review_solution", e)
        return {
            "errors": state["errors"] + [f"Erro na revisão da solução: {str(e)}"],
            "current_step": "error"
        }


def validate_solution(state: AgentState) -> Dict[str, Any]:
    """
    Nó 8: Validação final da solução
    
    Args:
        state: Estado atual do grafo
        
    Returns:
        Atualizações para o estado
    """
    log_node_start("validate_solution")
    
    try:
        # Obter modelo configurado
        model_name = state["selected_models"].get("reviewer", "claude-opus-4-20250514")
        llm = create_llm(model_name, temperature=0.1)
        
        # Usar with_structured_output
        structured_llm = llm.with_structured_output(ValidationOutput)
        
        # Formatar prompt
        prompt = FINAL_VALIDATOR_PROMPT.format(
            requirements=json.dumps(state["requirements"], indent=2),
            plan=json.dumps(state["plan"], indent=2),
            solution=json.dumps(state["solution"], indent=2),
            code_review=json.dumps(state["solution_review"], indent=2)
        )
        
        # Chamar LLM
        log_llm_call("final_validator", model_name)
        result: ValidationOutput = structured_llm.invoke([HumanMessage(content=prompt)])
        
        # Criar objeto ValidationResult
        validation = ValidationResult(
            is_valid=result.is_valid,
            passed_checks=result.passed_checks,
            failed_checks=[fc.check for fc in result.failed_checks],
            warnings=result.warnings
        )
        
        # Estimar custo
        tokens_in = len(prompt.split()) * 1.3
        tokens_out = 300
        cost = estimate_cost(model_name, int(tokens_in), int(tokens_out))
        
        # Adicionar ao histórico
        status = "✅ Válido" if validation.is_valid else "❌ Inválido"
        new_messages = [
            AIMessage(content=f"Validação Final: {status}")
        ]
        
        log_node_complete("validate_solution", {
            "valid": validation.is_valid,
            "passed": len(validation.passed_checks),
            "failed": len(validation.failed_checks)
        })
        
        # Marcar como concluído
        from datetime import datetime
        
        return {
            "validation_result": validation.model_dump(),
            "current_step": "completed",
            "completed_at": datetime.now(),
            "messages": new_messages,
            "total_tokens_used": state["total_tokens_used"] + int(tokens_in + tokens_out),
            "total_cost": state["total_cost"] + cost,
        }
        
    except Exception as e:
        log_node_error("validate_solution", e)
        return {
            "errors": state["errors"] + [f"Erro na validação final: {str(e)}"],
            "current_step": "error"
        }