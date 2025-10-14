"""
Nós de Construção da Solução
VERSÃO ULTRA-ROBUSTA - Resolve problema de JSON truncado do Gemini
"""
import json
import re
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
        # String aberta, fechar
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
            return {}
        
        # Caso 2: Tentar parse como JSON
        try:
            parsed = json.loads(value)
            print(f"✅ Parse JSON bem-sucedido para campo '{field_name}'")
            return parsed
        except json.JSONDecodeError as e:
            print(f"⚠️ Parse JSON falhou para '{field_name}': {e}")
            
            # Tentar corrigir JSON truncado
            try:
                fixed = fix_truncated_json(value)
                parsed = json.loads(fixed)
                print(f"✅ JSON truncado corrigido para '{field_name}'")
                return parsed
            except:
                # Não é JSON válido, retornar como string
                return value
    
    # Outros tipos, retornar como está
    return value


def fix_solution_output(raw_dict: dict) -> dict:
    """
    Corrige formato de SolutionOutput garantindo tipos corretos
    
    Args:
        raw_dict: Dicionário com resultado do LLM
        
    Returns:
        Dicionário corrigido
    """
    fixed = raw_dict.copy()
    
    # ✅ CRÍTICO: Parse do campo files se for string
    if 'files' in fixed:
        fixed['files'] = parse_json_field(fixed['files'], 'files')
        
        # Garantir que files é dict
        if not isinstance(fixed['files'], dict):
            if isinstance(fixed['files'], str):
                # String única vira arquivo único
                fixed['files'] = {'main.py': fixed['files']}
            elif isinstance(fixed['files'], list):
                # Lista vira dict numerado
                fixed['files'] = {f'file_{i}.py': str(content) for i, content in enumerate(fixed['files'])}
            else:
                fixed['files'] = {}
    
    # Parse de outros campos que podem estar como JSON string
    if 'dependencies' in fixed and isinstance(fixed['dependencies'], str):
        fixed['dependencies'] = parse_json_field(fixed['dependencies'], 'dependencies')
        if not isinstance(fixed['dependencies'], list):
            # Se não conseguiu parsear como lista, split por newline
            fixed['dependencies'] = [line.strip() for line in fixed['dependencies'].split('\n') if line.strip()]
    
    # Garantir valores default para campos opcionais
    fixed.setdefault('code', None)
    fixed.setdefault('tests', None)
    fixed.setdefault('documentation', '')
    fixed.setdefault('setup_instructions', '')
    fixed.setdefault('usage_examples', '')
    fixed.setdefault('architecture_notes', '')
    fixed.setdefault('dependencies', [])
    fixed.setdefault('files', {})
    
    return fixed


