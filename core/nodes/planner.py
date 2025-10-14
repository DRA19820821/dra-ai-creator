"""
Nós de Planejamento
VERSÃO ULTRA-ROBUSTA - Resolve problema de None no structured output
"""
import json
import re
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


def fix_truncated_json(json_str: str) -> str:
    """
    Tenta corrigir JSON truncado adicionando fechamentos
    
    Args:
        json_str: String JSON possivelmente truncada
        
    Returns:
        JSON corrigido
    """
    # Contar abertura e fechamento de chaves/colchetes
    open_braces = json_str.count('{')
    close_braces = json_str.count('}')
    open_brackets = json_str.count('[')
    close_brackets = json_str.count(']')
    
    # Adicionar fechamentos faltando
    fixed = json_str
    
    # Fechar strings abertas
    quote_count = json_str.count('"')
    if quote_count % 2 != 0:
        fixed += '"'
    
    # Fechar colchetes
    if open_brackets > close_brackets:
        fixed += ']' * (open_brackets - close_brackets)
    
    # Fechar chaves
    if open_braces > close_braces:
        fixed += '}' * (open_braces - close_braces)
    
    return fixed


def parse_json_field(value: Any, field_name: str = "unknown") -> Any:
    """
    Parse robusto de campo que pode ser JSON string
    
    Args:
        value: Valor a ser parseado
        field_name: Nome do campo (para logging)
        
    Returns:
        Valor parseado corretamente
    """
    # Se já é dict ou list, retornar como está
    if isinstance(value, (dict, list)):
        return value
    
    # Se é None, retornar None
    if value is None:
        return None
    
    # Se é string, tentar parse
    if isinstance(value, str):
        # Caso 1: String vazia
        if not value.strip():
            return []
        
        # Caso 2: Tentar parse como JSON
        try:
            parsed = json.loads(value)
            return parsed
        except json.JSONDecodeError:
            # Não é JSON válido, retornar como string
            return value
    
    # Outros tipos, retornar como está
    return value


