"""
Interface Streamlit - AI Agent Flow (VERSÃO CORRIGIDA)
"""
import streamlit as st
import json
import uuid
from datetime import datetime
from typing import Dict, Any

# Imports do projeto
from config.settings import settings, check_api_keys, validate_minimum_config
from config.llm_config import AVAILABLE_MODELS, get_all_providers, get_models_by_provider
from core.graph import create_agent_graph, get_graph_visualization, get_current_step_description
from core.state import create_initial_state, get_plan, get_solution
from utils.logger import get_logger
from utils.llm_factory import validate_model

# Configuração da página
st.set_page_config(
    page_title="AI Agent Flow",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    .step-indicator {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f0f2f6;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)


# ========================================
# INICIALIZAÇÃO DA SESSÃO
# ========================================

def initialize_session():
    """Inicializa variáveis da sessão"""
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    
    if "graph" not in st.session_state:
        st.session_state.graph = None
    
    if "state" not in st.session_state:
        st.session_state.state = None
    
    if "execution_started" not in st.session_state:
        st.session_state.execution_started = False
    
    if "execution_paused" not in st.session_state:
        st.session_state.execution_paused = False
    
    if "selected_models" not in st.session_state:
        st.session_state.selected_models = {}
    
    if "user_demand" not in st.session_state:
        st.session_state.user_demand = ""


initialize_session()
logger = get_logger()


# ========================================
# SIDEBAR - CONFIGURAÇÕES
# ========================================

with st.sidebar:
    st.markdown("## ⚙️ Configurações")
    
    # Verificar configuração mínima
    is_valid, missing = validate_minimum_config()
    
    if not is_valid:
        st.error("⚠️ Configuração Incompleta")
        st.write("Faltando:")
        for item in missing:
            st.write(f"- {item}")
        st.info("Configure as API keys no arquivo .env")
        st.stop()
    
    # Mostrar API keys configuradas
    with st.expander("🔑 API Keys Configuradas"):
        api_status = check_api_keys()
        for provider, configured in api_status.items():
            icon = "✅" if configured else "❌"
            st.write(f"{icon} {provider}")
    
    st.markdown("---")
    
    # Seleção de modelos por função
    st.markdown("### 🤖 Seleção de Modelos")
    
    # Função auxiliar para seleção de modelo
    def select_model(function_name: str, label: str, default_provider: str = None):
        """Widget para seleção de modelo"""
        # Provider
        providers = get_all_providers()
        
        # Filtrar apenas providers com API key configurada
        api_status = check_api_keys()
        available_providers = [
            p for p in providers 
            if api_status.get(p, False) or p == "Ollama"
        ]
        
        if not available_providers:
            st.error(f"Nenhum provider disponível para {label}")
            return None
        
        provider_key = f"{function_name}_provider"
        if provider_key not in st.session_state:
            st.session_state[provider_key] = default_provider or available_providers[0]
        
        provider = st.selectbox(
            f"Provider - {label}",
            available_providers,
            key=provider_key,
            index=available_providers.index(st.session_state[provider_key]) if st.session_state[provider_key] in available_providers else 0
        )
        
        # Modelo
        models = get_models_by_provider(provider)
        if not models:
            st.warning(f"Nenhum modelo disponível para {provider}")
            return None
        
        model_options = [f"{m.display_name} (${m.cost_per_1m_output}/M out)" for m in models]
        
        model_key = f"{function_name}_model"
        if model_key not in st.session_state:
            st.session_state[model_key] = 0
        
        selected_idx = st.selectbox(
            f"Modelo - {label}",
            range(len(model_options)),
            format_func=lambda x: model_options[x],
            key=model_key
        )
        
        return models[selected_idx].name
    
    # Seleção para cada função
    st.markdown("#### Classificador")
    classifier_model = select_model("classifier", "Classificação", "Google")
    
    st.markdown("#### Planejador")
    planner_model = select_model("planner", "Planejamento", "Google")
    
    st.markdown("#### Construtor")
    builder_model = select_model("builder", "Construção", "Google")
    
    st.markdown("#### Revisor")
    reviewer_model = select_model("reviewer", "Revisão", "Google")
    
    # Armazenar seleções
    st.session_state.selected_models = {
        "classifier": classifier_model,
        "planner": planner_model,
        "builder": builder_model,
        "reviewer": reviewer_model,
    }
    
    st.markdown("---")
    
    # Configurações adicionais
    with st.expander("🎛️ Configurações Avançadas"):
        st.slider("Temperature", 0.0, 1.0, 0.7, 0.1, key="temperature")
        st.checkbox("Verbose Logging", value=False, key="verbose")
        st.checkbox("Auto-approve (sem checkpoint)", value=False, key="auto_approve")
    
    st.markdown("---")
    
    # Botão de reset
    if st.button("🔄 Nova Sessão", type="secondary", use_container_width=True):
        for key in list(st.session_state.keys()):
            if key not in ["session_id"]:  # Manter apenas session_id
                del st.session_state[key]
        st.session_state.session_id = str(uuid.uuid4())
        st.rerun()


# ========================================
# HEADER
# ========================================

st.markdown('<div class="main-header">🤖 AI Agent Flow</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Sistema Multi-Agente para Planejamento e Construção de Soluções</div>', unsafe_allow_html=True)

# Mostrar visualização do grafo
with st.expander("📊 Visualização do Fluxo de Agentes"):
    st.code(get_graph_visualization(), language="")


# ========================================
# TABS PRINCIPAIS
# ========================================

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📝 Input da Demanda",
    "📋 Planejamento",
    "⚙️ Execução",
    "📦 Resultados",
    "📊 Logs"
])