def build_solution(state: AgentState) -> Dict[str, Any]:
    """
    Nó 6: Constrói a solução conforme o plano aprovado
    VERSÃO ULTRA-ROBUSTA - Lida com JSON truncado e múltiplas tentativas
    
    Args:
        state: Estado atual do grafo
        
    Returns:
        Atualizações para o estado
    """
    log_node_start("build_solution")
    
    try:
        # Obter modelo configurado
        model_name = state["selected_models"].get("builder", "gemini-2.5-pro")
        
        # Formatar prompt
        prompt = BUILDER_PROMPT_TEMPLATE.format(
            demand_type=state["demand_type"],
            plan=json.dumps(state["plan"], indent=2),
            requirements=json.dumps(state["requirements"], indent=2)
        )
        
        # Chamar LLM
        log_llm_call("builder", model_name)
        
        # ✅ ESTRATÉGIA MULTI-TENTATIVA
        max_retries = 2
        result_dict = None
        last_error = None
        
        for attempt in range(max_retries):
            # Ajustar max_tokens baseado na tentativa
            # Tentativa 1: 16000 (dobro do original)
            # Tentativa 2: 32000 (se disponível) ou quebrar em partes
            max_tokens = 16000 if attempt == 0 else 32000
            
            print(f"\n🔄 Tentativa {attempt + 1}/{max_retries} (max_tokens={max_tokens})")
            
            try:
                # Criar LLM com configuração específica da tentativa
                llm = create_llm(model_name, temperature=0.3, max_tokens=max_tokens)
                
                # ✅ ESTRATÉGIA 1: Tentar structured_output
                try:
                    structured_llm = llm.with_structured_output(SolutionOutput)
                    result: SolutionOutput = structured_llm.invoke([HumanMessage(content=prompt)])
                    result_dict = result.model_dump()
                    print("✅ Structured output funcionou")
                    break  # Sucesso!
                    
                except Exception as e1:
                    print(f"⚠️ Structured output falhou: {str(e1)[:200]}")
                    
                    # ✅ ESTRATÉGIA 2: Parse manual do JSON
                    try:
                        raw_result = llm.invoke([HumanMessage(content=prompt)])
                        response_text = raw_result.content
                        
                        # Salvar resposta bruta para debug
                        print(f"📝 Resposta bruta: {len(response_text)} caracteres")
                        
                        # Limpar resposta
                        if "```json" in response_text:
                            response_text = response_text.split("```json")[1].split("```")[0]
                        elif "```" in response_text:
                            response_text = response_text.split("```")[1].split("```")[0]
                        
                        # Tentar parse
                        try:
                            result_dict = json.loads(response_text.strip())
                            print("✅ Parse manual funcionou")
                            break  # Sucesso!
                        except json.JSONDecodeError as e2:
                            print(f"⚠️ JSON inválido: {e2}")
                            
                            # ✅ ESTRATÉGIA 3: Tentar corrigir JSON truncado
                            try:
                                fixed_json = fix_truncated_json(response_text.strip())
                                result_dict = json.loads(fixed_json)
                                print("✅ JSON truncado corrigido com sucesso!")
                                break  # Sucesso!
                            except Exception as e3:
                                print(f"❌ Correção de JSON também falhou: {e3}")
                                last_error = f"Structured: {e1}, Manual: {e2}, Fixed: {e3}"
                                
                                # Se não é última tentativa, continuar loop
                                if attempt < max_retries - 1:
                                    print("🔄 Tentando novamente com mais tokens...")
                                    continue
                    
                    except Exception as e2:
                        print(f"❌ Erro ao obter resposta: {e2}")
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
        
        # ✅ ESTRATÉGIA 4: Corrigir formato do resultado
        print(f"📋 Resultado bruto - tipo de files: {type(result_dict.get('files'))}")
        
        # Aplicar correções
        fixed_dict = fix_solution_output(result_dict)
        
        print(f"✅ Resultado corrigido - tipo de files: {type(fixed_dict.get('files'))}")
        print(f"📁 Arquivos detectados: {list(fixed_dict.get('files', {}).keys())}")
        
        # Criar SolutionOutput com dados corrigidos
        try:
            result = SolutionOutput(**fixed_dict)
        except Exception as e:
            print(f"❌ Erro ao criar SolutionOutput: {e}")
            print(f"📋 Dados: {json.dumps(fixed_dict, indent=2, default=str)[:1000]}")
            raise
        
        # ✅ Criar Solution final
        solution = Solution(
            code=result.code,
            documentation=result.documentation,
            tests=result.tests,
            dependencies=result.dependencies if isinstance(result.dependencies, list) else [],
            files=result.files if isinstance(result.files, dict) else {}
        )
        
        # ✅ Garantir que há pelo menos 1 arquivo
        if not solution.files:
            if solution.code:
                solution.files["main.py"] = solution.code
                print("✅ Criado main.py a partir do código principal")
            else:
                solution.files["README.md"] = "# Solução Gerada\n\nDocumentação em desenvolvimento."
                print("⚠️ Nenhum código gerado, criado README placeholder")
        
        # ✅ Adicionar README se não existe
        if "README.md" not in solution.files:
            readme_content = []
            
            if result.documentation:
                readme_content.append(f"# Solução Gerada\n\n{result.documentation}")
            else:
                readme_content.append("# Solução Gerada")
            
            if result.setup_instructions:
                readme_content.append(f"\n## Setup\n\n{result.setup_instructions}")
            
            if result.usage_examples:
                readme_content.append(f"\n## Uso\n\n{result.usage_examples}")
            
            solution.files["README.md"] = "\n".join(readme_content)
            print("✅ README.md adicionado")
        
        # ✅ Adicionar requirements.txt se há dependências
        if solution.dependencies and "requirements.txt" not in solution.files:
            solution.files["requirements.txt"] = "\n".join(solution.dependencies)
            print(f"✅ requirements.txt adicionado com {len(solution.dependencies)} dependências")
        
        # Estimar custo (usar max_tokens da última tentativa bem-sucedida)
        tokens_in = len(prompt.split()) * 1.3
        tokens_out = 3000  # Estimativa conservadora
        cost = estimate_cost(model_name, int(tokens_in), int(tokens_out))
        
        # Adicionar ao histórico
        files_count = len(solution.files)
        new_messages = [
            AIMessage(content=f"🔨 Solução construída: {files_count} arquivo(s) gerado(s)")
        ]
        
        print(f"\n🎉 Solução final: {files_count} arquivos")
        for filename in solution.files.keys():
            size = len(solution.files[filename])
            print(f"   📄 {filename} ({size} chars)")
        
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
        
        # Mostrar traceback completo para debug
        import traceback
        print("\n❌ ERRO COMPLETO:")
        print(traceback.format_exc())
        
        return {
            "errors": state["errors"] + [f"Erro ao construir solução: {str(e)}"],
            "current_step": "error"
        }


