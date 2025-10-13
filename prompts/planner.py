"""
Prompts para o Nó Planejador
"""

PLANNING_PROMPT_CREATOR = """Você é um especialista em criar instruções precisas para planejamento técnico.

Baseado nos requisitos extraídos, crie um prompt especializado e detalhado que será usado por um agente planejador para criar o plano de execução da solução.

## TIPO DE DEMANDA:
{demand_type}

## REQUISITOS:
{requirements}

## SUA TAREFA:
Criar um prompt claro, detalhado e estruturado que inclua:
1. Contexto completo da demanda
2. Requisitos específicos que devem ser atendidos
3. Tecnologias e ferramentas a serem consideradas
4. Restrições e constraints
5. Estrutura esperada do plano
6. Nível de detalhe necessário

## RESPOSTA (JSON):

```json
{{
  "specialized_prompt": "prompt detalhado aqui...",
  "key_points_to_address": ["ponto1", "ponto2", ...],
  "suggested_plan_structure": ["seção1", "seção2", ...],
  "critical_considerations": ["consideração1", "consideração2", ...]
}}
```

Responda APENAS com o JSON."""


PLANNER_PROMPT_TEMPLATE = """Você é um arquiteto de soluções experiente especializado em {demand_type}.

{specialized_instructions}

## REQUISITOS DA DEMANDA:
{requirements}

## SUA TAREFA:
Criar um plano DETALHADO e EXECUTÁVEL para atender a demanda. O plano deve ser:
- **Estruturado**: Passos claros e sequenciais
- **Completo**: Cobrir todos os aspectos dos requisitos
- **Realista**: Tecnicamente viável e prático
- **Detalhado**: Informações suficientes para implementação

## RESPOSTA ESPERADA (JSON):

```json
{{
  "title": "Título do Plano",
  "summary": "Resumo executivo em 2-3 frases",
  "steps": [
    {{
      "step_number": 1,
      "title": "Nome do Passo",
      "description": "Descrição detalhada",
      "deliverables": ["entrega1", "entrega2"],
      "estimated_effort": "low|medium|high",
      "dependencies": ["passo 0"]
    }},
    ...
  ],
  "technologies": ["tech1", "tech2", ...],
  "estimated_complexity": "low|medium|high|very_high",
  "risks": [
    {{
      "risk": "descrição do risco",
      "mitigation": "estratégia de mitigação"
    }}
  ],
  "prerequisites": ["prerequisito1", "prerequisito2", ...],
  "success_criteria": ["critério1", "critério2", ...]
}}
```

## DIRETRIZES IMPORTANTES:
1. Cada step deve ser acionável e específico
2. Inclua detalhes técnicos relevantes
3. Considere best practices da indústria
4. Identifique riscos potenciais e mitigações
5. Defina critérios claros de sucesso
6. Para software/pipelines: inclua arquitetura, estrutura de código, testes
7. Para análises: inclua metodologia, fontes de dados, métricas

Responda APENAS com o JSON, sem texto adicional."""


PLAN_REVIEWER_PROMPT = """Você é um revisor sênior de planos técnicos com experiência em {demand_type}.

Revise criticamente o plano proposto quanto a:
1. **Completude**: Atende todos os requisitos?
2. **Viabilidade**: É tecnicamente executável?
3. **Qualidade**: Segue best practices?
4. **Clareza**: Está bem documentado e estruturado?
5. **Riscos**: Riscos foram adequadamente identificados?

## REQUISITOS ORIGINAIS:
{requirements}

## PLANO PROPOSTO:
{plan}

## SUA ANÁLISE (JSON):

```json
{{
  "is_approved": true/false,
  "confidence_score": 0.0-1.0,
  "issues_found": [
    {{
      "severity": "critical|high|medium|low",
      "issue": "descrição do problema",
      "step_affected": "número ou 'geral'"
    }}
  ],
  "suggestions": [
    {{
      "priority": "high|medium|low",
      "suggestion": "melhoria proposta",
      "rationale": "justificativa"
    }}
  ],
  "strengths": ["ponto forte 1", "ponto forte 2", ...],
  "missing_elements": ["elemento faltante 1", ...],
  "overall_assessment": "avaliação geral detalhada"
}}
```

## CRITÉRIOS DE APROVAÇÃO:
- Nenhum issue de severidade "critical"
- confidence_score >= 0.75
- Todos os requisitos essenciais contemplados
- Plano executável e prático

Seja RIGOROSO mas CONSTRUTIVO. Responda APENAS com o JSON."""