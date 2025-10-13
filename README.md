# 🤖 AI Agent Flow

Sistema Multi-Agente Inteligente para Planejamento e Construção de Soluções usando LangGraph e Streamlit.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![LangGraph 0.6+](https://img.shields.io/badge/langgraph-0.6+-green.svg)](https://github.com/langchain-ai/langgraph)
[![Streamlit](https://img.shields.io/badge/streamlit-1.39+-red.svg)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 📋 Índice

- [Sobre o Projeto](#sobre-o-projeto)
- [Características](#características)
- [Arquitetura](#arquitetura)
- [Pré-requisitos](#pré-requisitos)
- [Instalação](#instalação)
- [Configuração](#configuração)
- [Uso](#uso)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Fluxo de Execução](#fluxo-de-execução)
- [Exemplos](#exemplos)
- [Troubleshooting](#troubleshooting)
- [Roadmap](#roadmap)
- [Contribuindo](#contribuindo)
- [Licença](#licença)

---

## 🎯 Sobre o Projeto

O **AI Agent Flow** é um sistema avançado de agentes de IA que recebe demandas em linguagem natural e automaticamente:

1. **Classifica** a demanda (Análise, Software, Pipeline de Dados)
2. **Extrai** requisitos estruturados
3. **Planeja** a solução step-by-step
4. **Aguarda aprovação** do usuário (human-in-the-loop)
5. **Constrói** a solução completa
6. **Revisa** e valida com múltiplas camadas
7. **Entrega** código, documentação e testes

### 💡 Casos de Uso

- 📊 **Análises de Mercado**: Gera análises completas com código Python para coleta e visualização de dados
- 💻 **Desenvolvimento de Software**: Cria aplicações completas com interface web, testes e documentação
- 🔄 **Pipelines de Dados**: Constrói pipelines PySpark/Pandas com validações e monitoramento

---

## ✨ Características

### 🔥 Fase 1 - MVP Funcional

- ✅ **Multi-Provider LLM**: Suporte para 7 providers (Anthropic, OpenAI, Google, DeepSeek, xAI, Qwen, Ollama)
- ✅ **Fluxo de Agentes Completo**: 10+ nós especializados orquestrados via LangGraph
- ✅ **Human-in-the-Loop**: Checkpoint obrigatório para aprovação do plano
- ✅ **Múltiplas Camadas de Revisão**: Validação em cada etapa crítica
- ✅ **Interface Web Intuitiva**: 5 abas organizadas (Input, Planejamento, Execução, Resultados, Logs)
- ✅ **Logging Completo**: Rastreamento detalhado de cada operação
- ✅ **Estimativa de Custos**: Tracking de tokens e custos em tempo real
- ✅ **Guardrails**: Validação de sintaxe, qualidade de código e completude
- ✅ **Configuração Flexível**: Escolha de modelos por função (Classificador, Planejador, Construtor, Revisor)

### 🚀 Próximas Fases (Roadmap)

- 🔄 **Fase 2**: Persistência de sessões e versionamento
- ⚡ **Fase 3**: Execução assíncrona com background workers
- 🛠️ **Fase 4**: Execução de código em sandbox seguro
- 🌐 **Fase 5**: Integração com web search e APIs externas

---

## 🏗️ Arquitetura

### Componentes Principais

```
┌─────────────────────────────────────────────────────────────┐
│                     STREAMLIT UI                            │
│  ┌──────────┬──────────┬──────────┬──────────┬──────────┐  │
│  │  Input   │   Plan   │   Exec   │ Results  │   Logs   │  │
│  └──────────┴──────────┴──────────┴──────────┴──────────┘  │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                     LANGGRAPH CORE                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Classifier   │→ │   Planner    │→ │   Builder    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│         ↕                 ↕                  ↕              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Reviewers   │  │  Feedback    │  │  Validators  │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                     LLM PROVIDERS                           │
│  Claude 4.5  │  GPT-5  │  Gemini 2.5  │  DeepSeek  │ ...   │
└─────────────────────────────────────────────────────────────┘
```

### Fluxo de Dados

```mermaid
graph TD
    A[User Input] --> B[Classifier]
    B --> C[Requirements Reviewer]
    C --> D[Prompt Creator]
    D --> E[Planner]
    E --> F[Plan Reviewer]
    F --> G{Approved?}
    G -->|No| H[Process Feedback]
    H --> E
    G -->|Yes| I[Wait User Approval]
    I --> J{User Decision}
    J -->|Feedback| H
    J -->|Approved| K[Builder]
    K --> L[Solution Reviewer]
    L --> M[Final Validator]
    M --> N[Deliverables]
```

---

## 🔧 Pré-requisitos

### Obrigatório

- **Python 3.11+** (recomendado 3.11 ou 3.12)
- **Pelo menos 1 API Key** de LLM provider:
  - Anthropic (Claude) - Recomendado
  - OpenAI (GPT)
  - Google (Gemini)
  - DeepSeek
  - xAI (Grok)
  - Qwen (Alibaba)

### Opcional

- **Ollama** - Para modelos locais (Llama, Mistral, etc)
- **Tavily ou Serper API** - Para web search (futuras fases)

### Recursos de Sistema

- **RAM**: 4GB mínimo, 8GB recomendado
- **Disco**: 500MB para dependências
- **Internet**: Conexão estável para chamadas de API

---

## 📦 Instalação

### 1. Clone o Repositório

```bash
git clone https://github.com/seu-usuario/ai-agent-flow.git
cd ai-agent-flow
```

### 2. Crie Ambiente Virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

### 3. Instale Dependências

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Verifique Instalação

```bash
python -c "import langchain; import langgraph; import streamlit; print('✅ Instalação OK!')"
```

---

## ⚙️ Configuração

### 1. Configure Variáveis de Ambiente

```bash
# Copie o template
cp .env.example .env

# Edite o arquivo .env com suas API keys
nano .env  # ou use seu editor preferido
```

### 2. Preencha as API Keys

Abra o arquivo `.env` e adicione suas chaves:

```env
# Anthropic (Recomendado - melhor para coding)
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# OpenAI (Opcional - mais barato)
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Google (Opcional - maior context window)
GOOGLE_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Outros providers (opcional)
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
XAI_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
QWEN_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 3. Configurações Adicionais (Opcional)

```env
# Nível de log
LOG_LEVEL=INFO

# Timeout para chamadas LLM (segundos)
DEFAULT_TIMEOUT=300

# URL do Ollama (se usar modelos locais)
OLLAMA_BASE_URL=http://localhost:11434
```

### 4. Teste a Configuração

```bash
python -c "from config.settings import validate_minimum_config; print('✅ Configuração válida!' if validate_minimum_config()[0] else '❌ Configuração incompleta')"
```

---

## 🚀 Uso

### Iniciar a Aplicação

```bash
streamlit run app.py
```

A aplicação abrirá automaticamente em `http://localhost:8501`

### Passo a Passo

#### 1️⃣ Configure os Modelos (Sidebar)

- Selecione o provider e modelo para cada função:
  - **Classificador**: Identifica tipo de demanda
  - **Planejador**: Cria o plano de execução
  - **Construtor**: Implementa a solução
  - **Revisor**: Valida qualidade

**Recomendação:**
- Classificador: Claude Sonnet 4.5 ou GPT-5
- Planejador: Claude Sonnet 4.5
- Construtor: Claude Sonnet 4.5 (melhor para código)
- Revisor: Claude Opus 4.1 (mais crítico)

#### 2️⃣ Descreva sua Demanda

Na aba **"Input da Demanda"**:
- Descreva em linguagem natural o que você precisa
- Seja específico sobre requisitos e restrições
- Mencione tecnologias se tiver preferência

#### 3️⃣ Inicie o Processamento

- Clique em **"🚀 Iniciar Processamento"**
- Vá para a aba **"Execução"**
- Clique em **"▶️ Executar Próximo Passo"** para avançar

#### 4️⃣ Revise o Plano

- Quando o sistema pausar, vá para a aba **"Planejamento"**
- Revise o plano gerado
- Escolha:
  - **✅ Aprovar e Prosseguir**: Continua para construção
  - **✏️ Solicitar Ajustes**: Dá feedback para ajustar

#### 5️⃣ Acompanhe a Execução

Na aba **"Execução"**:
- Veja o progresso em tempo real
- Monitore tokens e custos
- Observe logs de cada operação

#### 6️⃣ Obtenha os Resultados

Na aba **"Resultados"**:
- Visualize todos os arquivos gerados
- Faça download individual ou completo
- Leia a documentação gerada

#### 7️⃣ Analise os Logs

Na aba **"Logs"**:
- Veja timeline completa de eventos
- Filtre por nível ou tipo
- Exporte logs para arquivo

---

## 📂 Estrutura do Projeto

```
ai_agent_flow/
├── app.py                      # ⭐ Aplicação Streamlit principal
├── requirements.txt            # Dependências Python
├── .env.example               # Template de configuração
├── .env                       # Suas configurações (não versionar!)
├── README.md                  # Este arquivo
│
├── config/                    # Configurações
│   ├── __init__.py
│   ├── settings.py           # Settings gerais
│   └── llm_config.py         # Modelos LLM disponíveis
│
├── core/                      # Lógica principal
│   ├── __init__.py
│   ├── state.py              # Estados do LangGraph
│   ├── graph.py              # Definição do grafo
│   └── nodes/                # Nós do grafo
│       ├── __init__.py
│       ├── classifier.py     # Classificação
│       ├── planner.py        # Planejamento
│       ├── builder.py        # Construção
│       ├── reviewer.py       # Revisão
│       └── feedback.py       # Feedback do usuário
│
├── prompts/                   # Templates de prompts
│   ├── __init__.py
│   ├── classifier.py
│   ├── planner.py
│   └── builder.py
│
├── utils/                     # Utilitários
│   ├── __init__.py
│   ├── llm_factory.py        # Factory de LLMs
│   ├── logger.py             # Sistema de logs
│   └── validators.py         # Validadores
│
└── logs/                      # Logs gerados (criado automaticamente)
    └── app_YYYY-MM-DD.log
```

---

## 🔄 Fluxo de Execução

### Visão Geral

```
[USER INPUT] → Classificação → Requisitos → Planejamento → 
[CHECKPOINT: Aprovação] → Construção → Revisão → Validação → [OUTPUT]
```

### Detalhado

1. **Classificação** (2 nós)
   - Classifica tipo de demanda
   - Extrai requisitos estruturados
   - **Saída**: Requirements object

2. **Planejamento** (3 nós)
   - Cria prompts especializados
   - Gera plano detalhado
   - Revisa plano
   - **Saída**: Plan object

3. **⏸️ CHECKPOINT - Aprovação do Usuário**
   - Sistema pausa e aguarda
   - Usuário pode aprovar ou dar feedback
   - Se feedback: loop de ajuste

4. **Construção** (3 nós)
   - Implementa solução conforme plano
   - Revisa código (code review)
   - Valida solução final
   - **Saída**: Solution object com arquivos

### Guardrails por Etapa

- **Classificação**: Confiança mínima 0.7
- **Requisitos**: Aprovação do revisor
- **Plano**: Aprovação técnica + usuário
- **Código**: Sintaxe válida + qualidade mínima
- **Final**: Todos os requisitos atendidos

---

## 📚 Exemplos

### Exemplo 1: Análise de Mercado

**Input:**
```
Quero uma análise do mercado de cartão de crédito no Brasil, comparando 
os principais players (Itaú, Bradesco, Nubank, C6) sobre share de mercado, 
taxas médias e inovações recentes. Preciso de gráficos comparativos.
```

**Output:**
- `analysis.py`: Script Python para coleta de dados
- `visualization.py`: Código para gráficos
- `report.md`: Relatório em Markdown
- `requirements.txt`: Dependências (pandas, plotly, etc)

### Exemplo 2: Sistema de Testes A/B

**Input:**
```
Preciso de uma solução completa para Testes A/B em Python com interface Streamlit.
Deve fazer pareamento por propensity score, calcular lift e p-value, e gerar
relatório com gráficos. Dados de entrada: CSV com grupo e métricas.
```

**Output:**
- `app.py`: Interface Streamlit completa
- `ab_test.py`: Lógica de testes A/B
- `propensity.py`: Pareamento
- `statistics.py`: Cálculos estatísticos
- `tests/`: Testes unitários
- `README.md`: Documentação de uso

### Exemplo 3: Pipeline PySpark

**Input:**
```
Pipeline PySpark para análise de inadimplência em Databricks. Base tem: 
customer_id, data, saldo, dias_atraso. Preciso de tendência de inadimplência 
30+ dias, alertas e visualizações.
```

**Output:**
- `pipeline.py`: Pipeline PySpark completo
- `transformations.py`: Transformações de dados
- `metrics.py`: Cálculo de métricas
- `alerts.py`: Sistema de alertas
- `databricks_notebook.py`: Notebook Databricks
- `README.md`: Setup no Databricks

---

## 🐛 Troubleshooting

### Problema: "ANTHROPIC_API_KEY não configurada"

**Solução:**
```bash
# Verifique se o .env existe
ls -la .env

# Edite e adicione a key
echo "ANTHROPIC_API_KEY=sk-ant-seu-token" >> .env
```

### Problema: "Module 'langgraph' not found"

**Solução:**
```bash
# Reinstale dependências
pip install --upgrade -r requirements.txt
```

### Problema: Execução muito lenta

**Soluções:**
- Use modelos mais rápidos (GPT-4o-mini, Gemini Flash)
- Reduza temperature para <0.3
- Use Ollama para modelos locais

### Problema: Custos altos

**Soluções:**
- Use Claude Haiku 4 (mais barato)
- Use GPT-4o-mini
- Use Gemini 2.0 Flash Lite
- Configure modelos locais via Ollama

### Problema: Plano rejeitado sempre

**Soluções:**
- Use temperatura mais alta (0.7-0.8)
- Seja mais específico na demanda
- Use modelo mais capaz no Planejador

### Problema: Código com erros de sintaxe

**Soluções:**
- Use Claude Sonnet 4.5 no Construtor
- Aumente max_tokens para 8000+
- Ative modo verbose para debug

---

## 🗺️ Roadmap

### Fase 1 - MVP Funcional ✅ (Atual)
- [x] Interface Streamlit completa
- [x] Fluxo de agentes LangGraph
- [x] Suporte multi-provider
- [x] Human-in-the-loop
- [x] Logging e monitoring

### Fase 2 - Persistência 🔄 (Próxima)
- [ ] Banco de dados SQLite
- [ ] Salvamento de sessões
- [ ] Histórico de projetos
- [ ] Versionamento de soluções
- [ ] Retomada de execução

### Fase 3 - Execução Assíncrona ⏳
- [ ] Background workers (Celery)
- [ ] Sistema de filas
- [ ] Notificações de status
- [ ] Múltiplas sessões paralelas

### Fase 4 - Features Avançadas 🚀
- [ ] Execução de código em sandbox
- [ ] Integração web search
- [ ] Testes automatizados
- [ ] Deploy automático
- [ ] CI/CD integration

### Fase 5 - Enterprise 🏢
- [ ] Autenticação de usuários
- [ ] Multi-tenancy
- [ ] Rate limiting
- [ ] Audit logs
- [ ] Custom model fine-tuning

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Para contribuir:

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

### Guidelines

- Siga PEP 8
- Adicione docstrings
- Inclua testes quando possível
- Atualize o README se necessário

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

---

## 🙏 Agradecimentos

- **LangChain Team** - Pelo framework incrível
- **Anthropic** - Pelos modelos Claude excepcionais
- **Streamlit** - Pela interface web simples e poderosa
- **Comunidade Open Source** - Por todas as bibliotecas utilizadas

---

## 📞 Suporte

- 📧 Email: seu-email@example.com
- 🐛 Issues: [GitHub Issues](https://github.com/seu-usuario/ai-agent-flow/issues)
- 💬 Discussões: [GitHub Discussions](https://github.com/seu-usuario/ai-agent-flow/discussions)

---

## 📊 Status do Projeto

![Status](https://img.shields.io/badge/status-active-success.svg)
![Fase](https://img.shields.io/badge/fase-MVP%20Funcional-blue.svg)
![Testes](https://img.shields.io/badge/tests-passing-brightgreen.svg)

**Última atualização:** 13 de Outubro de 2025

---

<div align="center">
  <p>Feito com ❤️ usando LangGraph + Streamlit</p>
  <p>⭐ Se este projeto foi útil, considere dar uma estrela!</p>
</div>