def robust_parse_plan_output(raw_response: Any, prompt: str) -> Dict[str, Any]:
    """
    Parse robusto da resposta do LLM para criar plano
    VERSÃO MELHORADA - Extrai dados mesmo de PlanOutput
    
    Args:
        raw_response: Resposta bruta do LLM
        prompt: Prompt usado (para fallback)
        
    Returns:
        Dict com dados do plano
    """
    # Caso 1: Já é um dict (parsing direto funcionou)
    if isinstance(raw_response, dict):
        print("✅ Resposta já é dict")
        return raw_response
    
    # Caso 2: É um objeto PlanOutput (ou qualquer Pydantic model)
    if hasattr(raw_response, 'model_dump'):
        print("✅ Resposta é objeto Pydantic")
        result = raw_response.model_dump()
        
        # ✅ CRÍTICO: Processar campos que podem ser objetos Pydantic
        if 'steps' in result and result['steps']:
            # Se steps são objetos, converter para dict
            if hasattr(result['steps'][0], 'model_dump'):
                result['steps'] = [step.model_dump() for step in raw_response.steps]
                print(f"✅ Convertidos {len(result['steps'])} steps de objetos para dict")
        
        if 'risks' in result and result['risks']:
            # Se risks são objetos, converter para dict
            if hasattr(result['risks'][0], 'model_dump'):
                result['risks'] = [risk.model_dump() for risk in raw_response.risks]
                print(f"✅ Convertidos {len(result['risks'])} risks de objetos para dict")
        
        return result
    
    # Caso 3: É uma string (resposta de texto)
    if isinstance(raw_response, str):
        response_text = raw_response
    elif hasattr(raw_response, 'content'):
        response_text = raw_response.content
    else:
        raise ValueError(f"Tipo de resposta não suportado: {type(raw_response)}")
    
    print(f"📝 Resposta como texto: {len(response_text)} caracteres")
    
    # Limpar resposta
    if "```json" in response_text:
        response_text = response_text.split("```json")[1].split("```")[0]
    elif "```" in response_text:
        response_text = response_text.split("```")[1].split("```")[0]
    
    # Tentar parse
    try:
        result_dict = json.loads(response_text.strip())
        print("✅ Parse JSON manual bem-sucedido")
        return result_dict
    except json.JSONDecodeError as e:
        print(f"⚠️ JSON inválido: {e}")
        
        # Tentar corrigir JSON truncado
        try:
            fixed_json = fix_truncated_json(response_text.strip())
            result_dict = json.loads(fixed_json)
            print("✅ JSON truncado corrigido com sucesso!")
            return result_dict
        except:
            raise ValueError(f"Não foi possível fazer parse da resposta após múltiplas tentativas")


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
        model_name = state["selected_models"].get("planner", "gemini-2.5-pro")
        
        # Formatar prompt
        prompt = PLANNING_PROMPT_CREATOR.format(
            demand_type=state["demand_type"],
            requirements=json.dumps(state["requirements"], indent=2)
        )
        
        # Chamar LLM
        log_llm_call("prompt_creator", model_name)
        
        # ✅ ESTRATÉGIA MULTI-TENTATIVA
        max_retries = 2
        result_dict = None
        last_error = None
        
        for attempt in range(max_retries):
            max_tokens = 8000 if attempt == 0 else 16000
            
            print(f"\n🔄 Tentativa {attempt + 1}/{max_retries} (max_tokens={max_tokens})")
            
            try:
                llm = create_llm(model_name, temperature=0.4, max_tokens=max_tokens)
                
                # ✅ ESTRATÉGIA 1: Tentar structured_output
                try:
                    structured_llm = llm.with_structured_output(PlanningPromptsOutput)
                    result = structured_llm.invoke([HumanMessage(content=prompt)])
                    
                    if result is not None:
                        result_dict = result.model_dump() if hasattr(result, 'model_dump') else result
                        print("✅ Structured output funcionou")
                        break
                    else:
                        print("⚠️ Structured output retornou None")
                        
                except Exception as e1:
                    print(f"⚠️ Structured output falhou: {str(e1)[:200]}")
                
                # ✅ ESTRATÉGIA 2: Parse manual
                try:
                    raw_result = llm.invoke([HumanMessage(content=prompt)])
                    result_dict = robust_parse_plan_output(raw_result, prompt)
                    print("✅ Parse manual funcionou")
                    break
                    
                except Exception as e2:
                    print(f"⚠️ Parse manual falhou: {e2}")
                    last_error = str(e2)
                    if attempt < max_retries - 1:
                        continue
            
            except Exception as e:
                print(f"❌ Erro geral na tentativa {attempt + 1}: {e}")
                last_error = str(e)
                if attempt < max_retries - 1:
                    continue
        
        # Se todas as tentativas falharam
        if result_dict is None:
            raise Exception(f"Todas as {max_retries} tentativas falharam. Último erro: {last_error}")
        
        # Garantir campos obrigatórios
        result_dict.setdefault('specialized_prompt', 'Crie um plano detalhado e executável.')
        result_dict.setdefault('key_points_to_address', [])
        result_dict.setdefault('suggested_plan_structure', [])
        result_dict.setdefault('critical_considerations', [])
        
        # Estimar custo
        tokens_in = len(prompt.split()) * 1.3
        tokens_out = 200
        cost = estimate_cost(model_name, int(tokens_in), int(tokens_out))
        
        log_node_complete("create_planning_prompts")
        
        return {
            "planning_prompts": result_dict,
            "current_step": "create_plan",
            "total_tokens_used": state["total_tokens_used"] + int(tokens_in + tokens_out),
            "total_cost": state["total_cost"] + cost,
        }
        
    except Exception as e:
        log_node_error("create_planning_prompts", e)
        import traceback
        print("\n❌ ERRO COMPLETO:")
        print(traceback.format_exc())
        
        return {
            "errors": state["errors"] + [f"Erro ao criar prompts de planejamento: {str(e)}"],
            "current_step": "error"
        }


