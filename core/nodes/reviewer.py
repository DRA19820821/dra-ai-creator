"""
Nó Revisor Genérico - Utilitário para revisões

Este módulo contém funções auxiliares para revisão que podem ser
reutilizadas em diferentes contextos.
"""
import json
from typing import Dict, Any, Optional
from langchain_core.messages import HumanMessage
from langchain_core.language_models.chat_models import BaseChatModel

from utils.logger import log_validation
from config.llm_config import estimate_cost


def generic_review(
    content_to_review: Dict[str, Any],
    review_prompt: str,
    llm: BaseChatModel,
    model_name: str,
    node_name: str,
    min_confidence: float = 0.7
) -> tuple[Dict[str, Any], int, float]:
    """
    Função genérica para realizar revisões usando LLM
    
    Args:
        content_to_review: Conteúdo a ser revisado
        review_prompt: Prompt formatado para a revisão
        llm: Instância do LLM
        model_name: Nome do modelo sendo usado
        node_name: Nome do nó (para logging)
        min_confidence: Confiança mínima para aprovação
        
    Returns:
        Tupla (review_result, tokens_used, cost)
    """
    # Chamar LLM
    response = llm.invoke([HumanMessage(content=review_prompt)])
    response_text = response.content
    
    # Parse JSON
    if "```json" in response_text:
        response_text = response_text.split("```json")[1].split("```")[0]
    elif "```" in response_text:
        response_text = response_text.split("```")[1].split("```")[0]
    
    result = json.loads(response_text.strip())
    
    # Calcular métricas
    tokens_in = len(review_prompt.split()) * 1.3
    tokens_out = len(response_text.split()) * 1.3
    total_tokens = int(tokens_in + tokens_out)
    cost = estimate_cost(model_name, int(tokens_in), int(tokens_out))
    
    # Log da validação
    is_valid = result.get("is_approved", False) and result.get("confidence_score", 0.0) >= min_confidence
    log_validation(
        node_name,
        is_valid,
        f"Confidence: {result.get('confidence_score', 0.0):.0%}"
    )
    
    return result, total_tokens, cost


def check_critical_issues(issues: list) -> bool:
    """
    Verifica se há issues críticos na lista
    
    Args:
        issues: Lista de issues (pode ser strings ou dicts)
        
    Returns:
        True se há issues críticos
    """
    for issue in issues:
        if isinstance(issue, dict):
            severity = issue.get("severity", "").lower()
            if severity == "critical":
                return True
        elif isinstance(issue, str) and "critical" in issue.lower():
            return True
    
    return False


def format_review_summary(review: Dict[str, Any]) -> str:
    """
    Formata um resumo legível da revisão
    
    Args:
        review: Resultado da revisão
        
    Returns:
        String formatada com resumo
    """
    lines = []
    
    # Status
    is_approved = review.get("is_approved", False)
    confidence = review.get("confidence_score", 0.0)
    
    lines.append(f"{'✅ APROVADO' if is_approved else '❌ NÃO APROVADO'}")
    lines.append(f"Confiança: {confidence:.0%}")
    lines.append("")
    
    # Issues
    issues = review.get("issues_found", [])
    if issues:
        lines.append("⚠️ Issues Encontrados:")
        for issue in issues[:5]:  # Primeiros 5
            if isinstance(issue, dict):
                severity = issue.get("severity", "?")
                desc = issue.get("issue", str(issue))
                lines.append(f"  [{severity.upper()}] {desc}")
            else:
                lines.append(f"  • {issue}")
        if len(issues) > 5:
            lines.append(f"  ... e mais {len(issues) - 5} issue(s)")
        lines.append("")
    
    # Sugestões
    suggestions = review.get("suggestions", [])
    if suggestions:
        lines.append("💡 Sugestões:")
        for sug in suggestions[:3]:  # Primeiras 3
            if isinstance(sug, dict):
                desc = sug.get("suggestion", str(sug))
                lines.append(f"  • {desc}")
            else:
                lines.append(f"  • {sug}")
        if len(suggestions) > 3:
            lines.append(f"  ... e mais {len(suggestions) - 3} sugestão(ões)")
        lines.append("")
    
    # Pontos fortes
    strengths = review.get("strengths", [])
    if strengths:
        lines.append("✨ Pontos Fortes:")
        for strength in strengths[:3]:
            lines.append(f"  • {strength}")
        if len(strengths) > 3:
            lines.append(f"  ... e mais {len(strengths) - 3}")
    
    return "\n".join(lines)


def calculate_overall_quality_score(review: Dict[str, Any]) -> float:
    """
    Calcula um score geral de qualidade baseado na revisão
    
    Args:
        review: Resultado da revisão
        
    Returns:
        Score de 0.0 a 1.0
    """
    # Começar com confidence score
    score = review.get("confidence_score", 0.5)
    
    # Penalizar por issues
    issues = review.get("issues_found", [])
    critical_issues = sum(1 for i in issues if isinstance(i, dict) and i.get("severity") == "critical")
    high_issues = sum(1 for i in issues if isinstance(i, dict) and i.get("severity") == "high")
    
    score -= (critical_issues * 0.3)
    score -= (high_issues * 0.15)
    score -= (len(issues) * 0.05)
    
    # Bonificar por strengths
    strengths = review.get("strengths", [])
    score += (len(strengths) * 0.02)
    
    # Code quality scores (se existir)
    if "code_quality_score" in review:
        cqs = review["code_quality_score"]
        if isinstance(cqs, dict) and "overall" in cqs:
            code_score = cqs["overall"] / 10.0
            score = (score + code_score) / 2  # Média
    
    # Limitar entre 0 e 1
    return max(0.0, min(1.0, score))


def should_retry_with_feedback(
    review: Dict[str, Any],
    max_retries: int,
    current_retry: int
) -> tuple[bool, Optional[str]]:
    """
    Determina se deve fazer retry com feedback
    
    Args:
        review: Resultado da revisão
        max_retries: Máximo de retries permitidos
        current_retry: Retry atual
        
    Returns:
        Tupla (should_retry, feedback_message)
    """
    if current_retry >= max_retries:
        return False, None
    
    if review.get("is_approved", False):
        return False, None
    
    # Construir feedback
    issues = review.get("issues_found", [])
    suggestions = review.get("suggestions", [])
    
    feedback_parts = []
    
    if issues:
        feedback_parts.append("Issues encontrados que precisam ser corrigidos:")
        for issue in issues[:5]:
            if isinstance(issue, dict):
                feedback_parts.append(f"- {issue.get('issue', str(issue))}")
            else:
                feedback_parts.append(f"- {issue}")
    
    if suggestions:
        feedback_parts.append("\nSugestões de melhoria:")
        for sug in suggestions[:5]:
            if isinstance(sug, dict):
                feedback_parts.append(f"- {sug.get('suggestion', str(sug))}")
            else:
                feedback_parts.append(f"- {sug}")
    
    feedback = "\n".join(feedback_parts)
    
    return True, feedback