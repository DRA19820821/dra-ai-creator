"""
Schemas Pydantic para Structured Output dos LLMs
"""
from typing import List, Literal, Optional
from pydantic import BaseModel, Field


# ============================================
# SCHEMAS PARA CLASSIFICAÇÃO
# ============================================

class ClassificationOutput(BaseModel):
    """Schema para output do classificador"""
    demand_type: Literal["analysis", "software", "data_pipeline", "unknown"] = Field(
        description="Tipo de demanda identificado"
    )
    confidence_score: float = Field(
        ge=0.0, le=1.0,
        description="Confiança na classificação (0.0 a 1.0)"
    )
    key_requirements: List[str] = Field(
        description="Lista de requisitos principais extraídos"
    )
    technologies_mentioned: List[str] = Field(
        default_factory=list,
        description="Tecnologias mencionadas na demanda"
    )
    constraints: List[str] = Field(
        default_factory=list,
        description="Restrições e limitações identificadas"
    )
    expected_outputs: List[str] = Field(
        default_factory=list,
        description="Outputs esperados da solução"
    )
    reasoning: str = Field(
        description="Breve explicação da classificação"
    )


class ReviewOutput(BaseModel):
    """Schema para output de revisão"""
    is_approved: bool = Field(
        description="Se o item revisado foi aprovado"
    )
    confidence_score: float = Field(
        ge=0.0, le=1.0,
        description="Confiança na avaliação (0.0 a 1.0)"
    )
    issues_found: List[str] = Field(
        default_factory=list,
        description="Lista de problemas encontrados"
    )
    suggestions: List[str] = Field(
        default_factory=list,
        description="Sugestões de melhoria"
    )
    strengths: List[str] = Field(
        default_factory=list,
        description="Pontos fortes identificados"
    )
    reasoning: str = Field(
        default="",
        description="Análise detalhada"
    )


# ============================================
# SCHEMAS PARA PLANEJAMENTO
# ============================================

class PlanningPromptsOutput(BaseModel):
    """Schema para prompts de planejamento"""
    specialized_prompt: str = Field(
        description="Prompt especializado detalhado para o planejador"
    )
    key_points_to_address: List[str] = Field(
        default_factory=list,
        description="Pontos-chave que devem ser abordados"
    )
    suggested_plan_structure: List[str] = Field(
        default_factory=list,
        description="Estrutura sugerida para o plano"
    )
    critical_considerations: List[str] = Field(
        default_factory=list,
        description="Considerações críticas"
    )


class PlanStep(BaseModel):
    """Schema para um passo do plano"""
    step_number: int = Field(description="Número do passo")
    title: str = Field(description="Título do passo")
    description: str = Field(description="Descrição detalhada")
    deliverables: List[str] = Field(
        default_factory=list,
        description="Entregas esperadas"
    )
    estimated_effort: Literal["low", "medium", "high"] = Field(
        default="medium",
        description="Esforço estimado"
    )
    dependencies: List[str] = Field(
        default_factory=list,
        description="Dependências de outros passos"
    )


class RiskItem(BaseModel):
    """Schema para um risco"""
    risk: str = Field(description="Descrição do risco")
    mitigation: str = Field(description="Estratégia de mitigação")


class PlanOutput(BaseModel):
    """Schema para output do planejador"""
    title: str = Field(description="Título do plano")
    summary: str = Field(description="Resumo executivo")
    steps: List[PlanStep] = Field(
        description="Lista de passos do plano"
    )
    technologies: List[str] = Field(
        default_factory=list,
        description="Tecnologias a serem utilizadas"
    )
    estimated_complexity: Literal["low", "medium", "high", "very_high"] = Field(
        default="medium",
        description="Complexidade estimada"
    )
    risks: List[RiskItem] = Field(
        default_factory=list,
        description="Riscos identificados e mitigações"
    )
    prerequisites: List[str] = Field(
        default_factory=list,
        description="Pré-requisitos necessários"
    )
    success_criteria: List[str] = Field(
        default_factory=list,
        description="Critérios de sucesso"
    )


# ============================================
# SCHEMAS PARA CONSTRUÇÃO
# ============================================

