import streamlit as st
import i18n
import interaction_ui

def render_sources_view(current_section):
    st.markdown(f"<h2 style='text-align: center; color: var(--primary-color);'>{i18n.t('mode_6')}</h2>", unsafe_allow_html=True)
    st.divider()

    if current_section == i18n.t("m6_sub_sources_title"):
        st.markdown(f"### 📄 {i18n.t('m6_sub_sources_title')}")
        
        st.info("Todos os dados apresentados nesta aplicação têm como base documentos oficiais públicos da Polícia Civil do Estado de São Paulo e legislação vigente.", icon="🏛️")
        
        st.markdown("""
        **Documentos e Editais (Histórico e Recentes):**
        * Editais de Concurso Público (Ex: Acadepol / Vunesp).
        * Portarias e Resoluções da Delegacia Geral de Polícia (DGP).
        
        **Legislação Estadual:**
        * Leis Orgânicas da Polícia Civil (ex: LOPC/SP - LC 207/1979).
        * Decretos estaduais regulamentadores de atribuições (Ex: Decreto 47.788/1967).
        * Projetos de Lei Complementar em tramitação ou recentemente aprovados sobre a reestruturação das carreiras policiais (Ex: 2024/2025).
        
        *Nota: O detalhamento exato dos documentos extraídos para cada cenário encontra-se documentado na raiz do projeto.*
        """)
        
        # Opcional: Like button de interação
        if 'interaction_ui' in globals():
            interaction_ui.render_like_button("6.1 Fontes Públicas", "6_1")

    elif current_section == i18n.t("m6_sub_principles_title"):
        st.markdown(f"### ⚖️ {i18n.t('m6_sub_principles_title')}")
        
        st.warning("🚧 **Seção em Construção:** Os princípios orientadores utilizados na interpretação dos dados e metodologias serão listados aqui em breve pelo autor.")
        
        st.markdown("""
        *Esta seção detalhará as premissas lógicas, acadêmicas e operacionais que nortearam a categorização de atribuições (ex: o que foi considerado atribuição meio vs fim, critérios de equivalência semântica e agrupamento de sinônimos).*
        """)
        
        # Opcional: Like button de interação
        if 'interaction_ui' in globals():
            interaction_ui.render_like_button("6.2 Princípios do Autor", "6_2")