# TAB 1: INPUT DA DEMANDA
with tab1:
    st.markdown("### 📝 Descreva sua Demanda")
    
    st.markdown("""
    Descreva em linguagem natural o que você precisa. Por exemplo:
    - **Análise**: "Quero uma análise do mercado de cartão de crédito no Brasil..."
    - **Software**: "Preciso de uma solução completa para Testes A/B em Python..."
    - **Pipeline**: "Preciso de um pipeline PySpark para análise de inadimplência..."
    """)
    
    user_demand = st.text_area(
        "Sua demanda:",
        height=200,
        placeholder="Digite aqui sua demanda em linguagem natural...",
        key="demand_input"
    )
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        if st.button("🚀 Iniciar Processamento", type="primary", disabled=st.session_state.execution_started):
            if not user_demand or len(user_demand.strip()) < 20:
                st.error("Por favor, descreva sua demanda com mais detalhes (mínimo 20 caracteres)")
            else:
                # Validar modelos selecionados
                invalid_models = []
                for func, model in st.session_state.selected_models.items():
                    if model:
                        is_valid, error = validate_model(model)
                        if not is_valid:
                            invalid_models.append(f"{func}: {error}")
                
                if invalid_models:
                    st.error("Modelos inválidos ou sem API key:")
                    for error in invalid_models:
                        st.write(f"- {error}")
                else:
                    # Iniciar execução
                    st.session_state.user_demand = user_demand
                    st.session_state.execution_started = True
                    
                    # Criar estado inicial
                    initial_state = create_initial_state(
                        user_demand=user_demand,
                        session_id=st.session_state.session_id,
                        selected_models=st.session_state.selected_models
                    )
                    
                    st.session_state.state = initial_state
                    
                    # Criar grafo
                    st.session_state.graph = create_agent_graph()
                    
                    logger.log_user_input("demand", user_demand)
                    
                    st.success("✅ Processamento iniciado!")
                    st.rerun()
    
    with col2:
        if st.button("📋 Exemplos"):
            st.session_state.show_examples = not st.session_state.get("show_examples", False)
    
    with col3:
        if st.button("🗑️ Limpar"):
            st.session_state.demand_input = ""
            st.rerun()
    
    # Mostrar exemplos se solicitado
    if st.session_state.get("show_examples", False):
        with st.expander("💡 Exemplos de Demandas", expanded=True):
            st.markdown("""
            **Exemplo 1 - Análise de Mercado:**
            ```
            Quero uma análise do mercado de cartão de crédito no Brasil, comparando os 
            principais players (bancos incumbentes e fintechs) sobre o ponto de vista do 
            share do mercado. Preciso de dados atualizados, gráficos comparativos e 
            insights sobre tendências.
            ```
            
            **Exemplo 2 - Sistema de Testes A/B:**
            ```
            Preciso que seja criada uma solução completa para execução de Testes A/B em Python.
            Deve incluir interface web, etapas de pareamento e balanceamento, até o cálculo 
            do lift. O cliente vai subir Grupo teste e Grupo controle que devem ser pareados 
            por variáveis. A saída deve ser um relatório didático sobre os resultados.
            ```
            
            **Exemplo 3 - Pipeline PySpark:**
            ```
            Tenho uma base de dados sobre saldo da carteira de crédito de cartão de crédito.
            A base tem: customer_id, data_referencia, saldo_devedor, dias_atraso, limite_credito.
            Preciso de um pipeline em PySpark que roda no Databricks para análise de tendência 
            da inadimplência 30 dias, com visualizações e alertas.
            ```
            """)

