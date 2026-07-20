import streamlit as st
import pandas as pd
import json
import plotly.express as px
import plotly.graph_objects as go
from data_processing import calcular_distancias
import explanations
import i18n
import interaction_ui
import visualizations
from floating_toc import render_toc
def render_comparativo_axb(opcoes_cenarios, mapa_cenarios, cenario_a, cenario_b, cargo_foco_a, cargos_destaque=None, current_section=None):
    if cenario_a == cenario_b:
        st.warning(i18n.t("warning_diff_scenarios"))
        return

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
        
        with st.expander("📖 Assignments Translation Table"):
            st.markdown("Below are the available translations for the assignments in the active dataset.")
            df_translations = pd.DataFrame(list(i18n.dic_traducao_atribuicoes.items()), columns=["Portuguese (PT-BR)", "English (US-EN)"])
            st.dataframe(df_translations, use_container_width=True, hide_index=True)

    if cargos_destaque is None: cargos_destaque = []
    destaques_completos = list(set(cargos_destaque))
    if cargo_foco_a and cargo_foco_a not in destaques_completos:
        destaques_completos.append(cargo_foco_a)

    df_a = mapa_cenarios[cenario_a].copy()
    df_b = mapa_cenarios[cenario_b].copy()

    # Higienização de Nomes Longos igual ao app.py
    for df in [df_a, df_b]:
        if 'Carreira' in df.columns:
            df['Carreira'] = df['Carreira'].replace({
                "Investigador de Polícia (+ Agente de Telecomunicações Policial + Agente Policial + Carcereiro Policial)": "Investigador de Polícia (+ Apoio)"
            })
    
    with open('csv_dump.json', 'r', encoding='utf-8') as f:
        mapa_dict = json.load(f)
    
    # mapa_dict is a list of dicts. We want mapping from cenario_a to cenario_b
    mapping_a_to_b = {}
    for row in mapa_dict:
        val_a = row.get(cenario_a)
        val_b = row.get(cenario_b)
        if not val_a or not val_b: continue
        
        if val_a == "Investigador de Polícia (+ Agente de Telecomunicações Policial + Agente Policial + Carcereiro Policial)":
            val_a = "Investigador de Polícia (+ Apoio)"
        if val_b == "Investigador de Polícia (+ Agente de Telecomunicações Policial + Agente Policial + Carcereiro Policial)":
            val_b = "Investigador de Polícia (+ Apoio)"
            
        mapping_a_to_b[val_a] = val_b

    gower_a = calcular_distancias(df_a, metric='jaccard')
    gower_b = calcular_distancias(df_b, metric='jaccard')

    cargos_a = list(mapping_a_to_b.keys())
    cargos_a = list(dict.fromkeys(cargos_a))
    
    # Drop cargos that don't exist in gower_a 
    cargos_a = [c for c in cargos_a if c in gower_a.index]

    delta_matrix = pd.DataFrame(index=cargos_a, columns=cargos_a, dtype=float)
    
    for c1 in cargos_a:
        for c2 in cargos_a:
            g_a = gower_a.loc[c1, c2]
            
            m1, m2 = mapping_a_to_b.get(c1), mapping_a_to_b.get(c2)
            if m1 in gower_b.index and m2 in gower_b.index:
                g_b = gower_b.loc[m1, m2]
            else:
                g_b = None
                
            if g_a is not None and g_b is not None:
                delta_matrix.loc[c1, c2] = g_b - g_a
            else:
                delta_matrix.loc[c1, c2] = 0.0

    cargo_foco_b = mapping_a_to_b.get(cargo_foco_a) if cargo_foco_a else None
    destaques_b = [mapping_a_to_b.get(c, c) for c in destaques_completos]

    PALETTE = [
        'rgba(255, 152, 0, 0.4)',  # Laranja
        'rgba(33, 150, 243, 0.4)', # Azul
        'rgba(233, 30, 99, 0.4)',  # Rosa
        'rgba(76, 175, 80, 0.4)',  # Verde
        'rgba(156, 39, 176, 0.4)', # Roxo
        'rgba(255, 235, 59, 0.4)', # Amarelo
        'rgba(0, 188, 212, 0.4)'   # Ciano
    ]
    TEXT_PALETTE = [
        '#ffb74d', '#64b5f6', '#f06292', '#81c784', '#ba68c8', '#fff176', '#4dd0e1'
    ]
    
    color_map = {}
    text_map = {}
    
    c_idx = 0
    for c in destaques_completos:
        if c not in color_map:
            color_map[c] = PALETTE[c_idx % len(PALETTE)]
            text_map[c] = TEXT_PALETTE[c_idx % len(TEXT_PALETTE)]
            
            cb = mapping_a_to_b.get(c, c)
            color_map[cb] = PALETTE[c_idx % len(PALETTE)]
            text_map[cb] = TEXT_PALETTE[c_idx % len(TEXT_PALETTE)]
            c_idx += 1

    if current_section is None or current_section == "sub_delta_title":
        st.markdown("---")
        st.markdown("<div id='toc-delta'></div>", unsafe_allow_html=True)
        st.subheader(
            i18n.t("sub_delta_title").format(cenario_a=i18n.t(cenario_a), cenario_b=i18n.t(cenario_b)),
            help=i18n.t("sub_delta_help")
        )
        interaction_ui.render_like_button("2.3 Discrepancias", "2_3")
        st.markdown(f"<p style='color:#ccc; font-size:0.9rem;'>{i18n.t('delta_subtitle')}</p>", unsafe_allow_html=True)
        
        # Calcula o limite máximo real para calibrar a escala de cor 
        max_val = delta_matrix.abs().max().max()
        limit = max_val if pd.notna(max_val) and max_val > 0 else 0.1
    
        delta_matrix_vis = delta_matrix.copy()
        if lang == 'EN' and traduzir:
            delta_matrix_vis.index = [i18n.dic_traducao_cargos.get(c, c) for c in delta_matrix_vis.index]
            delta_matrix_vis.columns = [i18n.dic_traducao_cargos.get(c, c) for c in delta_matrix_vis.columns]
    
        fig = px.imshow(
            delta_matrix_vis,
            color_continuous_scale='RdBu_r', 
            zmin=-limit, zmax=limit,
            labels=dict(color="Δ Gower"),
            aspect="auto"
        )
        fig.update_traces(xgap=1, ygap=1)
        
        # Invert y axis so the diagonal goes from top-left to bottom-right
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            margin=dict(l=0, r=0, t=30, b=0),
            xaxis=dict(tickangle=-45, title="Cargos"),
            yaxis=dict(autorange="reversed", title="Cargos"),
            height=700
        )
        # Adiciona Highlight na linha e coluna do cargo selecionado
        for dest in destaques_completos:
            if dest in cargos_a:
                idx = cargos_a.index(dest)
                border_color = text_map.get(dest, "rgba(255,152,0,0.8)")
                # Highlight Row
                fig.add_shape(type="rect",
                    x0=-0.5, y0=idx-0.5, x1=len(cargos_a)-0.5, y1=idx+0.5,
                    line=dict(color=border_color, width=2), fillcolor="rgba(0,0,0,0)"
                )
                # Highlight Col
                fig.add_shape(type="rect",
                    x0=idx-0.5, y0=-0.5, x1=idx+0.5, y1=len(cargos_a)-0.5,
                    line=dict(color=border_color, width=2), fillcolor="rgba(0,0,0,0)"
                )
    
        st.plotly_chart(fig, use_container_width=True)
        if st.session_state.get('show_explanations', False):
            st.info(explanations.get_explanation("m2_delta", st.session_state.get('explanation_tone', 'tecnico'), st.session_state.get('language', 'PT-BR')))
    
    if current_section is None or current_section == "sub_dist_title":
        st.markdown("<div id='toc-dist'></div>", unsafe_allow_html=True)
        st.subheader(
            i18n.t("sub_dist_title", default="Distribuição de Distâncias"),
            help="Mostra como as distâncias estão distribuídas dentro de cada cenário."
        )
        dist_col_a, dist_col_b = st.columns(2)
        with dist_col_a:
            st.markdown(f"**{i18n.t(cenario_a)}**")
            fig_dist_a = visualizations.plot_distance_histogram(gower_a, "")
            st.plotly_chart(fig_dist_a, use_container_width=True)
        with dist_col_b:
            st.markdown(f"**{i18n.t(cenario_b)}**")
            fig_dist_b = visualizations.plot_distance_histogram(gower_b, "")
            st.plotly_chart(fig_dist_b, use_container_width=True)
    
        st.markdown("---")

    if current_section is None or current_section == "sub_flow_title":
        st.markdown("<div id='toc-flow'></div>", unsafe_allow_html=True)
        st.subheader(
            i18n.t("sub_flow_title"),
            help=i18n.t("sub_flow_help")
        )
        interaction_ui.render_like_button("2.1 Comparativo Direito (Base)", "2_1")
        
        # Extração de Atribuições Ganhos/Perdas
        if not cargo_foco_a:
            st.info(i18n.t("flow_no_career_warning"))
        elif cargo_foco_a in df_a['Carreira'].values and cargo_foco_b in df_b['Carreira'].values:
            row_a = df_a[df_a['Carreira'] == cargo_foco_a].iloc[0].drop('Carreira')
            row_b = df_b[df_b['Carreira'] == cargo_foco_b].iloc[0].drop('Carreira')
            
            # Converter para numérico 0/1 para garantir comparação segura
            row_a = pd.to_numeric(row_a, errors='coerce').fillna(0)
            row_b = pd.to_numeric(row_b, errors='coerce').fillna(0)
            
            # Alinhar os eixos para o caso de haver atribuições diferentes catalogadas (embora devam ser 399/400)
            all_attrs = list(set(row_a.index) | set(row_b.index))
            
            comparativo_attrs = []
            for attr in all_attrs:
                val_a = row_a.get(attr, 0)
                val_b = row_b.get(attr, 0)
                
                if val_a == 1 and val_b == 0:
                    comparativo_attrs.append({i18n.t("hover_assignment"): attr, "Status": i18n.t("status_lost"), i18n.t(cenario_a): i18n.t("lbl_yes"), i18n.t(cenario_b): i18n.t("lbl_no")})
                elif val_a == 0 and val_b == 1:
                    comparativo_attrs.append({i18n.t("hover_assignment"): attr, "Status": i18n.t("status_gained"), i18n.t(cenario_a): i18n.t("lbl_no"), i18n.t(cenario_b): i18n.t("lbl_yes")})
                elif val_a == 1 and val_b == 1:
                    comparativo_attrs.append({i18n.t("hover_assignment"): attr, "Status": i18n.t("status_maintained"), i18n.t(cenario_a): i18n.t("lbl_yes"), i18n.t(cenario_b): i18n.t("lbl_yes")})
                    
            df_comparativo_attrs = pd.DataFrame(comparativo_attrs)
            
            # Tradução opcional
            if lang == 'EN' and traduzir and not df_comparativo_attrs.empty:
                df_comparativo_attrs[i18n.t("hover_assignment")] = df_comparativo_attrs[i18n.t("hover_assignment")].map(lambda x: i18n.dic_traducao_atribuicoes.get(x, x))
            
            # Ordenar (Ganhos primeiro, Perdas depois, Mantidas no final)
            if not df_comparativo_attrs.empty:
                df_comparativo_attrs['SortKey'] = df_comparativo_attrs['Status'].map({i18n.t("status_gained"): 1, i18n.t("status_lost"): 2, i18n.t("status_maintained"): 3})
                df_comparativo_attrs = df_comparativo_attrs.sort_values(by=['SortKey', i18n.t("hover_assignment")]).drop(columns=['SortKey']).reset_index(drop=True)
                
                opcoes_status_22 = ["status_gained", "status_lost", "status_maintained"]
                filtro_status_22 = st.multiselect(
                    i18n.t("flow_filter_label"), 
                    opcoes_status_22, 
                    default=opcoes_status_22, 
                    format_func=lambda x: i18n.t(x),
                    key="filtro_status_22"
                )
                df_mostrar_22 = df_comparativo_attrs[df_comparativo_attrs["Status"].isin([i18n.t(k) for k in filtro_status_22])]
                def highlight_status_22(row):
                    status = row["Status"]
                    if status == i18n.t("status_gained"):
                        return ['background-color: rgba(76, 175, 80, 0.15); color: #81c784;'] * len(row)
                    elif status == i18n.t("status_lost"):
                        return ['background-color: rgba(244, 67, 54, 0.15); color: #e57373;'] * len(row)
                    else:
                        return ['color: #9e9e9e;'] * len(row)
                
                st.dataframe(df_mostrar_22.style.apply(highlight_status_22, axis=1), use_container_width=True, height=(len(df_mostrar_22) + 1) * 35 + 3)
            else:
                st.write(i18n.t("flow_no_attr_warning"))
        else:
            st.warning(i18n.t("flow_career_not_found"))
        if st.session_state.get('show_explanations', False):
            st.info(explanations.get_explanation("m2_fluxo", st.session_state.get('explanation_tone', 'tecnico'), st.session_state.get('language', 'PT-BR')))
    
        st.markdown("---")
    
    if current_section is None or current_section == "sub_radar_title":
        st.markdown("<div id='toc-radar'></div>", unsafe_allow_html=True)
        st.subheader(
            i18n.t("sub_radar_title"),
            help=i18n.t("sub_radar_help")
        )
        interaction_ui.render_like_button("2.2 Similaridade Geral (Radar)", "2_2")
        
        if not cargo_foco_a:
            st.info(i18n.t("radar_no_career_warning"))
        elif cargo_foco_a in df_a['Carreira'].values and cargo_foco_b in df_b['Carreira'].values:
            # Pega TODAS as carreiras do cenário (exceto ela mesma)
            todas_carreiras = [c for c in gower_a.index if c != cargo_foco_a]
                
            fig_radar = go.Figure()
            
            def calc_similarity(df, c1, c2, metric):
                if c1 not in df['Carreira'].values or c2 not in df['Carreira'].values: return 0.0
                r1 = pd.to_numeric(df[df['Carreira'] == c1].iloc[0].drop('Carreira'), errors='coerce').fillna(0)
                r2 = pd.to_numeric(df[df['Carreira'] == c2].iloc[0].drop('Carreira'), errors='coerce').fillna(0)
                
                a = ((r1 == 1) & (r2 == 1)).sum()
                b = ((r1 == 1) & (r2 == 0)).sum()
                c = ((r1 == 0) & (r2 == 1)).sum()
                
                if metric == 'jaccard':
                    return a / (a + b + c) if (a + b + c) > 0 else 0.0
                elif metric == 'sokalsneath':
                    return a / (a + 2*(b + c)) if (a + 2*(b + c)) > 0 else 0.0
                elif metric == 'dice':
                    return 2*a / (2*a + b + c) if (2*a + b + c) > 0 else 0.0
                elif metric == 'overlap':
                    min_ab_ac = min(a + b, a + c)
                    return a / min_ab_ac if min_ab_ac > 0 else 0.0
                elif metric == 'cosine':
                    import math
                    denom = math.sqrt((a + b) * (a + c))
                    return a / denom if denom > 0 else 0.0
                return 0.0
                
            # Afinidade calculada pela métrica selecionada
            # Para isso precisamos do selectbox da métrica
            metric_options = {
                'jaccard': i18n.t("metric_jaccard", default="Jaccard (usado no artigo)"),
                'sokalsneath': i18n.t("metric_sokal", default="Sokal & Sneath"),
                'dice': i18n.t("metric_dice", default="Sørensen-Dice / Gower & Legendre 2"),
                'overlap': i18n.t("metric_overlap", default="Overlap Coefficient"),
                'cosine': i18n.t("metric_cosine", default="Cosine Similarity")
            }
            
            selected_radar_metric = st.selectbox(
                i18n.t("select_radar_metric", default="Métrica de Afinidade no Radar"),
                list(metric_options.keys()),
                format_func=lambda x: metric_options[x],
                key="radar_metric_selectbox"
            )
            
            vals_a = [calc_similarity(df_a, cargo_foco_a, c, selected_radar_metric) for c in todas_carreiras]
            
            vals_b = []
            for c in todas_carreiras:
                cb = mapping_a_to_b.get(c)
                vals_b.append(calc_similarity(df_b, cargo_foco_b, cb, selected_radar_metric))
            todas_carreiras_display = [i18n.traduzir_cargo(c) if traduzir else c for c in todas_carreiras]
                    
            fig_radar.add_trace(go.Scatterpolar(
                r=vals_a + [vals_a[0]], 
                theta=todas_carreiras_display + [todas_carreiras_display[0]],
                fill='toself',
                name=f"{i18n.t(cenario_a)}",
                line_color='cyan',
                hovertemplate=i18n.t("radar_hover")
            ))
            
            fig_radar.add_trace(go.Scatterpolar(
                r=vals_b + [vals_b[0]],
                theta=todas_carreiras_display + [todas_carreiras_display[0]],
                fill='toself',
                name=f"{i18n.t(cenario_b)}",
                line_color='orange',
                hovertemplate=i18n.t("radar_hover")
            ))
            
            for dest in destaques_completos:
                if dest in todas_carreiras:
                    dest_display = i18n.traduzir_cargo(dest) if traduzir else dest
                    fig_radar.add_trace(go.Scatterpolar(
                        r=[1.0],
                        theta=[dest_display],
                        mode='markers+text',
                        marker=dict(color=text_map.get(dest, 'white'), size=12, symbol='star'),
                        text=["⭐"],
                        textposition="top center",
                        name=f"{i18n.t('radar_highlight')}: {dest_display}",
                        showlegend=True,
                        hoverinfo='skip'
                    ))
                    
            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 1]
                    )
                ),
                showlegend=True,
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                height=750,
                margin=dict(l=100, r=100, t=60, b=60)
            )
            
            st.plotly_chart(fig_radar, use_container_width=True)
            
            # TABELA DE DIVERGÊNCIA
            st.markdown(i18n.t("sub_affinity_title"), help=i18n.t("sub_affinity_help"))
            
            tabela_dados = []
            for i, c in enumerate(todas_carreiras):
                sim_a = vals_a[i]
                sim_b = vals_b[i]
                delta = sim_b - sim_a
                
                # Seta indicativa
                if delta > 0.01:
                    seta = i18n.t("trend_approached")
                elif delta < -0.01:
                    seta = i18n.t("trend_distanced")
                else:
                    seta = i18n.t("trend_stable")
                    
                c_display = i18n.traduzir_cargo(c) if traduzir else c
                tabela_dados.append({
                    i18n.t("col_related_career"): c_display,
                    f"{i18n.t('col_base_affinity')} ({i18n.t(cenario_a)})": float(sim_a * 100),
                    f"{i18n.t('col_new_affinity')} ({i18n.t(cenario_b)})": float(sim_b * 100),
                    i18n.t("col_delta_var"): float(delta * 100),
                    i18n.t("col_trend"): seta
                })
                
            df_radar_comp = pd.DataFrame(tabela_dados).sort_values(by=f"{i18n.t('col_base_affinity')} ({i18n.t(cenario_a)})", ascending=False).reset_index(drop=True)
            
            opcoes_status_24 = ["trend_approached", "trend_distanced", "trend_stable"]
            filtro_status_24 = st.multiselect(
                i18n.t("affinity_filter_label"), 
                opcoes_status_24, 
                default=opcoes_status_24, 
                format_func=lambda x: i18n.t(x),
                key="filtro_status_24"
            )
            df_mostrar_24 = df_radar_comp[df_radar_comp[i18n.t("col_trend")].isin([i18n.t(k) for k in filtro_status_24])]
            
            def highlight_24(row):
                c_disp = row[i18n.t("col_related_career")]
                # We map it back to original name for color logic, or color map just doesn't match...
                # The color_map keys are original names.
                # Let's find the original name.
                orig_c = next((k for k in color_map.keys() if i18n.traduzir_cargo(k) == c_disp or k == c_disp), None)
                if orig_c and orig_c in color_map:
                    return [f'background-color: {color_map[orig_c]}; color: {text_map[orig_c]}; font-weight: bold;'] * len(row)
                return [''] * len(row)
                
            st.dataframe(
                df_mostrar_24.style.apply(highlight_24, axis=1),
                use_container_width=True,
                column_config={
                    f"{i18n.t('col_base_affinity')} ({i18n.t(cenario_a)})": st.column_config.NumberColumn(
                        f"{i18n.t('col_base_affinity')} ({i18n.t(cenario_a)})",
                        format="%.1f%%"
                    ),
                    f"{i18n.t('col_new_affinity')} ({i18n.t(cenario_b)})": st.column_config.NumberColumn(
                        f"{i18n.t('col_new_affinity')} ({i18n.t(cenario_b)})",
                        format="%.1f%%"
                    ),
                    i18n.t("col_delta_var"): st.column_config.NumberColumn(
                        i18n.t("col_delta_var"),
                        format="%+.1f%%"
                    )
                },
                height=(len(df_mostrar_24) + 1) * 35 + 3
            )
            if st.session_state.get('show_explanations', False):
                st.info(explanations.get_explanation("m2_radar", st.session_state.get('explanation_tone', 'tecnico'), st.session_state.get('language', 'PT-BR')))
    
        st.markdown("---")
    
    if current_section is None or current_section == "sub_network_comp_title":
        st.markdown("<div id='toc-network'></div>", unsafe_allow_html=True)
        st.subheader(
            i18n.t("sub_network_comp_title"),
            help=i18n.t("sub_network_comp_help")
        )
        
        threshold_adj_comp = st.slider(i18n.t("network_comp_slider"), min_value=1, max_value=20, value=1, step=1, key="slider_grafo_comp")
        
        import data_processing
        
        adj_a = data_processing.gerar_matriz_adjacencia(df_a)
        adj_b = data_processing.gerar_matriz_adjacencia(df_b)
        
        nodes_a, edges_a, pos_a = data_processing.gerar_dados_grafo(adj_a, threshold=threshold_adj_comp)
        nodes_b, edges_b, pos_b = data_processing.gerar_dados_grafo(adj_b, threshold=threshold_adj_comp)
        
        if lang == 'EN' and traduzir:
            for node_list in [nodes_a, nodes_b]:
                for n in node_list: n["id"] = i18n.dic_traducao_cargos.get(n["id"], n["id"])
            for edge_list in [edges_a, edges_b]:
                for e in edge_list:
                    e["source"] = i18n.dic_traducao_cargos.get(e["source"], e["source"])
                    e["target"] = i18n.dic_traducao_cargos.get(e["target"], e["target"])
            # Update cargos destaque lists to English
            cargos_destaque_a = [i18n.dic_traducao_cargos.get(c, c) for c in destaques_completos if c in adj_a.index] or None
            cargos_destaque_b = [i18n.dic_traducao_cargos.get(c, c) for c in destaques_b if c in adj_b.index] or None
        else:
            cargos_destaque_a = [c for c in destaques_completos if c in adj_a.index] or None
            cargos_destaque_b = [c for c in destaques_b if c in adj_b.index] or None
            
        fig_grafo_a = visualizations.plot_network_graph(nodes_a, edges_a, f"{i18n.t('network_graph_base')} ({cenario_a})", cargos_destaque=cargos_destaque_a)
        fig_grafo_b = visualizations.plot_network_graph(nodes_b, edges_b, f"{i18n.t('network_graph_target')} ({cenario_b})", cargos_destaque=cargos_destaque_b)
        
        col_grafo1, col_grafo2 = st.columns(2)
        with col_grafo1:
            st.plotly_chart(fig_grafo_a, use_container_width=True)
        with col_grafo2:
            st.plotly_chart(fig_grafo_b, use_container_width=True)
    
        st.markdown(i18n.t("network_details_title"))
        st.caption(i18n.t("network_details_caption").format(threshold=threshold_adj_comp))
        
        todas_carreiras_grafo = list(set([n["id"] for n in nodes_a] + [n["id"] for n in nodes_b]))
        
        tabela_grafo = []
        for c in todas_carreiras_grafo:
            deg_a = sum(1 for e in edges_a if e["source"] == c or e["target"] == c)
            
            # O nome do cargo no cenário B pode ser diferente, então usamos o mapeamento
            cb = mapping_a_to_b.get(c, c) 
            deg_b = sum(1 for e in edges_b if e["source"] == cb or e["target"] == cb)
            
            diff = deg_b - deg_a
            if diff > 0:
                status = i18n.t("net_more_connected")
            elif diff < 0:
                status = i18n.t("net_less_connected")
            else:
                status = i18n.t("net_stable")
                
            c_display = i18n.traduzir_cargo(c) if traduzir else c
            tabela_grafo.append({
                i18n.t("hover_career"): c_display,
                i18n.t('col_conn_base').format(cenario=i18n.t(cenario_a)): deg_a,
                i18n.t('col_conn_base').format(cenario=i18n.t(cenario_b)): deg_b,
                i18n.t("col_conn_var"): diff,
                i18n.t("col_net_impact"): status
            })
            
        df_grafo = pd.DataFrame(tabela_grafo).sort_values(by=i18n.t("col_conn_var"), ascending=False).reset_index(drop=True)
        
        opcoes_status_25 = ["net_more_connected", "net_less_connected", "net_stable"]
        filtro_status_25 = st.multiselect(
            i18n.t("network_filter_label"), 
            opcoes_status_25, 
            default=opcoes_status_25, 
            format_func=lambda x: i18n.t(x),
            key="filtro_status_25"
        )
        df_mostrar_25 = df_grafo[df_grafo[i18n.t("col_net_impact")].isin([i18n.t(k) for k in filtro_status_25])]
        
        def highlight_25(row):
            c_disp = row[i18n.t("hover_career")]
            orig_c = next((k for k in color_map.keys() if i18n.traduzir_cargo(k) == c_disp or k == c_disp), None)
            if orig_c and orig_c in color_map:
                return [f'background-color: {color_map[orig_c]}; color: {text_map[orig_c]}; font-weight: bold;'] * len(row)
            return [''] * len(row)
            
        st.dataframe(
            df_mostrar_25.style.apply(highlight_25, axis=1),
            use_container_width=True,
            column_config={
                i18n.t("col_conn_var"): st.column_config.NumberColumn(
                    i18n.t("col_conn_var"),
                    format="%+d"
                )
            },
            height=(len(df_mostrar_25) + 1) * 35 + 3
        )
        if st.session_state.get('show_explanations', False):
            st.info(explanations.get_explanation("m2_grafo", st.session_state.get('explanation_tone', 'tecnico'), st.session_state.get('language', 'PT-BR')))
    
        st.markdown("---")

    if current_section is None or current_section == "sub_tree_comp_title":
        st.markdown("<div id='toc-tree'></div>", unsafe_allow_html=True)
        st.subheader(
            i18n.t("sub_tree_comp_title"),
            help=i18n.t("sub_tree_comp_help")
        )
        
        # O Dendrograma precisa do gower_a e gower_b
        # Apenas se houver mais de um cargo para poder clusterizar
        if len(gower_a.columns) > 1 and len(gower_b.columns) > 1:
            st.markdown("### " + i18n.t("config_metrics", default="Configurações de Distância e Agrupamento"))
            col_metric_dendro, col_linkage_dendro = st.columns(2)
            metric_options_dendro = {
                'gower': i18n.t("metric_gower", default="Distância de Gower (usado no artigo - ver Errata)"),
                'jaccard': i18n.t("metric_jaccard", default="Jaccard (Assimétrica)"),
                'sokalsneath': i18n.t("metric_sokal", default="Sokal & Sneath"),
                'dice': i18n.t("metric_dice", default="Sørensen-Dice / Gower & Legendre 2"),
                'overlap': i18n.t("metric_overlap", default="Overlap Coefficient"),
                'cosine': i18n.t("metric_cosine", default="Cosine Similarity")
            }
            with col_metric_dendro:
                selected_metric_dendro = st.selectbox(
                    i18n.t("select_metric", default="Selecione a Métrica de Similaridade"),
                    list(metric_options_dendro.keys()),
                    format_func=lambda x: metric_options_dendro[x],
                    key="dendro_metric_selectbox"
                )
            with col_linkage_dendro:
                linkage_options = {
                    'single': i18n.t("linkage_single", default="Single Linkage (usado no artigo)"),
                    'complete': i18n.t("linkage_complete", default="Complete Linkage"),
                    'average': i18n.t("linkage_average", default="Average Linkage (UPGMA)")
                }
                selected_linkage_dendro = st.selectbox(
                    i18n.t("select_linkage", default="Selecione o Método de Agrupamento (Linkage)"),
                    list(linkage_options.keys()),
                    format_func=lambda x: linkage_options[x],
                    key="dendro_linkage_selectbox"
                )
                
            # Recalcular com a métrica selecionada
            gower_a_dendro = calcular_distancias(df_a, metric=selected_metric_dendro)
            gower_b_dendro = calcular_distancias(df_b, metric=selected_metric_dendro)
            
            if lang == 'EN' and traduzir:
                gower_a_disp = gower_a_dendro.rename(index=i18n.dic_traducao_cargos, columns=i18n.dic_traducao_cargos)
                gower_b_disp = gower_b_dendro.rename(index=i18n.dic_traducao_cargos, columns=i18n.dic_traducao_cargos)
                destaques_a_disp = [i18n.dic_traducao_cargos.get(c, c) for c in destaques_completos if c in gower_a_dendro.columns] or None
                destaques_b_disp = [i18n.dic_traducao_cargos.get(c, c) for c in destaques_b if c in gower_b_dendro.columns] or None
            else:
                gower_a_disp = gower_a_dendro
                gower_b_disp = gower_b_dendro
                destaques_a_disp = [c for c in destaques_completos if c in gower_a_dendro.columns] or None
                destaques_b_disp = [c for c in destaques_b if c in gower_b_dendro.columns] or None
                
            fig_dendro_a = visualizations.plot_dendrogram(gower_a_disp, f"{i18n.t('tree_graph_base')} ({cenario_a})", cargos_destaque=destaques_a_disp, linkage_method=selected_linkage_dendro)
            fig_dendro_b = visualizations.plot_dendrogram(gower_b_disp, f"{i18n.t('tree_graph_target')} ({cenario_b})", cargos_destaque=destaques_b_disp, linkage_method=selected_linkage_dendro)
            
            col_dendro1, col_dendro2 = st.columns(2)
            with col_dendro1:
                st.plotly_chart(fig_dendro_a, use_container_width=True)
            with col_dendro2:
                st.plotly_chart(fig_dendro_b, use_container_width=True)
                
            st.markdown(i18n.t("tree_details_title"))
            st.caption(i18n.t("tree_details_caption"))
            
            tabela_dendro = []
            for c in gower_a_dendro.columns:
                # Encontrar o vizinho mais próximo no cenário A
                dist_a = gower_a_dendro[c].drop(c)
                vizinho_a = dist_a.idxmin()
                val_a = dist_a.min()
                
                # Encontrar o correspondente de 'c' no cenário B
                cb = mapping_a_to_b.get(c, c)
                if cb in gower_b_dendro.columns:
                    dist_b = gower_b_dendro[cb].drop(cb)
                    vizinho_b = dist_b.idxmin()
                    val_b = dist_b.min()
                    
                    # Para saber se mudou de galho, precisamos ver se vizinho_b (no novo nome) 
                    # corresponde ao vizinho_a (no novo nome)
                    viz_a_mapped = mapping_a_to_b.get(vizinho_a, vizinho_a)
                    mudou_galho = i18n.t("branch_jumped") if vizinho_b != viz_a_mapped else i18n.t("branch_maintained")
                    
                    c_display = i18n.traduzir_cargo(c) if traduzir else c
                    vizinho_a_display = i18n.traduzir_cargo(vizinho_a) if traduzir else vizinho_a
                    vizinho_b_display = i18n.traduzir_cargo(vizinho_b) if traduzir else vizinho_b
                    
                    tabela_dendro.append({
                        i18n.t("hover_career"): c_display,
                        f"{i18n.t('col_closest_neighbor')} ({i18n.t(cenario_a)})": vizinho_a_display,
                        f"{i18n.t('col_distance')} ({i18n.t(cenario_a)})": val_a,
                        f"{i18n.t('col_new_neighbor')} ({i18n.t(cenario_b)})": vizinho_b_display,
                        f"{i18n.t('col_distance')} ({i18n.t(cenario_b)})": val_b,
                        i18n.t("col_branch_change"): mudou_galho
                    })
            
            if tabela_dendro:
                df_dendro = pd.DataFrame(tabela_dendro).sort_values(by=f"{i18n.t('col_distance')} ({i18n.t(cenario_a)})").reset_index(drop=True)
                
                opcoes_status_26 = ["branch_jumped", "branch_maintained"]
                filtro_status_26 = st.multiselect(
                    i18n.t("tree_filter_label"), 
                    opcoes_status_26, 
                    default=opcoes_status_26, 
                    format_func=lambda x: i18n.t(x),
                    key="filtro_status_26"
                )
                df_mostrar_26 = df_dendro[df_dendro[i18n.t("col_branch_change")].isin([i18n.t(k) for k in filtro_status_26])]
                
                def highlight_26(row):
                    c_disp = row[i18n.t("hover_career")]
                    orig_c = next((k for k in color_map.keys() if i18n.traduzir_cargo(k) == c_disp or k == c_disp), None)
                    if orig_c and orig_c in color_map:
                        return [f'background-color: {color_map[orig_c]}; color: {text_map[orig_c]}; font-weight: bold;'] * len(row)
                    return [''] * len(row)
                    
                st.dataframe(
                    df_mostrar_26.style.apply(highlight_26, axis=1),
                    use_container_width=True,
                    column_config={
                        f"{i18n.t('col_distance')} ({i18n.t(cenario_a)})": st.column_config.NumberColumn(
                            f"{i18n.t('col_distance')} ({i18n.t(cenario_a)})",
                            format="%.3f"
                        ),
                        f"{i18n.t('col_distance')} ({i18n.t(cenario_b)})": st.column_config.NumberColumn(
                            f"{i18n.t('col_distance')} ({i18n.t(cenario_b)})",
                            format="%.3f"
                        )
                    },
                    height=(len(df_mostrar_26) + 1) * 35 + 3
                )
                
        else:
            st.warning(i18n.t("tree_warning"))
        if st.session_state.get('show_explanations', False):
            st.info(explanations.get_explanation("m2_dendro", st.session_state.get('explanation_tone', 'tecnico'), st.session_state.get('language', 'PT-BR')))
    
        st.markdown("💡 **Dica:** Compare os índices cofenéticos abaixo para verificar se a reestruturação melhorou a fidelidade dos agrupamentos hierárquicos.")
        with st.expander("📖 ABRIR COMPARAÇÕES E ÍNDICES COFENÉTICOS (CENÁRIO A vs CENÁRIO B)"):
            st.markdown("#### Índices Cofenéticos")
            st.markdown("<span style='color:#00cc00; font-weight:bold;'>Verde (≥0.90)</span> | <span style='color:#ffcc00; font-weight:bold;'>Amarelo (≥0.75)</span> | <span style='color:#ff9900; font-weight:bold;'>Laranja (≥0.50)</span> | <span style='color:#ff3333; font-weight:bold;'>Vermelho (<0.50)</span>", unsafe_allow_html=True)
            
            from data_processing import get_cophenetic_comparison_table
            df_coph_a = get_cophenetic_comparison_table(df_a)
            df_coph_b = get_cophenetic_comparison_table(df_b)
            
            def color_coph(val):
                if isinstance(val, str) and " (" in val:
                    try:
                        val = float(val.split(" ")[0])
                    except ValueError:
                        pass
                if isinstance(val, (int, float)):
                    if val >= 0.90:
                        f = (val - 0.90) / 0.10
                        f = max(0, min(1, f))
                        r = int(150 + f * (0 - 150))
                        g = int(255 + f * (200 - 255))
                        b = int(150 + f * (0 - 150))
                    elif val >= 0.75:
                        f = (val - 0.75) / 0.15
                        f = max(0, min(1, f))
                        r = int(255 + f * (150 - 255))
                        g = int(220 + f * (255 - 220))
                        b = int(0 + f * (150 - 0))
                    elif val >= 0.50:
                        f = (val - 0.50) / 0.25
                        f = max(0, min(1, f))
                        r = int(255 + f * (255 - 255))
                        g = int(150 + f * (220 - 150))
                        b = int(0 + f * (0 - 0))
                    else:
                        f = val / 0.50
                        f = max(0, min(1, f))
                        r = int(255 + f * (255 - 255))
                        g = int(50 + f * (150 - 50))
                        b = int(50 + f * (0 - 50))
                    return f'background-color: rgb({r},{g},{b}); color: black;'
                return ''
                
            coph_col_a, coph_col_b = st.columns(2)
            with coph_col_a:
                st.markdown(f"**{i18n.t(cenario_a)}**")
                st.dataframe(df_coph_a.style.map(color_coph), use_container_width=True)
            with coph_col_b:
                st.markdown(f"**{i18n.t(cenario_b)}**")
                st.dataframe(df_coph_b.style.map(color_coph), use_container_width=True)
    
        st.markdown("<div style='height: 150px;'></div>", unsafe_allow_html=True)
    
