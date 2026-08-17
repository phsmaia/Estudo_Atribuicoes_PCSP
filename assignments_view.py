import streamlit as st
import pandas as pd
import i18n
import data_loader
import explanations
import os

def render_assignments_view(current_section=None):
    st.markdown(f"<h2 style='text-align: center; color: var(--primary-color);'>{i18n.t('mode_1')}</h2>", unsafe_allow_html=True)
    st.divider()

    lang = st.session_state.get('language', 'PT-BR')
    tone_key = 'leigo' if st.session_state.get('toggle_leigo', False) else 'tecnico'

    # Setup Tabs
    tab1, tab2 = st.tabs([
        "Catálogo de Atribuições" if lang == 'PT-BR' else "Assignments Catalog",
        "Tabela de Conversão de Cargos" if lang == 'PT-BR' else "Role Conversion Table"
    ])

    with tab1:
        st.markdown("Navegue por todas as atribuições históricas e atuais, organizadas e traduzidas de acordo com o idioma selecionado." if lang == 'PT-BR' else "Browse through all historical and current assignments, organized and translated according to the selected language.")

        # Textos Explicativos
        if st.session_state.get('show_explanations', False):
            st.info(explanations.get_explanation("mode_1_catalog", tone_key))

        # Legenda de Status
        with st.expander("📌 Legenda de Status / Status Legend" if lang == 'EN' else "📌 Legenda de Status"):
            if lang == 'PT-BR':
                st.markdown("""
                * **Mantida Inicialmente:** atribuições comuns a todos os policiais, conforme Portaria DGP 30/2012.
                * **Mantida:** atribuições pertencentes a pelo menos um dos cargos vindo de editais ou outras normas.
                * **Retirada:** atribuições retiradas do escopo do projeto pois estão repetidas ou possuem a mesma essência de outra.
                * **Modificação:** atribuições criadas para substituirem outras, gerando novidades de atribução e consequentemente alterações de situações de atribuições e cargos.
                * **Antiga:** atribuições advindas de Decreto 47788/1967, que ainda estão em voga ou foram "atualizadas" pela DGP 30/2012 ou editais recentes.
                """)
            else:
                st.markdown("""
                * **Initially Kept:** Assignments common to all police officers, per DGP Ordinance 30/2012.
                * **Kept:** Assignments belonging to at least one of the roles coming from notices or other norms.
                * **Removed:** Assignments removed from the project's scope as they are repeated or share the same essence as another.
                * **Modified:** Assignments created to substitute others, generating assignment novelties and consequently altering the situations of assignments and roles.
                * **Old:** Assignments from Decree 47788/1967, which are still in effect or were "updated" by DGP 30/2012 or recent notices.
                """)

        # Load base dataset
        datasets = data_loader.get_all_datasets()
        df_editais = datasets.get("editais")
        
        if df_editais is None or df_editais.empty:
            st.error("Não foi possível carregar a base de dados de atribuições (Atribuicoes_Carreiras_Editais.CSV).")
        else:
            # Work on a copy to translate
            df_display = df_editais.copy()
            
            # Translate columns if necessary
            if lang == 'EN':
                # Map pre-translated english columns if they exist
                if 'Carreira_Inglês' in df_display.columns:
                    df_display['Carreira'] = df_display['Carreira_Inglês']
                if 'atribuicao_inglês' in df_display.columns:
                    df_display['atribuicao'] = df_display['atribuicao_inglês']
                if 'Reduzida_Inglês' in df_display.columns:
                    df_display['Reduzida'] = df_display['Reduzida_Inglês']
                if 'Norma_Inglês' in df_display.columns:
                    df_display['Norma'] = df_display['Norma_Inglês']
                if 'Status_Inglês' in df_display.columns:
                    df_display['Status'] = df_display['Status_Inglês']
                if 'Mesclada_Inglês' in df_display.columns:
                    df_display['Mesclada'] = df_display['Mesclada_Inglês']
                    
                # Rename columns for display
                df_display = df_display.rename(columns={
                    'Norma': 'Norm/Source',
                    'Carreira': 'Career / Role',
                    'atribuicao': 'Full Assignment',
                    'Reduzida': 'Short Description',
                    'Status': 'Status',
                    'Mesclada': 'Merged'
                })
            else:
                df_display = df_display.rename(columns={
                    'Norma': 'Norma/Edital',
                    'Carreira': 'Carreira',
                    'atribuicao': 'Atribuição Completa',
                    'Reduzida': 'Atribuição Reduzida'
                })

            # Remove internal translation columns to avoid cluttering the view
            cols_to_drop = [
                'Carreira_Inglês', 'atribuicao_inglês', 'Reduzida_Inglês', 
                'Norma_Inglês', 'Status_Inglês', 'Mesclada_Inglês', 'num_atrib'
            ]
            df_display = df_display.drop(columns=[c for c in cols_to_drop if c in df_display.columns])

            # Filters
            st.markdown(f"#### 🔍 Filtros / Filters" if lang == 'EN' else f"#### 🔍 Filtros")
            col1, col2 = st.columns(2)
            
            carreira_col = 'Career / Role' if lang == 'EN' else 'Carreira'
            norma_col = 'Norm/Source' if lang == 'EN' else 'Norma/Edital'

            with col1:
                carreiras_unicas = sorted([str(x) for x in df_display[carreira_col].dropna().unique()])
                selected_carreiras = st.multiselect(
                    "Filtrar por Carreira / Filter by Role" if lang == 'EN' else "Filtrar por Carreira",
                    options=carreiras_unicas,
                    default=[]
                )
            
            with col2:
                normas_unicas = sorted([str(x) for x in df_display[norma_col].dropna().unique()])
                selected_normas = st.multiselect(
                    "Filtrar por Norma / Filter by Norm" if lang == 'EN' else "Filtrar por Norma/Edital",
                    options=normas_unicas,
                    default=[]
                )

            # Apply filters
            if selected_carreiras:
                df_display = df_display[df_display[carreira_col].isin(selected_carreiras)]
            if selected_normas:
                df_display = df_display[df_display[norma_col].isin(selected_normas)]

            st.markdown(f"**Total de registros:** {len(df_display)}" if lang == 'PT-BR' else f"**Total records:** {len(df_display)}")

            # Display interactive dataframe
            st.dataframe(
                df_display,
                use_container_width=True,
                hide_index=True,
                height=600
            )

    with tab2:
        st.markdown("Consulte a tabela de equivalência e conversão de cargos ao longo das reestruturações e marcos legais." if lang == 'PT-BR' else "Consult the role equivalence and conversion table across restructurings and legal milestones.")
        
        # Textos Explicativos
        if st.session_state.get('show_explanations', False):
            st.info(explanations.get_explanation("mode_1_conversion", tone_key))
            
        conv_path = 'Tabela_Conversao_Cargos.CSV'
        if not os.path.exists(conv_path):
            st.error("Não foi possível carregar a Tabela de Conversão (Tabela_Conversao_Cargos.CSV).")
        else:
            try:
                df_conv = pd.read_csv(conv_path, encoding='utf-8-sig', sep=';')
            except UnicodeDecodeError:
                df_conv = pd.read_csv(conv_path, encoding='iso-8859-1', sep=';')
            
            # Remove blank rows
            df_conv = df_conv.dropna(how='all')
                
            if lang == 'EN':
                col_translations = {
                    'Atual Sem Correção': 'Current Uncorrected',
                    'Atual Com Correção': 'Current Corrected',
                    'LONPC Sem Correção': 'LONPC Uncorrected',
                    'LONPC Com Correção': 'LONPC Corrected',
                    'Reestruturação 2024': '2024 Restructuring',
                    'Reestruturação Reunião 1 2025': '2025 Rest. Gov R1',
                    'Reestruturação Reunião 2 2025': '2025 Rest. Gov R2',
                    'Decreto 47788 / 1967': 'Decree 47788 / 1967'
                }
                df_conv = df_conv.rename(columns=col_translations)
                for col in df_conv.columns:
                    df_conv[col] = df_conv[col].apply(lambda x: i18n.traduzir_cargo(x) if pd.notna(x) and isinstance(x, str) else x)
            
            st.dataframe(
                df_conv,
                use_container_width=True,
                hide_index=True
            )
            
    # Optional interaction like button
    if 'interaction_ui' in globals():
        pass
