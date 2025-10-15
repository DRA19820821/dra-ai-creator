# components/requirements_feedback.py

import streamlit as st
from typing import List, Dict

def show_requirements_feedback(
    issues: List[Dict[str, str]], 
    original_demand: str,
    attempt_number: int = 1
):
    """
    Exibe feedback sobre requisitos não aprovados de forma interativa
    
    Args:
        issues: Lista de dicionários com 'problema' e 'sugestao'
        original_demand: Descrição original do usuário
        attempt_number: Número da tentativa atual
    """
    
    # Header com status
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("### 🔍 Revisão dos Requisitos")
    with col2:
        st.metric("Tentativa", f"{attempt_number}/3")
    
    # Explicação amigável
    st.info("""
    🤖 **O que aconteceu?**
    
    Analisamos sua descrição e identificamos alguns pontos que precisam ser mais específicos 
    para criar a melhor solução possível para você.
    """)
    
    # Mostrar issues com expansores
    st.markdown("### ⚠️ Pontos a esclarecer:")
    
    for i, issue in enumerate(issues, 1):
        with st.expander(f"**Ponto {i}:** {issue['problema'][:80]}...", expanded=True):
            st.error(f"**Problema identificado:**\n{issue['problema']}")
            st.success(f"**{issue['sugestao']}**")
            
            # Mini exemplo inline
            if 'visualizações' in issue['problema'].lower():
                st.code("""
Exemplo de descrição clara:
"Preciso de um gráfico de barras mostrando 
o saldo médio por faixa de dias de atraso"
                """, language="text")
    
    st.markdown("---")
    
    # Área de refinamento com tabs
    tab1, tab2, tab3 = st.tabs(["✏️ Refinar", "💡 Dicas", "📝 Exemplo Completo"])
    
    with tab1:
        st.markdown("**Reescreva sua necessidade incluindo os detalhes solicitados:**")
        
        # Mostrar descrição original em destaque
        with st.container():
            st.markdown("**Sua descrição original:**")
            st.text_area(
                "Original", 
                value=original_demand, 
                height=100, 
                disabled=True,
                label_visibility="collapsed"
            )
        
        # Área para nova descrição
        refined = st.text_area(
            "Nova descrição (mais detalhada):",
            placeholder="Cole aqui sua descrição original e adicione os detalhes solicitados acima...",
            height=250,
            key=f"refined_demand_{attempt_number}"
        )
        
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            submit = st.button(
                "🚀 Processar novamente", 
                type="primary",
                use_container_width=True
            )
        
        with col2:
            if st.button("🔄 Usar IA para ajudar", use_container_width=True):
                st.session_state['use_ai_helper'] = True
        
        with col3:
            if st.button("❌", help="Cancelar"):
                st.session_state.clear()
                st.rerun()
        
        if submit and refined:
            return refined
        elif submit:
            st.warning("⚠️ Por favor, preencha a descrição refinada")
    
    with tab2:
        show_refinement_tips(issues)
    
    with tab3:
        show_complete_example()
    
    return None


def show_refinement_tips(issues: List[Dict]):
    """Mostra dicas contextuais baseadas nos issues"""
    
    st.markdown("### 💡 Checklist para uma boa descrição:")
    
    checklist = {
        'visualizações': [
            "Tipo de gráfico (barras, linha, pizza, mapa, tabela)",
            "Quais dados visualizar (eixo X e Y)",
            "Filtros ou segmentações necessárias"
        ],
        'alertas': [
            "Condição para disparar (ex: quando X > Y)",
            "Canal de notificação (email, dashboard, Slack)",
            "Frequência de verificação (tempo real, diária, semanal)"
        ],
        'métrica': [
            "Nome da métrica",
            "Fórmula de cálculo precisa",
            "Unidade de medida (%, R$, quantidade)"
        ],
        'dados': [
            "Colunas necessárias da base",
            "Período de análise (último mês, 12 meses, etc.)",
            "Granularidade (dia, semana, mês)"
        ]
    }
    
    # Mostrar checklist relevante baseado nos issues
    for issue in issues:
        for key, items in checklist.items():
            if key in issue['problema'].lower():
                st.markdown(f"**Para {key}:**")
                for item in items:
                    st.markdown(f"- ✓ {item}")


def show_complete_example():
    """Mostra exemplo completo de descrição bem estruturada"""
    
    st.markdown("### 📝 Exemplo de descrição completa e clara:")
    
    st.markdown("""
    **Contexto:**
    Tenho uma base de dados de carteira de crédito com as seguintes colunas:
    - customer_id (identificador único)
    - saldo_atual (valor em R$)
    - dias_atraso (número de dias de atraso no pagamento)
    - data_referencia (data da coleta do dado)
    - regiao (região geográfica)
    
    ---
    
    **Visualizações necessárias:**
    
    1. **Dashboard principal** contendo:
       - Gráfico de barras: distribuição de clientes por faixa de saldo (0-1k, 1k-5k, 5k-10k, 10k+)
       - Gráfico de linha: evolução mensal da taxa de inadimplência nos últimos 12 meses
       - KPI cards no topo: total de clientes, saldo total, taxa de inadimplência, saldo médio
       - Filtros: por região e período
    
    2. **Gráfico de pizza**: proporção de clientes por faixa de dias de atraso (0, 1-30, 31-60, 61-90, 90+)
    
    ---
    
    **Métricas e cálculos:**
    
    - **Taxa de inadimplência**: percentual de clientes com dias_atraso >= 30
    - **Saldo em risco**: soma do saldo_atual dos clientes com dias_atraso >= 60
    - **Evolução mensal**: comparação percentual com mês anterior
    
    ---
    
    **Alertas necessários:**
    
    1. Email para equipe@empresa.com quando:
       - Taxa de inadimplência aumentar mais de 10% em relação ao mês anterior
       - Saldo em risco ultrapassar R$ 5 milhões
    
    2. Verificação: diária (às 8h da manhã)
    """)
    
    st.success("✅ Esta descrição contém todos os elementos necessários!")


# Função auxiliar para usar IA como ajudante
def ai_helper_for_refinement(original: str, issues: List[Dict]) -> str:
    """Usa LLM para sugerir uma versão refinada da descrição"""
    
    with st.spinner("🤖 IA gerando sugestão de refinamento..."):
        # Prompt para o LLM
        prompt = f"""
        Descrição original do usuário:
        {original}
        
        Problemas identificados:
        {[issue['problema'] for issue in issues]}
        
        Reescreva a descrição do usuário incluindo os detalhes necessários para resolver 
        os problemas identificados. Mantenha o estilo e contexto original, apenas adicione 
        as especificações faltantes de forma natural.
        """
        
        # Chamar LLM (implementar com seu modelo)
        # refined = call_llm(prompt)
        
        # Por enquanto, retornar placeholder
        refined = f"{original}\n\n[IA adicionaria aqui os detalhes sugeridos]"
        
        return refined
    

if __name__ == "__main__":
    # Teste do componente
    test_issues = [
        {
            'problema': 'Ambiguidade na definição de visualizações',
            'sugestao': '📊 Especifique o tipo de gráfico e quais dados visualizar'
        },
        {
            'problema': 'Definição da métrica principal incompleta',
            'sugestao': '📐 Explique como calcular a métrica'
        }
    ]
    
    test_demand = "Preciso de visualizações e alertas sobre inadimplência"
    
    result = show_requirements_feedback(test_issues, test_demand, 1)
    if result:
        st.success(f"Nova descrição: {result}")