# TAB 2: PLANEJAMENTO
with tab2:
    st.markdown("### 📋 Plano de Execução")
    
    if not st.session_state.execution_started:
        st.info("👈 Comece descrevendo sua demanda na aba 'Input da Demanda'")
    else:
        state = st.session_state.state
        
        # Mostrar requisitos extraídos
        if state and state.get("requirements"):
            with st.expander("📑 Requisitos Extraídos", expanded=False):
                req = state["requirements"]
                st.write(f"**Tipo de Demanda:** {req['demand_type']}")
                st.write(f"**Confiança:** {req['confidence_score']:.0%}")
                
                if req.get("key_requirements"):
                    st.write("**Requisitos Principais:**")
                    for r in req["key_requirements"]:
                        st.write(f"- {r}")
                
                if req.get("technologies_mentioned"):
                    st.write("**Tecnologias Mencionadas:**")
                    st.write(", ".join(req["technologies_mentioned"]))
        
        # Mostrar plano se existir
        if state and state.get("plan"):
            plan = get_plan(state)
            
            st.markdown(f"## {plan.title}")
            st.write(plan.summary)
            
            # Métricas
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Passos", len(plan.steps))
            with col2:
                st.metric("Complexidade", plan.estimated_complexity.upper())
            with col3:
                st.metric("Tecnologias", len(plan.technologies))
            with col4:
                st.metric("Riscos", len(plan.risks))
            
            st.markdown("---")
            
            # Passos detalhados
            st.markdown("### 📝 Passos do Plano")
            for step in plan.steps:
                with st.expander(f"**Passo {step.get('step_number', '?')}**: {step.get('title', 'Sem título')}", expanded=False):
                    st.write(step.get("description", "Sem descrição"))
                    
                    if step.get("deliverables"):
                        st.write("**Entregas:**")
                        for d in step["deliverables"]:
                            st.write(f"- {d}")
                    
                    if step.get("estimated_effort"):
                        st.write(f"**Esforço Estimado:** {step['estimated_effort']}")
            
            st.markdown("---")
            
            # Tecnologias
            if plan.technologies:
                st.markdown("### 🛠️ Tecnologias")
                st.write(", ".join(plan.technologies))
            
            # Riscos
            if plan.risks:
                st.markdown("### ⚠️ Riscos Identificados")
                for risk in plan.risks:
                    if isinstance(risk, dict):
                        st.warning(f"**{risk.get('risk')}**")
                        st.write(f"*Mitigação:* {risk.get('mitigation')}")
                    else:
                        st.warning(risk)
            
            st.markdown("---")
            
            # Revisão do plano
            if state.get("plan_review"):
                review = state["plan_review"]
                
                if review["is_approved"]:
                    st.success(f"✅ Plano Aprovado (Confiança: {review['confidence_score']:.0%})")
                else:
                    st.warning(f"⚠️ Plano Requer Ajustes (Confiança: {review['confidence_score']:.0%})")
                
                if review.get("strengths"):
                    with st.expander("✨ Pontos Fortes"):
                        for s in review["strengths"]:
                            st.write(f"- {s}")
                
                if review.get("issues_found"):
                    with st.expander("⚠️ Issues Encontrados"):
                        for i in review["issues_found"]:
                            st.write(f"- {i}")
                
                if review.get("suggestions"):
                    with st.expander("💡 Sugestões"):
                        for s in review["suggestions"]:
                            st.write(f"- {s}")
            
            # ✅ CHECKPOINT CORRIGIDO: Aprovação do usuário
            if state.get("current_step") in ["wait_user_approval", "waiting_approval"]:
                st.markdown("---")
                st.markdown("### ✋ Decisão Necessária")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("✅ Aprovar e Prosseguir", type="primary", use_container_width=True):
                        # Atualizar estado
                        st.session_state.state["user_approved"] = True
                        st.session_state.state["user_feedback"] = None
                        st.session_state.execution_paused = False
                        
                        # ✅ Retomar execução automaticamente
                        with st.spinner("Retomando execução..."):
                            try:
                                graph = st.session_state.graph
                                config = {"configurable": {"thread_id": st.session_state.session_id}}
                                
                                result = graph.invoke(st.session_state.state, config)
                                
                                if result is not None:
                                    st.session_state.state = result
                                
                                st.success("Plano aprovado! Prosseguindo para construção...")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro ao retomar: {str(e)}")
                                logger.log_node_error("resume", e)
                
                with col2:
                    if st.button("✏️ Solicitar Ajustes", type="secondary", use_container_width=True):
                        st.session_state.show_feedback_form = True
                
                if st.session_state.get("show_feedback_form", False):
                    feedback = st.text_area(
                        "Descreva os ajustes necessários:",
                        height=150,
                        key="user_feedback_input"
                    )
                    
                    if st.button("📤 Enviar Feedback"):
                        if feedback:
                            st.session_state.state["user_feedback"] = feedback
                            st.session_state.state["user_approved"] = False
                            st.session_state.show_feedback_form = False
                            
                            # ✅ Retomar execução para processar feedback
                            with st.spinner("Processando feedback e ajustando plano..."):
                                try:
                                    graph = st.session_state.graph
                                    config = {"configurable": {"thread_id": st.session_state.session_id}}
                                    
                                    result = graph.invoke(st.session_state.state, config)
                                    
                                    if result is not None:
                                        st.session_state.state = result
                                    
                                    st.success("Feedback enviado! Ajustando plano...")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Erro ao processar feedback: {str(e)}")
                                    logger.log_node_error("feedback_processing", e)
                        else:
                            st.error("Por favor, descreva os ajustes necessários")
        else:
            if state and state.get("current_step") not in ["classification", "review_requirements"]:
                st.info("⏳ Aguardando criação do plano...")


