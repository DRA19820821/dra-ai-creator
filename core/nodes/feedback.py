"""
Nós de Processamento de Feedback do Usuário
VERSÃO CORRIGIDA - Tratamento robusto de None
"""
import json
from typing import Dict, Any
from langchain_core.messages import HumanMessage, AIMessage

from core.state import AgentState
from core.schemas import PlanOutput
from utils.llm_factory import create_llm
from utils.logger import log_node_start, log_node_complete, log_node_error, log_llm_call
from config.llm_config import estimate_cost


def wait_user_approval(state: AgentState) -> Dict[str, Any]:
    """
    Nó que aguarda aprovação do usuário (checkpoint)
    
    Este é um nó de controle que não executa nada.
    O fluxo é pausado aqui até que o usuário:
    - Aprove o plano (user_approved=True)
    - Ou solicite ajustes (user_feedback com texto)
    
    Args:
        state: Estado atual do grafo
        
    Returns:
        Atualizações para o estado
    """
    log_node_start("wait_user_approval")
    
    # Esse nó é apenas um marcador
    # A lógica de decisão está no roteamento do grafo
    
    log_node_complete("wait_user_approval")
    
    return {
        "current_step": "waiting_approval"
    }


def process_feedback(state: AgentState) -> Dict[str, Any]:
    """
    Processa o feedback do usuário e ajusta o plano
    VERSÃO ROBUSTA - Tratamento completo de erros
    
    Args:
        state: Estado atual do grafo
        
    Returns:
        Atualizações para o estado
    """
    log_node_start("process_feedback", {"feedback": state.get("user_feedback", "")[:100]})
    
    try:
        # ✅ VERIFICAR SE STATE E PLAN EXISTEM
        if not state:
            raise ValueError("State is None")
        
        if not state.get("plan"):
            raise ValueError("Plan not found in state")
        
        # Verificar se há feedback
        user_feedback = state.get("user_feedback", "")
        if not user_feedback:
            # Se não há feedback mas chegou aqui, é porque foi rejeitado pela revisão
            # Usar issues da revisão como feedback
            plan_review = state.get("plan_review", {})
            if not plan_review:
                # ✅ FALLBACK: Se nem review existe, usar feedback genérico
                user_feedback = "Por favor, revise e melhore o plano considerando os requisitos."
            else:
                issues = plan_review.get("issues_found", [])
                suggestions = plan_review.get("suggestions", [])
                
                feedback_parts = ["Ajustes necessários baseados na revisão:"]
                feedback_parts.extend([f"- {issue}" for issue in issues[:5]])
                feedback_parts.extend([f"Sugestão: {sug}" for sug in suggestions[:3]])
                
                user_feedback = "\n".join(feedback_parts)
        
        # Obter modelo configurado
        model_name = state["selected_models"].get("planner", "gemini-2.5-pro")
        llm = create_llm(model_name, temperature=0.5, max_tokens=4000)
        
        # Usar with_structured_output
        structured_llm = llm.with_structured_output(PlanOutput)
        
        # Criar prompt para ajustar o plano
        adjust_prompt = f"""Você é um especialista em planejamento técnico.

Você criou um plano, mas recebeu feedback solicitando ajustes.

## PLANO ORIGINAL:
{json.dumps(state["plan"], indent=2)}

## FEEDBACK RECEBIDO:
{user_feedback}

## SUA TAREFA:
Ajustar o plano incorporando o feedback. Mantenha o que está bom e modifique apenas o necessário.

Retorne o plano ajustado no mesmo formato, com todos os campos preenchidos."""
        
        # Chamar LLM com structured output
        log_llm_call("feedback_processor", model_name)
        
        # ✅ MULTI-TENTATIVA
        max_retries = 2
        adjusted_plan = None
        
        for attempt in range(max_retries):
            try:
                result = structured_llm.invoke([HumanMessage(content=adjust_prompt)])
                
                # ✅ VERIFICAR SE RETORNOU NONE
                if result is None:
                    print(f"⚠️ Tentativa {attempt + 1}: Structured output retornou None")
                    if attempt < max_retries - 1:
                        continue
                    # ✅ FALLBACK: Manter plano original com aviso
                    adjusted_plan = state["plan"].copy()
                    break
                
                # Converter para dict
                adjusted_plan = result.model_dump()
                
                # ✅ Converter steps e risks se necessário
                if hasattr(result, 'steps') and result.steps:
                    if hasattr(result.steps[0], 'model_dump'):
                        adjusted_plan['steps'] = [step.model_dump() for step in result.steps]
                
                if hasattr(result, 'risks') and result.risks:
                    if hasattr(result.risks[0], 'model_dump'):
                        adjusted_plan['risks'] = [risk.model_dump() for risk in result.risks]
                
                print(f"✅ Plano ajustado com sucesso")
                break
                
            except Exception as e:
                print(f"⚠️ Erro na tentativa {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    continue
                # ✅ FALLBACK FINAL: Manter plano original
                adjusted_plan = state["plan"].copy()
                break
        
        # ✅ GARANTIR QUE adjusted_plan NÃO É NONE
        if adjusted_plan is None:
            print("⚠️ Usando plano original como fallback")
            adjusted_plan = state["plan"].copy()
        
        # Estimar custo
        tokens_in = len(adjust_prompt.split()) * 1.3
        tokens_out = 800
        cost = estimate_cost(model_name, int(tokens_in), int(tokens_out))
        
        # Incrementar contador de iterações
        new_iteration = state.get("feedback_iteration", 0) + 1
        
        # Adicionar ao histórico
        new_messages = [
            HumanMessage(content=f"Feedback do usuário: {user_feedback[:200]}..."),
            AIMessage(content=f"🔄 Plano ajustado (iteração {new_iteration})")
        ]
        
        log_node_complete("process_feedback", {"iteration": new_iteration})
        
        # Limitar iterações para evitar loop infinito
        MAX_ITERATIONS = 3
        if new_iteration >= MAX_ITERATIONS:
            return {
                "plan": adjusted_plan,
                "feedback_iteration": new_iteration,
                "warnings": state.get("warnings", []) + [
                    f"Atingido limite de {MAX_ITERATIONS} iterações de feedback"
                ],
                "current_step": "build_solution",  # Força prosseguir
                "messages": new_messages,
                "total_tokens_used": state.get("total_tokens_used", 0) + int(tokens_in + tokens_out),
                "total_cost": state.get("total_cost", 0.0) + cost,
            }
        
        return {
            "plan": adjusted_plan,
            "feedback_iteration": new_iteration,
            "user_feedback": None,  # Limpar feedback
            "user_approved": False,  # Resetar aprovação
            "current_step": "review_plan",  # Volta para revisão
            "messages": new_messages,
            "total_tokens_used": state.get("total_tokens_used", 0) + int(tokens_in + tokens_out),
            "total_cost": state.get("total_cost", 0.0) + cost,
        }
        
    except Exception as e:
        log_node_error("process_feedback", e)
        
        import traceback
        print("\n❌ ERRO COMPLETO:")
        print(traceback.format_exc())
        
        # ✅ FALLBACK: Retornar erro mas não travar
        return {
            "errors": state.get("errors", []) + [f"Erro ao processar feedback: {str(e)}"],
            "warnings": state.get("warnings", []) + ["Feedback não processado - prosseguindo"],
            "current_step": "build_solution",  # Prosseguir mesmo com erro
        }


def route_after_plan_review(state: AgentState) -> str:
    """
    Função de roteamento após revisão do plano
    VERSÃO ROBUSTA
    
    Args:
        state: Estado atual
        
    Returns:
        Nome do próximo nó
    """
    # ✅ VERIFICAR SE STATE EXISTE
    if not state:
        return "process_feedback"
    
    plan_review = state.get("plan_review", {})
    
    # ✅ VERIFICAR SE REVIEW EXISTE
    if not plan_review:
        # Se não tem review, assumir aprovado
        return "wait_user_approval"
    
    is_approved = plan_review.get("is_approved", False)
    
    if is_approved:
        return "wait_user_approval"
    else:
        return "process_feedback"


def route_after_user_approval(state: AgentState) -> str:
    """
    Função de roteamento após checkpoint de aprovação do usuário
    VERSÃO ROBUSTA
    
    Args:
        state: Estado atual
        
    Returns:
        Nome do próximo nó ou "wait" para pausar
    """
    # ✅ VERIFICAR SE STATE EXISTE
    if not state:
        return "wait"
    
    # Se aprovado explicitamente, prosseguir
    if state.get("user_approved", False):
        return "build_solution"
    
    # Se há feedback, processar
    if state.get("user_feedback"):
        return "process_feedback"
    
    # Se nenhum dos dois, terminar e aguardar decisão do usuário
    return "wait"