import streamlit as st
import pandas as pd
import plotly.express as px
import data_processing
import numpy as np
import json
import os
import explanations
import i18n

def render_longitudinal_mode(opcoes_cenarios, mapa_cenarios, filtro_cargos, cargos_destaque):
    lang = st.session_state.get('language', 'PT-BR')
    traduzir = st.session_state.get('traduzir_cargos', False)
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
    
    st.markdown("### 🧬 Rastreamento Longitudinal por Carreira")
    st.markdown("Acompanhe a mutação estrutural de cada cargo ao longo dos cenários. O cenário **Atual Sem Correção** atua como base de **Controle**, e os demais apresentam sua variação colorida indicando crescimento, queda ou salto filogenético.")
    if st.session_state.get('show_explanations', False):
        st.info(explanations.get_explanation("m4_micro_inicio", st.session_state.get('explanation_tone', 'tecnico')))
    
    # Load Dict
    mapa_dict = {}
    try:
        if os.path.exists('csv_dump.json'):
            with open('csv_dump.json', 'r', encoding='utf-8') as f:
                lista_mapa = json.load(f)
                for row in lista_mapa:
                    mapa_dict[row['Atual Sem Correção']] = row
    except Exception as e:
        st.error(f"Erro ao carregar mapa de conversão global: {e}")
        pass
        
    cargos_base = list(mapa_dict.keys()) if mapa_dict else []
    if not cargos_base or not filtro_cargos:
        st.warning("Nenhuma carreira selecionada para visualização.")
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

    with st.spinner("Compilando Rastreamento Longitudinal dos Cenários..."):
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
            gower_df = data_processing.calcular_distancias_gower(df_temp)
            
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

    st.markdown("---")
    
    def format_html_delta(val, control, is_float=False):
        if val is None or pd.isna(val) or val == "Extinto" or val == "Isolado":
            return str(val) if val is not None else "Extinto"
            
        if control is None or pd.isna(control) or control == "Extinto" or control == "Isolado":
            if is_float:
                return f"{val:.3f} <span class='jump-arrow'>(Novo)</span>"
            return f"{val} <span class='jump-arrow'>(Novo)</span>"
            
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
            return f"{val} <span class='jump-arrow'>(🔀 Saltou)</span>"

    def render_html_table(hist_dict, is_float=False):
        header_origem = "Carreira Origem" if lang == 'PT-BR' else "Origin Role"
        header_controle = "Atual Sem Correção (Controle)" if lang == 'PT-BR' else "Current Uncorrected (Control)"
        html = "<table class='html-table'><thead><tr>"
        html += f"<th>{header_origem}</th><th>{header_controle}</th>"
        
        cenarios_secundarios = [c for c in opcoes_cenarios if c != "Atual Sem Correção"]
        for cen in cenarios_secundarios:
            html += f"<th>{cen}</th>"
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
                control_str = str(control_val) if control_val is not None else "Extinto"
            
            html += f"<td>{control_str}</td>"
            
            for cen in cenarios_secundarios:
                val = hist_dict[c].get(cen, None)
                cell_html = format_html_delta(val, control_val, is_float)
                html += f"<td>{cell_html}</td>"
            
            html += "</tr>"
            
        html += "</tbody></table>"
        st.markdown(html, unsafe_allow_html=True)
        
    def render_dashboard_aba(titulo, descricao, hist_dict, explanation_key=None, is_float=False, is_string=False):
        st.markdown(titulo)
        
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
                    if val is not None and val != "Extinto" and val != "Isolado":
                        try:
                            val_float = float(val)
                            dados_linhas.append({"Carreira": c, "Cenário": cen, "Valor": val_float})
                        except:
                            pass
            
            if dados_linhas:
                df_linhas = pd.DataFrame(dados_linhas)
                mapa_cores_plot = mapa_cores.copy()
                
                if lang == 'EN' and traduzir:
                    df_linhas['Carreira'] = df_linhas['Carreira'].map(lambda x: i18n.dic_traducao_cargos.get(x, x))
                    # Update color map keys for plotting
                    mapa_cores_plot = {i18n.dic_traducao_cargos.get(k, k): v for k, v in mapa_cores.items()}
                
                fig_line = px.line(df_linhas, x="Cenário", y="Valor", color="Carreira", markers=True, color_discrete_map=mapa_cores_plot)
                
                if cargos_destaque:
                    for trace in fig_line.data:
                        if trace.name not in cargos_destaque:
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
            st.info(explanations.get_explanation(explanation_key, st.session_state.get('explanation_tone', 'tecnico')))

    render_dashboard_aba("### 4.1 Volume Normativo", "Número de atribuições que a carreira possui (ignorando as genéricas).", hist_volume, "m4_micro_41")
        
    render_dashboard_aba("### 4.2 Atribuições Exclusivas", "Quantidade de funções que *apenas* essa carreira faz.", hist_exclusivas, "m4_micro_42")
        
    render_dashboard_aba("### 4.3 Atribuições Compartilhadas", "Quantidade de funções que a carreira divide com outros.", hist_compartilhadas, "m4_micro_43")
        
    render_dashboard_aba("### 4.4 Força de Adjacência", "Soma bruta de intersecções inter-carreiras.", hist_adj, "m4_micro_44")
        
    render_dashboard_aba("### 4.5 Média de Distância Gower", "O quão distante matematicamente a carreira está do grupo.", hist_gower, "m4_micro_45", is_float=True)
        
    render_dashboard_aba("### 4.6 Vizinho Filogenético", "A carreira mais similar matematicamente (Primeiro galho da árvore).", hist_vizinho, "m4_micro_46", is_string=True)

    st.markdown("<div style='height: 150px;'></div>", unsafe_allow_html=True)