def create_plan(state: AgentState) -> Dict[str, Any]:
    """
    Nó 4: Cria o plano de execução
    VERSÃO ULTRA-ROBUSTA
    
    Args:
        state: Estado atual do grafo
        
    Returns:
        Atualizações para o estado
    """
    log_node_start("create_plan")
    
    try:
        # Obter modelo configurado
        model_name = state["selected_models"].get("planner", "gemini-2.5-pro")
        
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
        
        # ✅ ESTRATÉGIA MULTI-TENTATIVA
        max_retries = 2
        result_dict = None
        last_error = None
        
        for attempt in range(max_retries):
            max_tokens = 8000 if attempt == 0 else 16000
            
            print(f"\n🔄 Tentativa {attempt + 1}/{max_retries} (max_tokens={max_tokens})")
            
            try:
                llm = create_llm(model_name, temperature=0.5, max_tokens=max_tokens)
                
                # ✅ ESTRATÉGIA 1: Tentar structured_output
                try:
                    structured_llm = llm.with_structured_output(PlanOutput)
                    result = structured_llm.invoke([HumanMessage(content=prompt)])
                    
                    # ✅ VERIFICAR SE RETORNOU NONE
                    if result is None:
                        print("⚠️ Structured output retornou None")
                        raise ValueError("Structured output returned None")
                    
                    result_dict = result.model_dump() if hasattr(result, 'model_dump') else result
                    print("✅ Structured output funcionou")
                    break
                    
                except Exception as e1:
                    print(f"⚠️ Structured output falhou: {str(e1)[:200]}")
                
                # ✅ ESTRATÉGIA 2: Parse manual do JSON
                try:
                    raw_result = llm.invoke([HumanMessage(content=prompt)])
                    result_dict = robust_parse_plan_output(raw_result, prompt)
                    print("✅ Parse manual funcionou")
                    break
                    
                except Exception as e2:
                    print(f"⚠️ Parse manual falhou: {e2}")
                    last_error = str(e2)
                    if attempt < max_retries - 1:
                        continue
            
            except Exception as e:
                print(f"❌ Erro geral na tentativa {attempt + 1}: {e}")
                last_error = str(e)
                if attempt < max_retries - 1:
                    continue
        
        # Se todas as tentativas falharam
        if result_dict is None:
            raise Exception(f"Todas as {max_retries} tentativas falharam. Último erro: {last_error}")
        
        # ✅ PROCESSAR E VALIDAR CAMPOS
        
        # Parse de campos que podem ser JSON strings
        if 'steps' in result_dict:
            result_dict['steps'] = parse_json_field(result_dict['steps'], 'steps')
            # Garantir que é lista de dicts
            if not isinstance(result_dict['steps'], list):
                result_dict['steps'] = []
        
        if 'risks' in result_dict:
            result_dict['risks'] = parse_json_field(result_dict['risks'], 'risks')
            # Garantir que é lista de dicts
            if not isinstance(result_dict['risks'], list):
                result_dict['risks'] = []
        
        if 'technologies' in result_dict:
            result_dict['technologies'] = parse_json_field(result_dict['technologies'], 'technologies')
            if not isinstance(result_dict['technologies'], list):
                result_dict['technologies'] = []
        
        if 'prerequisites' in result_dict:
            result_dict['prerequisites'] = parse_json_field(result_dict['prerequisites'], 'prerequisites')
            if not isinstance(result_dict['prerequisites'], list):
                result_dict['prerequisites'] = []
        
        # ✅ GARANTIR VALORES DEFAULT
        result_dict.setdefault('title', 'Plano de Execução')
        result_dict.setdefault('summary', 'Plano detalhado para atender a demanda')
        result_dict.setdefault('steps', [])
        result_dict.setdefault('technologies', [])
        result_dict.setdefault('estimated_complexity', 'medium')
        result_dict.setdefault('risks', [])
        result_dict.setdefault('prerequisites', [])
        
        # ✅ CRIAR OBJETO PLAN
        plan = Plan(**result_dict)
        
        # Estimar custo
        tokens_in = len(prompt.split()) * 1.3
        tokens_out = 800
        cost = estimate_cost(model_name, int(tokens_in), int(tokens_out))
        
        # Adicionar ao histórico
        new_messages = [
            AIMessage(content=f"📋 Plano criado: {plan.title}\n{len(plan.steps)} passos | Complexidade: {plan.estimated_complexity}")
        ]
        
        print(f"\n🎉 Plano criado: {plan.title} ({len(plan.steps)} passos)")
        
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
        
        # Mostrar traceback completo para debug
        import traceback
        print("\n❌ ERRO COMPLETO:")
        print(traceback.format_exc())
        
        return {
            "errors": state["errors"] + [f"Erro ao criar plano: {str(e)}"],
            "current_step": "error"
        }