# TAB 3: EXECUÇÃO
with tab3:
    st.markdown("### ⚙️ Status da Execução")
    
    if not st.session_state.execution_started:
        st.info("👈 Comece descrevendo sua demanda na aba 'Input da Demanda'")
    else:
        state = st.session_state.state
        graph = st.session_state.graph
        
        if state:
            # Step atual
            current_step = state.get("current_step", "unknown")
            step_description = get_current_step_description(current_step)
            
            st.markdown(f'<div class="step-indicator"><h3>{step_description}</h3></div>', unsafe_allow_html=True)
            
            # Progress bar (aproximado)
            steps_order = [
                "classification", "review_requirements",
                "create_planning_prompts", "create_plan", "review_plan",
                "wait_user_approval", "build_solution", "review_solution",
                "validate_solution", "completed"
            ]
            
            if current_step in steps_order:
                progress = (steps_order.index(current_step) + 1) / len(steps_order)
            else:
                progress = 0.5
            
            st.progress(progress, text=f"Progresso: {int(progress * 100)}%")
            
            # Métricas de execução
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                elapsed = datetime.now() - state.get("started_at", datetime.now())
                st.metric("Tempo Decorrido", f"{int(elapsed.total_seconds())}s")
            
            with col2:
                st.metric("Tokens Usados", f"{state.get('total_tokens_used', 0):,}")
            
            with col3:
                st.metric("Custo Estimado", f"${state.get('total_cost', 0.0):.4f}")
            
            with col4:
                iteration = state.get("feedback_iteration", 0)
                st.metric("Iterações", iteration)
            
            st.markdown("---")
            
            # ✅ CORRIGIDO: Verificar se já está no checkpoint
            current_step = state.get("current_step", "")
            if current_step in ["wait_user_approval", "waiting_approval"]:
                st.session_state.execution_paused = True
                st.warning("⏸️ **Execução pausada no checkpoint**")
                st.info("👉 Vá para a aba **'Planejamento'** para aprovar ou solicitar ajustes no plano.")
            
            # Botão de execução
            if not st.session_state.execution_paused:
                if st.button("▶️ Executar Próximo Passo", type="primary", use_container_width=True):
                    with st.spinner("Executando..."):
                        try:
                            # Executar um passo do grafo
                            config = {"configurable": {"thread_id": st.session_state.session_id}}
                            
                            result = graph.invoke(state, config)
                            
                            # ✅ Verificar se resultado é válido
                            if result is None:
                                st.error("Erro: Grafo retornou None. Possível problema de configuração.")
                                logger.log_node_error("execution", Exception("Graph returned None"))
                                return
                            
                            st.session_state.state = result
                            
                            # Verificar se chegou no checkpoint
                            if result.get("current_step") in ["wait_user_approval", "waiting_approval"]:
                                st.session_state.execution_paused = True
                                st.info("⏸️ Execução pausada. Aguardando sua aprovação na aba 'Planejamento'")
                            
                            st.rerun()
                            
                        except Exception as e:
                            st.error(f"Erro na execução: {str(e)}")
                            import traceback
                            st.code(traceback.format_exc())
                            logger.log_node_error("execution", e)
            else:
                st.info("⏸️ Execução pausada. Aprove o plano na aba 'Planejamento' para continuar.")
            
            # Mensagens e erros
            if state.get("errors"):
                st.markdown("### ❌ Erros")
                for error in state["errors"]:
                    st.error(error)
            
            if state.get("warnings"):
                st.markdown("### ⚠️ Avisos")
                for warning in state["warnings"]:
                    st.warning(warning)


