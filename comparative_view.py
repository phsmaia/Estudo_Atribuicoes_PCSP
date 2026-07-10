import streamlit as st
import pandas as pd
import json
import plotly.express as px
import plotly.graph_objects as go
from data_processing import calcular_distancias_gower
import explanations
import i18n

def render_comparativo_axb(opcoes_cenarios, mapa_cenarios, cenario_a, cenario_b, cargo_foco_a, cargos_destaque=None):
    if cenario_a == cenario_b:
        st.warning(i18n.t("warning_diff_scenarios"))
        return

    lang = st.session_state.get('language', 'PT-BR')
    traduzir = lang == 'EN'

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

    gower_a = calcular_distancias_gower(df_a)
    gower_b = calcular_distancias_gower(df_b)

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

    st.markdown("---")
    st.subheader(
        i18n.t("sub_delta_title").format(cenario_a=i18n.t(cenario_a), cenario_b=i18n.t(cenario_b)),
        help=i18n.t("sub_delta_help")
    )
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
    
    # Invert y axis so the diagonal goes from top-left to bottom-right
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        margin=dict(l=0, r=0, t=30, b=0),
        xaxis=dict(tickangle=-45),
        yaxis=dict(autorange="reversed"),
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
    
    st.markdown("---")
    
    st.subheader(
        i18n.t("sub_flow_title"),
        help=i18n.t("sub_flow_help")
    )
    
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
    
    st.subheader(
        i18n.t("sub_radar_title"),
        help=i18n.t("sub_radar_help")
    )
    
    if not cargo_foco_a:
        st.info(i18n.t("radar_no_career_warning"))
    elif cargo_foco_a in df_a['Carreira'].values and cargo_foco_b in df_b['Carreira'].values:
        # Pega TODAS as carreiras do cenário (exceto ela mesma)
        todas_carreiras = [c for c in gower_a.index if c != cargo_foco_a]
            
        fig_radar = go.Figure()
        
        def calc_jaccard(df, c1, c2):
            if c1 not in df['Carreira'].values or c2 not in df['Carreira'].values: return 0.0
            r1 = pd.to_numeric(df[df['Carreira'] == c1].iloc[0].drop('Carreira'), errors='coerce').fillna(0)
            r2 = pd.to_numeric(df[df['Carreira'] == c2].iloc[0].drop('Carreira'), errors='coerce').fillna(0)
            intersection = ((r1 == 1) & (r2 == 1)).sum()
            union = ((r1 == 1) | (r2 == 1)).sum()
            return intersection / union if union > 0 else 0.0
            
        # Afinidade calculada por Jaccard (Somente compartilhamentos positivos importam)
        vals_a = [calc_jaccard(df_a, cargo_foco_a, c) for c in todas_carreiras]
        
        vals_b = []
        for c in todas_carreiras:
            cb = mapping_a_to_b.get(c)
            vals_b.append(calc_jaccard(df_b, cargo_foco_b, cb))
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
    
    st.subheader(
        i18n.t("sub_network_comp_title"),
        help=i18n.t("sub_network_comp_help")
    )
    
    threshold_adj_comp = st.slider(i18n.t("network_comp_slider"), min_value=1, max_value=20, value=1, step=1, key="slider_grafo_comp")
    
    import data_processing
    import visualizations
    
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

    st.subheader(
        i18n.t("sub_tree_comp_title"),
        help=i18n.t("sub_tree_comp_help")
    )
    
    # O Dendrograma precisa do gower_a e gower_b (já calculados anteriormente)
    # Apenas se houver mais de um cargo para poder clusterizar
    if len(gower_a.columns) > 1 and len(gower_b.columns) > 1:
        if lang == 'EN' and traduzir:
            gower_a_disp = gower_a.rename(index=i18n.dic_traducao_cargos, columns=i18n.dic_traducao_cargos)
            gower_b_disp = gower_b.rename(index=i18n.dic_traducao_cargos, columns=i18n.dic_traducao_cargos)
            destaques_a_disp = [i18n.dic_traducao_cargos.get(c, c) for c in destaques_completos if c in gower_a.columns] or None
            destaques_b_disp = [i18n.dic_traducao_cargos.get(c, c) for c in destaques_b if c in gower_b.columns] or None
        else:
            gower_a_disp = gower_a
            gower_b_disp = gower_b
            destaques_a_disp = [c for c in destaques_completos if c in gower_a.columns] or None
            destaques_b_disp = [c for c in destaques_b if c in gower_b.columns] or None
            
        fig_dendro_a = visualizations.plot_dendrogram(gower_a_disp, f"{i18n.t('tree_graph_base')} ({cenario_a})", cargos_destaque=destaques_a_disp)
        fig_dendro_b = visualizations.plot_dendrogram(gower_b_disp, f"{i18n.t('tree_graph_target')} ({cenario_b})", cargos_destaque=destaques_b_disp)
        
        col_dendro1, col_dendro2 = st.columns(2)
        with col_dendro1:
            st.plotly_chart(fig_dendro_a, use_container_width=True)
        with col_dendro2:
            st.plotly_chart(fig_dendro_b, use_container_width=True)
            
        st.markdown(i18n.t("tree_details_title"))
        st.caption(i18n.t("tree_details_caption"))
        
        tabela_dendro = []
        for c in gower_a.columns:
            # Encontrar o vizinho mais próximo no cenário A
            dist_a = gower_a[c].drop(c)
            vizinho_a = dist_a.idxmin()
            val_a = dist_a.min()
            
            # Encontrar o correspondente de 'c' no cenário B
            cb = mapping_a_to_b.get(c, c)
            if cb in gower_b.columns:
                dist_b = gower_b[cb].drop(cb)
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

    st.markdown("<div style='height: 150px;'></div>", unsafe_allow_html=True)