def review_solution(state: AgentState) -> Dict[str, Any]:
    """Nó 7: Revisa a solução construída (code review)"""
    log_node_start("review_solution")
    
    try:
        model_name = state["selected_models"].get("reviewer", "gemini-2.5-pro")
        llm = create_llm(model_name, temperature=0.2, max_tokens=4000)
        structured_llm = llm.with_structured_output(CodeReviewOutput)
        
        prompt = CODE_REVIEWER_PROMPT.format(
            requirements=json.dumps(state["requirements"], indent=2),
            plan=json.dumps(state["plan"], indent=2),
            solution=json.dumps(state["solution"], indent=2)
        )
        
        log_llm_call("solution_reviewer", model_name)
        result: CodeReviewOutput = structured_llm.invoke([HumanMessage(content=prompt)])
        
        review = Review(
            is_approved=result.is_approved,
            confidence_score=result.confidence_score,
            issues_found=[issue.issue for issue in result.issues_found],
            suggestions=[sug.suggestion for sug in result.suggestions],
            strengths=result.strengths
        )
        
        tokens_in = len(prompt.split()) * 1.3
        tokens_out = 800
        cost = estimate_cost(model_name, int(tokens_in), int(tokens_out))
        
        status = "✅ Aprovado" if review.is_approved else "⚠️ Issues encontrados"
        new_messages = [AIMessage(content=f"Code Review: {status} (Score: {review.confidence_score:.0%})")]
        
        log_node_complete("review_solution", {"approved": review.is_approved, "issues": len(review.issues_found)})
        
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
    """Nó 8: Validação final da solução"""
    log_node_start("validate_solution")
    
    try:
        model_name = state["selected_models"].get("reviewer", "gemini-2.5-pro")
        llm = create_llm(model_name, temperature=0.1)
        structured_llm = llm.with_structured_output(ValidationOutput)
        
        prompt = FINAL_VALIDATOR_PROMPT.format(
            requirements=json.dumps(state["requirements"], indent=2),
            plan=json.dumps(state["plan"], indent=2),
            solution=json.dumps(state["solution"], indent=2),
            code_review=json.dumps(state["solution_review"], indent=2)
        )
        
        log_llm_call("final_validator", model_name)
        result: ValidationOutput = structured_llm.invoke([HumanMessage(content=prompt)])
        
        validation = ValidationResult(
            is_valid=result.is_valid,
            passed_checks=result.passed_checks,
            failed_checks=[fc.check for fc in result.failed_checks],
            warnings=result.warnings
        )
        
        tokens_in = len(prompt.split()) * 1.3
        tokens_out = 300
        cost = estimate_cost(model_name, int(tokens_in), int(tokens_out))
        
        status = "✅ Válido" if validation.is_valid else "❌ Inválido"
        new_messages = [AIMessage(content=f"Validação Final: {status}")]
        
        log_node_complete("validate_solution", {
            "valid": validation.is_valid,
            "passed": len(validation.passed_checks),
            "failed": len(validation.failed_checks)
        })
        
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