# TAB 4: RESULTADOS
with tab4:
    st.markdown("### 📦 Solução Gerada")
    
    if not st.session_state.execution_started:
        st.info("👈 Comece descrevendo sua demanda na aba 'Input da Demanda'")
    else:
        state = st.session_state.state
        
        if state and state.get("solution"):
            solution = get_solution(state)
            
            st.success("✅ Solução construída com sucesso!")
            
            # Validação
            if state.get("validation_result"):
                validation = state["validation_result"]
                if validation["is_valid"]:
                    st.success("✅ Solução validada e pronta para uso!")
                else:
                    st.warning("⚠️ Solução tem alguns avisos")
                
                with st.expander("📊 Detalhes da Validação"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("**Checks Passados:**")
                        for check in validation.get("passed_checks", []):
                            st.write(f"✅ {check}")
                    with col2:
                        st.write("**Checks Falhados:**")
                        for check in validation.get("failed_checks", []):
                            st.write(f"❌ {check}")
            
            st.markdown("---")
            
            # Arquivos gerados
            if solution.files:
                st.markdown("### 📁 Arquivos Gerados")
                
                for filename, content in solution.files.items():
                    with st.expander(f"📄 {filename}"):
                        # Detectar linguagem pelo filename
                        if filename.endswith(".py"):
                            lang = "python"
                        elif filename.endswith(".md"):
                            lang = "markdown"
                        elif filename.endswith(".txt"):
                            lang = "text"
                        elif filename.endswith(".json"):
                            lang = "json"
                        else:
                            lang = None
                        
                        st.code(content, language=lang)
                        
                        # Botão de download
                        st.download_button(
                            label=f"⬇️ Download {filename}",
                            data=content,
                            file_name=filename,
                            mime="text/plain"
                        )
            
            # Documentação
            if solution.documentation:
                st.markdown("### 📚 Documentação")
                st.markdown(solution.documentation)
            
            # Dependências
            if solution.dependencies:
                st.markdown("### 📦 Dependências")
                st.code("\n".join(solution.dependencies))
                
                st.download_button(
                    label="⬇️ Download requirements.txt",
                    data="\n".join(solution.dependencies),
                    file_name="requirements.txt",
                    mime="text/plain"
                )
        else:
            st.info("⏳ Solução ainda não foi gerada. Continue o processamento na aba 'Execução'")


# TAB 5: LOGS
with tab5:
    st.markdown("### 📊 Logs de Execução")
    
    logs = logger.get_session_logs()
    
    if not logs:
        st.info("Nenhum log disponível ainda")
    else:
        # Resumo
        summary = logger.get_logs_summary()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total de Logs", summary["total"])
        with col2:
            st.metric("Nós Executados", len(summary["nodes_executed"]))
        with col3:
            errors = summary["by_level"].get("ERROR", 0)
            st.metric("Erros", errors, delta_color="inverse")
        with col4:
            success = summary["by_level"].get("SUCCESS", 0)
            st.metric("Sucessos", success)
        
        st.markdown("---")
        
        # Filtros
        col1, col2 = st.columns(2)
        with col1:
            filter_level = st.multiselect(
                "Filtrar por nível:",
                options=list(summary["by_level"].keys()),
                default=list(summary["by_level"].keys())
            )
        with col2:
            filter_type = st.multiselect(
                "Filtrar por tipo:",
                options=list(summary["by_type"].keys()),
                default=list(summary["by_type"].keys())
            )
        
        # Mostrar logs
        st.markdown("### 📜 Timeline de Logs")
        
        for log in reversed(logs):  # Mais recentes primeiro
            if log["level"] in filter_level and log["type"] in filter_type:
                timestamp = log["timestamp"].strftime("%H:%M:%S")
                level = log["level"]
                message = log["message"]
                
                # Cor baseada no nível
                if level == "ERROR":
                    st.error(f"**[{timestamp}]** {message}")
                elif level == "WARNING":
                    st.warning(f"**[{timestamp}]** {message}")
                elif level == "SUCCESS":
                    st.success(f"**[{timestamp}]** {message}")
                else:
                    st.info(f"**[{timestamp}]** {message}")
        
        # Botão de export
        if st.button("📥 Exportar Logs"):
            filepath = logger.export_logs_to_file()
            st.success(f"Logs exportados para: {filepath}")


# ========================================
# FOOTER
# ========================================

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem;">
    <p>AI Agent Flow v1.0 | Powered by LangGraph + Streamlit</p>
    <p>Session ID: {}</p>
</div>
""".format(st.session_state.session_id), unsafe_allow_html=True)