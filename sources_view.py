import streamlit as st
import i18n
import interaction_ui

def render_sources_view(current_section):
    st.markdown(f"<h2 style='text-align: center; color: var(--primary-color);'>{i18n.t('mode_2')}</h2>", unsafe_allow_html=True)
    st.divider()

    if current_section == "m6_sub_sources_title":
        st.markdown(f"### 📄 {i18n.t('m6_sub_sources_title')}")
        
        st.info("Todos os dados apresentados nesta aplicação têm como base documentos oficiais públicos da Polícia Civil do Estado de São Paulo, legislação vigente, bem como notícias e reuniões oficiais sobre a reestruturação da instituição.", icon="🏛️")
        
        try:
            import os
            base_dir = os.path.dirname(os.path.abspath(__file__))
            file_path = os.path.join(base_dir, "Fonte_Documentos.md")
            with open(file_path, "r", encoding="utf-8") as f:
                fontes_md = f.read()
            
            # Substituir a tag markdown por uma tag HTML img com base64 para que a imagem fique renderizada DENTRO da lista e em tamanho menor
            image_tag = "![Tabela de Cargos da Segunda Reunião Reestruturação PC SP 2025](assets\\Apresentacao_2a_reuniao_reestruturacaoPCSP.jpeg)"
            img_path = os.path.join(base_dir, "assets", "Apresentacao_2a_reuniao_reestruturacaoPCSP.jpeg")
            
            if image_tag in fontes_md and os.path.exists(img_path):
                import base64
                with open(img_path, "rb") as img_file:
                    b64_img = base64.b64encode(img_file.read()).decode()
                
                img_html = f'<div style="margin-top: 10px; margin-bottom: 15px;"><img src="data:image/jpeg;base64,{b64_img}" style="width: 100%; max-width: 600px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);" alt="Tabela de Cargos da Segunda Reunião"></div>'
                fontes_md = fontes_md.replace(image_tag, img_html)
            elif image_tag in fontes_md:
                # Caso a imagem não exista no disco, apenas remove a tag
                fontes_md = fontes_md.replace(image_tag, "")
                
            st.markdown(fontes_md, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Erro ao carregar Fonte_Documentos.md: {e}")
        
        # Opcional: Like button de interação
        if 'interaction_ui' in globals():
            interaction_ui.render_like_button("6.1 Fontes Públicas", "6_1")

    elif current_section == "m6_sub_principles_title":
        st.markdown(f"### ⚖️ {i18n.t('m6_sub_principles_title')}")
        
        try:
            import os
            base_dir = os.path.dirname(os.path.abspath(__file__))
            lang = st.session_state.get('language', 'PT-BR')
            file_name = "Principles_Application_and_Study.md" if lang == "EN" else "Principios_Aplicacao_e_Estudo.md"
            file_path = os.path.join(base_dir, file_name)
            with open(file_path, "r", encoding="utf-8") as f:
                principles_md = f.read()
            st.markdown(principles_md, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Erro ao carregar arquivo de princípios: {e}")
        
        # Opcional: Like button de interação
        if 'interaction_ui' in globals():
            interaction_ui.render_like_button("6.2 Princípios do Autor", "6_2")

    elif current_section == "m6_sub_faq_title":
        st.markdown(f"### ❓ {i18n.t('m6_sub_faq_title')}")
        if st.session_state.get('language', 'PT-BR') == 'EN':
            st.warning("🚧 **Under Construction:** Frequently asked questions will be listed here soon.")
        else:
            st.warning("🚧 **Seção em Construção:** As perguntas frequentes serão listadas aqui em breve.")

    elif current_section == "m6_sub_tech_list_title":
        st.markdown(f"### 🛠️ {i18n.t('m6_sub_tech_list_title')}")
        if st.session_state.get('language', 'PT-BR') == 'EN':
            st.warning("🚧 **Under Construction:** The technical list will be detailed here soon.")
        else:
            st.warning("🚧 **Seção em Construção:** A lista técnica será detalhada aqui em breve.")
