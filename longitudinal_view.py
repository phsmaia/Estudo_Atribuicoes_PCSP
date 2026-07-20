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
import hashlib

def render_longitudinal_mode(opcoes_cenarios, mapa_cenarios, filtro_cargos, cargos_destaque, current_section=None):
    lang = st.session_state.get('language', 'PT-BR')
    traduzir = lang == 'EN'

    if lang == 'EN':
        with st.expander("📚 Brazilian Police Roles Glossary"):
            st.markdown("""
            **Roles Translation (Approximations):**
            - **Delegado de Polícia**: Police Chief / Police Delegate
            - **Investigador de Polícia**: Police Investigator / Detective
            - **Escrivão de Polícia**: Police Clerk / Desk Officer
            - **Agente Policial**: Police Agent / Operative
            - **Carcereiro Policial**: Police Jailer
            - **Agente de Telecomunicações Policial**: Police Telecommunications Agent / Dispatcher
            - **Papiloscopista Policial**: Fingerprint Examiner / Dactyloscopist
            - **Auxiliar de Papiloscopista Policial**: Fingerprint Examiner Assistant
            - **Perito Criminal**: Forensic Expert / Criminalist
            - **Médico Legista**: Medical Examiner / Forensic Pathologist
            - **Fotógrafo Técnico-Pericial**: Forensic Photographer
            - **Desenhista Técnico-Pericial**: Forensic Sketch Artist
            - **Atendente de Necrotério Policial**: Morgue Attendant
            - **Auxiliar de Necropsia**: Autopsy Assistant
            
            *(Note: 'Odontolegista' is not listed separately here because it's functionally merged within Medical Examiner and Forensic Expert duties in this dataset).*
            """)
            
    # CSS para as tabelas HTML
    st.markdown("""
    <style>
    .html-table { width: 100%; border-collapse: collapse; color: #e0e0e0; font-size: 0.95rem; margin-bottom: 20px;}
    .html-table th { background-color: #2D2D2D; padding: 12px 10px; text-align: left; border-bottom: 2px solid #4CAF50;}
    .html-table td { padding: 10px 10px; border-bottom: 1px solid #444; }
    .html-table tr:hover { background-color: #333 !important; opacity: 1.0 !important; }
    .up-arrow { color: #4CAF50; font-weight: bold; }
    .down-arrow { color: #F44336; font-weight: bold; }
    .flat-arrow { color: #9E9E9E; }
    .jump-arrow { color: #FFC107; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown(i18n.t("m4_intro_title"))
    st.markdown(i18n.t("m4_intro_desc"))
    if st.session_state.get('show_explanations', False):
        st.info(explanations.get_explanation("m4_micro_inicio", tone=st.session_state.get('explanation_tone', 'tecnico'), language=lang))
    
    # Load Dict
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
    if not cargos_base or not filtro_cargos:
        st.warning(i18n.t("m4_warning_no_career"))
        return
        
    # Mapeamento de cores fixas para as carreiras
    cores_padrao = px.colors.qualitative.Plotly + px.colors.qualitative.Dark24
    mapa_cores = {c: cores_padrao[i % len(cores_padrao)] for i, c in enumerate(cargos_base)}
        
    # --- PREPROCESS DATA ---
    hist_volume = {c: {} for c in cargos_base}
    hist_adj = {c: {} for c in cargos_base}
    hist_grafo = {c: {} for c in cargos_base}
    hist_gower = {c: {} for c in cargos_base}
    hist_vizinho = {c: {} for c in cargos_base}
    hist_exclusivas = {c: {} for c in cargos_base}
    hist_compartilhadas = {c: {} for c in cargos_base}

    with st.spinner(i18n.t("m4_spinner")):
        for cenario in opcoes_cenarios:
            df = mapa_cenarios[cenario]
            if df is None or df.empty:
                continue
                
            df_temp = df.copy()
            if 'Carreira' in df_temp.columns:
                df_temp = df_temp.set_index('Carreira')
            df_temp = df_temp.apply(pd.to_numeric, errors='coerce').fillna(0)
            
            df_limpo = data_processing.remover_atribuicoes_comuns(df_temp)
            adj_matrix = data_processing.gerar_matriz_adjacencia(df_temp)
            nodes, edges, pos = data_processing.gerar_dados_grafo(adj_matrix, threshold=1)
            gower_df = data_processing.calcular_distancias(df_temp, metric='gower')
            
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
                        hist_vizinho[c_base][cenario] = i18n.t("m4_isolated")
                else:
                    hist_volume[c_base][cenario] = None
                    hist_exclusivas[c_base][cenario] = None
                    hist_compartilhadas[c_base][cenario] = None
                    hist_adj[c_base][cenario] = None
                    hist_grafo[c_base][cenario] = None
                    hist_gower[c_base][cenario] = None
                    hist_vizinho[c_base][cenario] = i18n.t("m4_extinct")

    st.markdown("---")
    
    def format_html_delta(val, control, is_float=False):
        if val is None or pd.isna(val) or val == i18n.t("m4_extinct") or val == i18n.t("m4_isolated"):
            return str(val) if val is not None else i18n.t("m4_extinct")
            
        if control is None or pd.isna(control) or control == i18n.t("m4_extinct") or control == i18n.t("m4_isolated"):
            if is_float:
                return f"{val:.3f} <span class='jump-arrow'>{i18n.t('m4_new')}</span>"
            return f"{val} <span class='jump-arrow'>{i18n.t('m4_new')}</span>"
            
        if isinstance(val, (int, float)) and isinstance(control, (int, float)):
            diff = val - control
            if abs(diff) < 0.0001:
                seta = "<span class='flat-arrow'>➡ 0</span>"
            elif diff > 0:
                seta = f"<span class='up-arrow'>⬆ +{diff:.3f}</span>" if is_float else f"<span class='up-arrow'>⬆ +{int(diff)}</span>"
            else:
                seta = f"<span class='down-arrow'>⬇ {diff:.3f}</span>" if is_float else f"<span class='down-arrow'>⬇ {int(diff)}</span>"
                
            if is_float:
                return f"{val:.3f} ({seta})"
            return f"{int(val)} ({seta})"
            
        # Para strings (Vizinhos Filogenéticos)
        if val == control:
            return f"{val} <span class='flat-arrow'>(➡)</span>"
        else:
            return f"{val} <span class='jump-arrow'>{i18n.t('m4_jumped')}</span>"

    def render_html_table(hist_dict, is_float=False):
        header_origem = i18n.t("m4_header_origin")
        header_controle = i18n.t("m4_header_control")
        html = "<table class='html-table'><thead><tr>"
        html += f"<th>{header_origem}</th><th>{header_controle}</th>"
        
        cenarios_secundarios = [c for c in opcoes_cenarios if c != "Atual Sem Correção"]
        for cen in cenarios_secundarios:
            html += f"<th>{i18n.t(cen) if i18n.t(cen) != cen else cen}</th>"
        html += "</tr></thead><tbody>"
        
        for c in filtro_cargos:
            bg_color = "rgba(76, 175, 80, 0.15)" if c in cargos_destaque else "transparent"
            opacity = "1.0" if not cargos_destaque or c in cargos_destaque else "0.4"
            
            html += f"<tr style='background-color: {bg_color}; opacity: {opacity}; transition: opacity 0.3s;'>"
            cor_linha = mapa_cores.get(c, '#fff')
            c_label = i18n.dic_traducao_cargos.get(c, c) if lang == 'EN' and traduzir else c
            html += f"<td><span style='color: {cor_linha}; font-weight:bold;'>{c_label}</span></td>"
            
            control_val = hist_dict[c].get("Atual Sem Correção", None)
            
            if is_float and isinstance(control_val, float):
                control_str = f"{control_val:.3f}"
            else:
                control_str = str(control_val) if control_val is not None else i18n.t("m4_extinct")
            
            html += f"<td>{control_str}</td>"
            
            for cen in cenarios_secundarios:
                val = hist_dict[c].get(cen, None)
                cell_html = format_html_delta(val, control_val, is_float)
                html += f"<td>{cell_html}</td>"
            
            html += "</tr>"
            
        html += "</tbody></table>"
        st.markdown(html, unsafe_allow_html=True)
        
    def render_dashboard_aba(titulo, descricao, hist_dict, explanation_key=None, is_float=False, is_string=False, help_text=None, anchor_id=None):
        if anchor_id:
            st.markdown(f"<div id='{anchor_id}'></div>", unsafe_allow_html=True)
            
        if help_text:
            st.subheader(titulo, help=help_text)
        else:
            st.subheader(titulo)
            
        interaction_ui.render_like_button(titulo, f"4_{hashlib.md5(titulo.encode()).hexdigest()[:4]}")
        
        is_sample_biased = len(filtro_cargos) < len(cargos_base)
        if is_sample_biased:
            st.warning(explanations.get_short_bias_warning(language=lang), icon="🚨")
            
        st.caption(descricao)
        
        # Renderizar gráfico de linha (exceto se for texto)
        if not is_string:
            dados_linhas = []
            for c in filtro_cargos:
                for cen in opcoes_cenarios:
                    val = hist_dict[c].get(cen)
                    if val is not None and val != i18n.t("m4_extinct") and val != i18n.t("m4_isolated"):
                        try:
                            val_float = float(val)
                            cen_trans = i18n.t(cen) if i18n.t(cen) != cen else cen
                            col_val_str = "Value" if lang == 'EN' and traduzir else "Valor"
                            dados_linhas.append({i18n.t("col_roles"): c, i18n.t("m3_col_scenario"): cen_trans, col_val_str: val_float})
                        except:
                            pass
            
            if dados_linhas:
                df_linhas = pd.DataFrame(dados_linhas)
                mapa_cores_plot = mapa_cores.copy()
                
                if lang == 'EN' and traduzir:
                    df_linhas[i18n.t("col_roles")] = df_linhas[i18n.t("col_roles")].map(lambda x: i18n.dic_traducao_cargos.get(x, x))
                    # Update color map keys for plotting
                    mapa_cores_plot = {i18n.dic_traducao_cargos.get(k, k): v for k, v in mapa_cores.items()}
                
                fig_line = px.line(df_linhas, x=i18n.t("m3_col_scenario"), y=col_val_str, color=i18n.t("col_roles"), markers=True, color_discrete_map=mapa_cores_plot)
                
                if cargos_destaque:
                    cargos_destaque_trans = [i18n.dic_traducao_cargos.get(c, c) for c in cargos_destaque] if lang == 'EN' and traduzir else cargos_destaque
                    for trace in fig_line.data:
                        if trace.name not in cargos_destaque_trans:
                            trace.line.color = 'rgba(150, 150, 150, 0.2)'
                            trace.marker.color = 'rgba(150, 150, 150, 0.2)'
                        else:
                            trace.line.width = 4
                            trace.marker.size = 10
                            
                fig_line.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='white'), margin=dict(l=0, r=0, t=10, b=0))
                st.plotly_chart(fig_line, use_container_width=True)
                
        # Renderizar Tabela
        render_html_table(hist_dict, is_float)
        
        if explanation_key and st.session_state.get('show_explanations', False):
            st.info(explanations.get_explanation(explanation_key, tone=st.session_state.get('explanation_tone', 'tecnico'), language=lang))

    if current_section is None or current_section == "m4_sub_volume_title":
        render_dashboard_aba(i18n.t("m4_sub_volume_title"), i18n.t("m4_sub_volume_desc"), hist_volume, "m4_micro_41", help_text=i18n.t("m4_sub_volume_help"), anchor_id="toc-volume")
        
    if current_section is None or current_section == "m4_sub_exclusive_title":
        render_dashboard_aba(i18n.t("m4_sub_exclusive_title"), i18n.t("m4_sub_exclusive_desc"), hist_exclusivas, "m4_micro_42", help_text=i18n.t("m4_sub_exclusive_help"), anchor_id="toc-exclusive")
        
    if current_section is None or current_section == "m4_sub_shared_title":
        render_dashboard_aba(i18n.t("m4_sub_shared_title"), i18n.t("m4_sub_shared_desc"), hist_compartilhadas, "m4_micro_43", help_text=i18n.t("m4_sub_shared_help"), anchor_id="toc-shared")
        
    if current_section is None or current_section == "m4_sub_adj_title":
        render_dashboard_aba(i18n.t("m4_sub_adj_title"), i18n.t("m4_sub_adj_desc"), hist_adj, "m4_micro_44", help_text=i18n.t("m4_sub_adj_help"), anchor_id="toc-adj")
        
    if current_section is None or current_section == "m4_sub_gower_title":
        render_dashboard_aba(i18n.t("m4_sub_gower_title"), i18n.t("m4_sub_gower_desc"), hist_gower, "m4_micro_45", is_float=True, help_text=i18n.t("m4_sub_gower_help"), anchor_id="toc-gower")
        
    if current_section is None or current_section == "m4_sub_neighbor_title":
        render_dashboard_aba(i18n.t("m4_sub_neighbor_title"), i18n.t("m4_sub_neighbor_desc"), hist_vizinho, "m4_micro_46", is_string=True, help_text=i18n.t("m4_sub_neighbor_help"), anchor_id="toc-neighbor")

    st.markdown("<div style='height: 150px;'></div>", unsafe_allow_html=True)