def review_plan(state: AgentState) -> Dict[str, Any]:
    """
    Nó 5: Revisa o plano criado
    VERSÃO ULTRA-ROBUSTA - Com tratamento completo de erros e fallback
    
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
        
        # Obter modelo configurado
        model_name = state["selected_models"].get("reviewer", "gemini-2.5-pro")
        
        # Formatar prompt
        prompt = PLAN_REVIEWER_PROMPT.format(
            demand_type=state["demand_type"],
            requirements=json.dumps(state["requirements"], indent=2),
            plan=json.dumps(state["plan"], indent=2)
        )
        
        # Chamar LLM
        log_llm_call("plan_reviewer", model_name)
        
        # ✅ ESTRATÉGIA MULTI-TENTATIVA COM FALLBACK COMPLETO
        max_retries = 2
        result_dict = None
        
        for attempt in range(max_retries):
            max_tokens = 8000 if attempt == 0 else 16000
            
            print(f"\n🔄 Review - Tentativa {attempt + 1}/{max_retries} (max_tokens={max_tokens})")
            
            try:
                llm = create_llm(model_name, temperature=0.2, max_tokens=max_tokens)
                
                # ✅ ESTRATÉGIA 1: Tentar structured output
                try:
                    structured_llm = llm.with_structured_output(ReviewOutput)
                    result = structured_llm.invoke([HumanMessage(content=prompt)])
                    
                    if result is not None:
                        result_dict = result.model_dump() if hasattr(result, 'model_dump') else result
                        print("✅ Structured output funcionou")
                        break
                    else:
                        print("⚠️ Structured output retornou None")
                except Exception as e1:
                    print(f"⚠️ Structured output falhou: {str(e1)[:100]}")
                
                # ✅ ESTRATÉGIA 2: Parse manual
                try:
                    raw_result = llm.invoke([HumanMessage(content=prompt)])
                    response_text = raw_result.content if hasattr(raw_result, 'content') else str(raw_result)
                    
                    print(f"📝 Resposta texto: {len(response_text)} caracteres")
                    
                    # ✅ VERIFICAR SE RESPOSTA ESTÁ VAZIA
                    if not response_text or len(response_text.strip()) < 10:
                        print("⚠️ Resposta vazia ou muito curta")
                        raise ValueError("Empty response from LLM")
                    
                    # Limpar e parsear
                    if "```json" in response_text:
                        response_text = response_text.split("```json")[1].split("```")[0]
                    elif "```" in response_text:
                        response_text = response_text.split("```")[1].split("```")[0]
                    
                    # ✅ VERIFICAR NOVAMENTE APÓS LIMPEZA
                    cleaned = response_text.strip()
                    if not cleaned:
                        print("⚠️ Texto vazio após limpeza")
                        raise ValueError("Empty text after cleaning")
                    
                    result_dict = json.loads(cleaned)
                    print("✅ Parse manual funcionou")
                    break
                    
                except json.JSONDecodeError as e2:
                    print(f"⚠️ JSON inválido: {e2}")
                    
                    # ✅ ESTRATÉGIA 3: Tentar corrigir JSON
                    try:
                        fixed_json = fix_truncated_json(response_text.strip())
                        result_dict = json.loads(fixed_json)
                        print("✅ JSON corrigido funcionou")
                        break
                    except Exception as e3:
                        print(f"⚠️ Correção de JSON falhou: {e3}")
                        if attempt < max_retries - 1:
                            continue
                        raise
                
                except Exception as e2:
                    print(f"⚠️ Parse manual falhou: {e2}")
                    if attempt < max_retries - 1:
                        continue
                    raise
                    
            except Exception as e:
                print(f"❌ Erro geral na tentativa {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    continue
                # ✅ ÚLTIMA TENTATIVA FALHOU - USAR DEFAULTS
                print("⚠️ Todas as tentativas falharam - usando review padrão")
                result_dict = {
                    "is_approved": True,  # Aprovar por padrão para não travar
                    "confidence_score": 0.7,
                    "issues_found": [],
                    "suggestions": ["Review automático falhou - plano aprovado por padrão"],
                    "strengths": ["Plano estruturado presente"],
                    "reasoning": "Review automático não disponível - aprovado por padrão"
                }
                break
        
        # ✅ GARANTIR CAMPOS OBRIGATÓRIOS
        if result_dict is None:
            result_dict = {}
        
        result_dict.setdefault('is_approved', True)
        result_dict.setdefault('confidence_score', 0.8)
        result_dict.setdefault('issues_found', [])
        result_dict.setdefault('suggestions', [])
        result_dict.setdefault('strengths', [])
        result_dict.setdefault('reasoning', 'Review concluído')
        
        # Criar objeto Review
        review = Review(**result_dict)
        
        # Estimar custo
        tokens_in = len(prompt.split()) * 1.3
        tokens_out = 200
        cost = estimate_cost(model_name, int(tokens_in), int(tokens_out))
        
        # Adicionar ao histórico
        status = "✅ Aprovado" if review.is_approved else "⚠️ Requer ajustes"
        new_messages = [
            AIMessage(content=f"Revisão do plano: {status} (Confiança: {review.confidence_score:.0%})")
        ]
        
        print(f"\n✅ Review concluído: {status}")
        
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
        
        import traceback
        print("\n❌ ERRO COMPLETO:")
        print(traceback.format_exc())
        
        # ✅ FALLBACK FINAL: Aprovar com warning
        print("⚠️ Usando fallback final - aprovando plano com warning")
        
        fallback_review = Review(
            is_approved=True,
            confidence_score=0.7,
            issues_found=[],
            suggestions=["Review automático falhou"],
            strengths=["Plano presente"]
        )
        
        return {
            "plan_review": fallback_review.model_dump(),
            "warnings": state["warnings"] + [f"Review falhou mas plano foi aprovado: {str(e)}"],
            "current_step": "wait_user_approval",
            "messages": [AIMessage(content="⚠️ Review automático falhou - plano aprovado com warning")],
            "total_tokens_used": state["total_tokens_used"] + 500,
            "total_cost": state["total_cost"] + 0.01,
        }