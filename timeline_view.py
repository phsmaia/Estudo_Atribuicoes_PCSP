import streamlit as st
import pandas as pd
import plotly.express as px
import data_processing
import numpy as np
import json
import os
import explanations
import i18n
import interaction_ui

def render_timeline_mode(opcoes_cenarios, mapa_cenarios):
    st.markdown(i18n.t("m3_intro"))
    
    # --- CARREGAMENTO DO DICIONÁRIO DE MAPA GERAL ---
    mapa_dict = {}
    try:
        if os.path.exists('csv_dump.json'):
            with open('csv_dump.json', 'r', encoding='utf-8') as f:
                lista_mapa = json.load(f)
                for row in lista_mapa:
                    mapa_dict[row['Atual Sem Correção']] = row
    except Exception as e:
        st.error(f"{i18n.t('err_load_global_map')} {e}")
        pass
        
    cargos_base = list(mapa_dict.keys()) if mapa_dict else []
    
    data_macro = []
    
    # Dicionários para rastreamento longitudinal
    hist_volume = {c: {} for c in cargos_base}
    hist_adj = {c: {} for c in cargos_base}
    hist_grafo = {c: {} for c in cargos_base}
    hist_gower = {c: {} for c in cargos_base}
    hist_vizinho = {c: {} for c in cargos_base}
    hist_exclusivas = {c: {} for c in cargos_base}
    hist_compartilhadas = {c: {} for c in cargos_base}
    
    with st.spinner(i18n.t("m3_spinner")):
        for cenario in opcoes_cenarios:
            df = mapa_cenarios[cenario]
            if df is None or df.empty:
                continue
                
            df_temp = df.copy()
            if 'Carreira' in df_temp.columns:
                df_temp = df_temp.set_index('Carreira')
            df_temp = df_temp.apply(pd.to_numeric, errors='coerce').fillna(0)
            
            # --- MACRO MÉTRICAS ---
            num_atribuicoes_ativas = (df_temp.sum(axis=0) > 0).sum()
            colunas_ativas = df_temp.loc[:, df_temp.sum(axis=0) > 0]
            media_compartilhamento = colunas_ativas.sum(axis=0).mean() if not colunas_ativas.empty else 0
            
            gower_df = data_processing.calcular_distancias_gower(df_temp)
            if len(gower_df) > 1:
                mask = np.triu(np.ones(gower_df.shape), k=1).astype(bool)
                media_gower = gower_df.where(mask).mean().mean()
            else:
                media_gower = 0
                
            data_macro.append({
                "Cenário": i18n.t(cenario) if i18n.t(cenario) != cenario else cenario,
                i18n.t("m3_col_active_roles"): len(df_temp.index),
                i18n.t("m3_col_total_unique"): num_atribuicoes_ativas,
                i18n.t("m3_col_sharing_level"): media_compartilhamento,
                i18n.t("m3_col_gower"): media_gower
            })
            
            # --- MICRO MÉTRICAS (LONGITUDINAL) ---
            if not cargos_base:
                continue
                
            df_limpo = data_processing.remover_atribuicoes_comuns(df_temp)
            adj_matrix = data_processing.gerar_matriz_adjacencia(df_temp)
            
            # Para o grafo inter-cenários, vamos usar um threshold fixo de 2 ou 3 se não houver UI ainda, 
            # Mas podemos extrair a aresta crua se quisermos, porém o slider está fora do loop.
            # O ideal é extrair o valor da adjacência e deixar a tabela mostrar "Adjacencia Bruta" 
            # já que não temos o slider de threshold no topo antes do processamento.
            # Vamos gerar o grafo com threshold=1 para contar qualquer conexão.
            nodes, edges, pos = data_processing.gerar_dados_grafo(adj_matrix, threshold=1)
            
            for c_base in cargos_base:
                c_cenario = mapa_dict[c_base].get(cenario, "")
                
                if c_cenario in df_temp.index:
                    hist_volume[c_base][cenario] = int(df_limpo.loc[c_cenario].sum())
                    
                    atribs_cargo = df_temp.columns[df_temp.loc[c_cenario] == 1]
                    somas_atribs = df_temp[atribs_cargo].sum(axis=0)
                    hist_exclusivas[c_base][cenario] = int((somas_atribs == 1).sum())
                    hist_compartilhadas[c_base][cenario] = int((somas_atribs > 1).sum())
                    
                    soma_adj = adj_matrix.loc[c_cenario].sum() - adj_matrix.loc[c_cenario, c_cenario]
                    hist_adj[c_base][cenario] = int(soma_adj)
                    
                    degree = sum(1 for e in edges if e["source"] == c_cenario or e["target"] == c_cenario)
                    hist_grafo[c_base][cenario] = int(degree)
                    
                    dist = gower_df[c_cenario].drop(c_cenario)
                    if not dist.empty:
                        hist_gower[c_base][cenario] = dist.mean()
                        hist_vizinho[c_base][cenario] = dist.idxmin()
                    else:
                        hist_gower[c_base][cenario] = None
                        hist_vizinho[c_base][cenario] = "Isolado"
                else:
                    hist_volume[c_base][cenario] = None
                    hist_exclusivas[c_base][cenario] = None
                    hist_compartilhadas[c_base][cenario] = None
                    hist_adj[c_base][cenario] = None
                    hist_grafo[c_base][cenario] = None
                    hist_gower[c_base][cenario] = None
                    hist_vizinho[c_base][cenario] = "Extinto"

    # --- RENDERIZAÇÃO DA VISÃO MACRO ---
    df_metrics = pd.DataFrame(data_macro)
    
    col1, col2 = st.columns(2)
    
    fig1 = px.bar(df_metrics, x="Cenário", y=i18n.t("m3_col_gower"), text=i18n.t("m3_col_gower"),
                   color=i18n.t("m3_col_gower"), color_continuous_scale="Teal")
    fig1.update_traces(texttemplate='%{text:.3f}', textposition='outside')
    fig1.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='white'), margin=dict(l=0, r=0, t=30, b=0), coloraxis_showscale=False)
    
    with col1:
        st.subheader(i18n.t("m3_sub_gower_title"), help=i18n.t("m3_sub_gower_help"))
        st.plotly_chart(fig1, use_container_width=True)
        interaction_ui.render_like_button("3.1 Distancia Media Gower", "3_1")
        st.markdown(f"<p style='font-size:0.8rem; color:#aaa; margin-top:5px;'>{i18n.t('m3_gower_desc')}</p>", unsafe_allow_html=True)
        if st.session_state.get('show_explanations', False):
            st.info(explanations.get_explanation("gower", tone=st.session_state.get('explanation_tone', 'tecnico'), language=st.session_state.get('language', 'PT-BR')))
    
    fig2 = px.bar(df_metrics, x="Cenário", y=i18n.t("m3_col_total_unique"), text=i18n.t("m3_col_total_unique"),
                  color=i18n.t("m3_col_total_unique"), color_continuous_scale="Viridis")
    fig2.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='white'), margin=dict(l=0, r=0, t=30, b=0), coloraxis_showscale=False)
    fig2.update_traces(textposition='outside')
    
    with col2:
        st.subheader(i18n.t("m3_sub_vol_title"), help=i18n.t("m3_sub_vol_help"))
        st.plotly_chart(fig2, use_container_width=True)
        interaction_ui.render_like_button("3.2 Volume de Atribuicoes", "3_2")
        st.markdown(f"<p style='font-size:0.8rem; color:#aaa; margin-top:5px;'>{i18n.t('m3_vol_desc')}</p>", unsafe_allow_html=True)
        if st.session_state.get('show_explanations', False):
            st.info(explanations.get_explanation("m3_macro_31", tone=st.session_state.get('explanation_tone', 'tecnico'), language=st.session_state.get('language', 'PT-BR')))
        
    st.markdown("---")
    
    fig3 = px.bar(df_metrics, x="Cenário", y=i18n.t("m3_col_sharing_level"), text=i18n.t("m3_col_sharing_level"),
                   color=i18n.t("m3_col_sharing_level"), color_continuous_scale="Oranges")
    fig3.update_traces(texttemplate='%{text:.2f}', textposition='outside')
    fig3.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='white'), margin=dict(l=0, r=0, t=30, b=0), coloraxis_showscale=False)
    
    st.subheader(i18n.t("m3_sub_share_title"), help=i18n.t("m3_sub_share_help"))
    st.plotly_chart(fig3, use_container_width=True)
    interaction_ui.render_like_button("3.3 Nivel de Compartilhamento", "3_3")
    st.markdown(f"<p style='font-size:0.8rem; color:#aaa; margin-top:5px;'>{i18n.t('m3_share_desc')}</p>", unsafe_allow_html=True)
    if st.session_state.get('show_explanations', False):
        st.info(explanations.get_explanation("m3_macro_33", tone=st.session_state.get('explanation_tone', 'tecnico'), language=st.session_state.get('language', 'PT-BR')))

    st.markdown("<div style='height: 150px;'></div>", unsafe_allow_html=True)