class SolutionOutput(BaseModel):
    """Schema para output do construtor"""
    code: Optional[str] = Field(
        None,
        description="Código principal (se aplicável)"
    )
    files: dict[str, str] = Field(
        default_factory=dict,
        description="Arquivos gerados (filename: content)"
    )
    documentation: str = Field(
        default="",
        description="Documentação geral da solução"
    )
    tests: Optional[str] = Field(
        None,
        description="Código de testes (se aplicável)"
    )
    dependencies: List[str] = Field(
        default_factory=list,
        description="Lista de dependências (formato requirements.txt)"
    )
    setup_instructions: str = Field(
        default="",
        description="Instruções de setup passo a passo"
    )
    usage_examples: str = Field(
        default="",
        description="Exemplos de uso"
    )
    architecture_notes: str = Field(
        default="",
        description="Notas sobre arquitetura e decisões técnicas"
    )


class CodeIssue(BaseModel):
    """Schema para um issue de código"""
    severity: Literal["critical", "high", "medium", "low"] = Field(
        description="Severidade do issue"
    )
    category: Literal["functionality", "quality", "security", "performance", "documentation"] = Field(
        description="Categoria do issue"
    )
    issue: str = Field(description="Descrição do problema")
    file: str = Field(default="", description="Arquivo afetado")
    line: Optional[int] = Field(None, description="Linha afetada")
    fix_suggestion: str = Field(default="", description="Sugestão de correção")


class CodeSuggestion(BaseModel):
    """Schema para sugestão de melhoria"""
    priority: Literal["high", "medium", "low"] = Field(
        description="Prioridade da sugestão"
    )
    category: Literal["refactoring", "optimization", "documentation", "testing"] = Field(
        description="Categoria da sugestão"
    )
    suggestion: str = Field(description="Melhoria proposta")
    rationale: str = Field(description="Justificativa")


class CodeQualityScore(BaseModel):
    """Schema para score de qualidade"""
    readability: int = Field(ge=0, le=10, description="Score de legibilidade")
    maintainability: int = Field(ge=0, le=10, description="Score de manutenibilidade")
    efficiency: int = Field(ge=0, le=10, description="Score de eficiência")
    documentation: int = Field(ge=0, le=10, description="Score de documentação")
    overall: int = Field(ge=0, le=10, description="Score geral")


class CodeReviewOutput(BaseModel):
    """Schema para review de código"""
    is_approved: bool = Field(description="Se o código foi aprovado")
    confidence_score: float = Field(
        ge=0.0, le=1.0,
        description="Confiança na avaliação"
    )
    issues_found: List[CodeIssue] = Field(
        default_factory=list,
        description="Issues encontrados"
    )
    suggestions: List[CodeSuggestion] = Field(
        default_factory=list,
        description="Sugestões de melhoria"
    )
    strengths: List[str] = Field(
        default_factory=list,
        description="Pontos fortes"
    )
    code_quality_score: CodeQualityScore = Field(
        description="Scores de qualidade"
    )
    test_coverage_assessment: str = Field(
        default="",
        description="Avaliação da cobertura de testes"
    )
    security_assessment: str = Field(
        default="",
        description="Avaliação de segurança"
    )
    overall_assessment: str = Field(
        description="Avaliação geral detalhada"
    )


class FailedCheck(BaseModel):
    """Schema para check que falhou"""
    check: str = Field(description="Nome do check")
    reason: str = Field(description="Razão da falha")
    blocking: bool = Field(description="Se bloqueia a entrega")


class DeliverablesChecklist(BaseModel):
    """Schema para checklist de entregas"""
    code: bool = Field(description="Código presente")
    documentation: bool = Field(description="Documentação presente")
    tests: bool = Field(description="Testes presentes")
    setup_instructions: bool = Field(description="Instruções de setup presentes")
    dependencies: bool = Field(description="Dependências declaradas")


class ValidationOutput(BaseModel):
    """Schema para validação final"""
    is_valid: bool = Field(description="Se a solução é válida")
    passed_checks: List[str] = Field(
        default_factory=list,
        description="Checks que passaram"
    )
    failed_checks: List[FailedCheck] = Field(
        default_factory=list,
        description="Checks que falharam"
    )
    warnings: List[str] = Field(
        default_factory=list,
        description="Avisos"
    )
    deliverables_checklist: DeliverablesChecklist = Field(
        description="Checklist de entregas"
    )
    readiness_score: float = Field(
        ge=0.0, le=1.0,
        description="Score de prontidão (0.0 a 1.0)"
    )
    final_notes: str = Field(
        default="",
        description="Notas finais para o usuário"
    )
    recommended_next_steps: List[str] = Field(
        default_factory=list,
        description="Próximos passos recomendados"
    )