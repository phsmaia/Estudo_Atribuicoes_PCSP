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
        st.warning(i18n.t("dendro_warning") if i18n.t("dendro_warning") != "dendro_warning" else "Selecione cenários diferentes no Painel Superior para comparar.")
        return

    lang = st.session_state.get('language', 'PT-BR')
    traduzir = st.session_state.get('traduzir_cargos', False)

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
        f"2.1. Delta de Similaridade de Gower ({cenario_a} → {cenario_b})",
        help="**O que é isso?**\nEste mapa de calor matemático calcula a diferença vetorial exata entre os dois cenários.\n\n**Como ler:**\n- **Azul (Negativo)**: A distância entre os cargos diminuiu. Eles se tornaram mais parecidos (Aglutinação de funções).\n- **Vermelho (Positivo)**: A distância aumentou. Eles se afastaram e tornaram-se mais exclusivos/distintos.\n- **Branco (Zero)**: Não houve alteração na relação matemática entre os cargos."
    )
    st.markdown("<p style='color:#ccc; font-size:0.9rem;'>Valores negativos (Azul) indicam aproximação (ficaram mais similares). Valores positivos (Vermelho) indicam distanciamento.</p>", unsafe_allow_html=True)
    
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
        st.info(explanations.get_explanation("m2_delta", st.session_state.get('explanation_tone', 'tecnico')))
    
    st.markdown("---")
    
    st.subheader(
        "2.2. Fluxo Normativo (Ganhos e Perdas)",
        help="**O que é isso?**\nExibe explicitamente quais atribuições foram adicionadas (ganho), removidas (perda) ou mantidas para a carreira selecionada na transição entre os cenários."
    )
    
    # Extração de Atribuições Ganhos/Perdas
    if not cargo_foco_a:
        st.info("💡 Selecione uma 'Carreira para Análise Detalhada' no topo para visualizar o Fluxo Normativo (Ganhos e Perdas).")
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
                comparativo_attrs.append({"Atribuição": attr, "Status": "🔴 Perdeu", cenario_a: "Sim", cenario_b: "Não"})
            elif val_a == 0 and val_b == 1:
                comparativo_attrs.append({"Atribuição": attr, "Status": "🟢 Ganhou", cenario_a: "Não", cenario_b: "Sim"})
            elif val_a == 1 and val_b == 1:
                comparativo_attrs.append({"Atribuição": attr, "Status": "⚪ Manteve", cenario_a: "Sim", cenario_b: "Sim"})
                
        df_comparativo_attrs = pd.DataFrame(comparativo_attrs)
        
        # Tradução opcional
        if lang == 'EN' and traduzir and not df_comparativo_attrs.empty:
            df_comparativo_attrs['Atribuição'] = df_comparativo_attrs['Atribuição'].map(lambda x: i18n.dic_traducao_atribuicoes.get(x, x))
        
        # Ordenar (Ganhos primeiro, Perdas depois, Mantidas no final)
        if not df_comparativo_attrs.empty:
            df_comparativo_attrs['SortKey'] = df_comparativo_attrs['Status'].map({"🟢 Ganhou": 1, "🔴 Perdeu": 2, "⚪ Manteve": 3})
            df_comparativo_attrs = df_comparativo_attrs.sort_values(by=['SortKey', 'Atribuição']).drop(columns=['SortKey']).reset_index(drop=True)
            
            opcoes_status_22 = ["🟢 Ganhou", "🔴 Perdeu", "⚪ Manteve"]
            filtro_status_22 = st.multiselect("Filtrar Status da Atribuição:", opcoes_status_22, default=opcoes_status_22, key="filtro_status_22")
            df_mostrar_22 = df_comparativo_attrs[df_comparativo_attrs["Status"].isin(filtro_status_22)]
            def highlight_status_22(row):
                status = row["Status"]
                if "Ganhou" in status:
                    return ['background-color: rgba(76, 175, 80, 0.15); color: #81c784;'] * len(row)
                elif "Perdeu" in status:
                    return ['background-color: rgba(244, 67, 54, 0.15); color: #e57373;'] * len(row)
                else:
                    return ['color: #9e9e9e;'] * len(row)
            
            st.dataframe(df_mostrar_22.style.apply(highlight_status_22, axis=1), use_container_width=True, height=(len(df_mostrar_22) + 1) * 35 + 3)
        else:
            st.write("Nenhuma atribuição encontrada para esta carreira.")
    else:
        st.warning("Carreira não localizada nos dados para comparação direta de atribuições.")
    if st.session_state.get('show_explanations', False):
        st.info(explanations.get_explanation("m2_fluxo", st.session_state.get('explanation_tone', 'tecnico')))

    st.markdown("---")
    st.subheader(
        "2.3. Régua Evolutiva por Cargo (Radar de Afinidade)",
        help="**O que é isso?**\nUm gráfico bidimensional que sobrepõe a similaridade do cargo selecionado contra as outras carreiras da polícia nos dois cenários.\n\n**Como ler:**\n- Quanto mais a ponta do radar se esticar para a borda externa, mais as carreiras são **similares**.\n- Se a área laranja (Cenário Alvo) for maior que a ciano (Cenário Base), o cargo selecionado *absorveu* funções e se aproximou das demais carreiras.\n- Se a área encolher, o cargo sofreu um expurgo normativo e isolou-se."
    )
    
    if not cargo_foco_a:
        st.info("💡 Selecione uma 'Carreira para Análise Detalhada' no topo para visualizar o Radar de Afinidade e o Detalhamento Analítico.")
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
                
        fig_radar.add_trace(go.Scatterpolar(
            r=vals_a + [vals_a[0]], 
            theta=todas_carreiras + [todas_carreiras[0]],
            fill='toself',
            name=f"{cenario_a}",
            line_color='cyan',
            hovertemplate="<b>Carreira:</b> %{theta}<br><b>Afinidade Jaccard:</b> %{r:.1%}<extra></extra>"
        ))
        
        fig_radar.add_trace(go.Scatterpolar(
            r=vals_b + [vals_b[0]],
            theta=todas_carreiras + [todas_carreiras[0]],
            fill='toself',
            name=f"{cenario_b}",
            line_color='orange',
            hovertemplate="<b>Carreira:</b> %{theta}<br><b>Afinidade Jaccard:</b> %{r:.1%}<extra></extra>"
        ))
        
        for dest in destaques_completos:
            if dest in todas_carreiras:
                fig_radar.add_trace(go.Scatterpolar(
                    r=[1.0],
                    theta=[dest],
                    mode='markers+text',
                    marker=dict(color=text_map.get(dest, 'white'), size=12, symbol='star'),
                    text=["⭐"],
                    textposition="top center",
                    name=f"Destaque: {dest}",
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
        st.markdown("#### 2.4. Detalhamento Analítico de Afinidade", help="**Como a afinidade é calculada?**\nA Afinidade é calculada matematicamente pelo **Índice de Similaridade de Jaccard**. Ela leva em conta estritamente o que é *COMPARTILHADO E PRESENTE* entre os cargos. Atribuições que **nenhum dos dois** exerce não entram na conta e não aproximam artificialmente os cargos, corrigindo falhas analíticas de matrizes simples. Se Afinidade for `100%`, eles exercem exatamente as mesmas funções em comum.")
        
        tabela_dados = []
        for i, c in enumerate(todas_carreiras):
            sim_a = vals_a[i]
            sim_b = vals_b[i]
            delta = sim_b - sim_a
            
            # Seta indicativa
            if delta > 0.01:
                seta = "🟢 ↗ Aproximou"
            elif delta < -0.01:
                seta = "🔴 ↘ Afastou"
            else:
                seta = "⚪ ➡ Estável"
                
            tabela_dados.append({
                "Carreira Relacionada": c,
                f"Afinidade Base ({cenario_a})": float(sim_a * 100),
                f"Nova Afinidade ({cenario_b})": float(sim_b * 100),
                "Δ Variação": float(delta * 100),
                "Tendência": seta
            })
            
        df_tabela = pd.DataFrame(tabela_dados).sort_values(by=f"Afinidade Base ({cenario_a})", ascending=False).reset_index(drop=True)
        
        opcoes_status_24 = ["🟢 ↗ Aproximou", "🔴 ↘ Afastou", "⚪ ➡ Estável"]
        filtro_status_24 = st.multiselect("Filtrar Tendência de Afinidade:", opcoes_status_24, default=opcoes_status_24, key="filtro_status_24")
        df_mostrar_24 = df_tabela[df_tabela["Tendência"].isin(filtro_status_24)]
        
        def highlight_24(row):
            c = row["Carreira Relacionada"]
            if c in color_map:
                return [f'background-color: {color_map[c]}; color: {text_map[c]}; font-weight: bold;'] * len(row)
            return [''] * len(row)
            
        st.dataframe(
            df_mostrar_24.style.apply(highlight_24, axis=1),
            use_container_width=True,
            column_config={
                f"Afinidade Base ({cenario_a})": st.column_config.NumberColumn(
                    f"Afinidade Base ({cenario_a})",
                    format="%.1f%%"
                ),
                f"Nova Afinidade ({cenario_b})": st.column_config.NumberColumn(
                    f"Nova Afinidade ({cenario_b})",
                    format="%.1f%%"
                ),
                "Δ Variação": st.column_config.NumberColumn(
                    "Δ Variação",
                    format="%+.1f%%"
                )
            },
            height=(len(df_mostrar_24) + 1) * 35 + 3
        )
        if st.session_state.get('show_explanations', False):
            st.info(explanations.get_explanation("m2_radar", st.session_state.get('explanation_tone', 'tecnico')))

    st.markdown("---")
    
    st.subheader(
        "2.5. Rede de Adjacência Comparativa (Grafo de Similaridade)",
        help="**O que é isso?**\nExibe as 'teias de aranha' de conexões lado a lado. Se o cenário alvo fragmentou as atribuições, você verá o grafo B mais desconectado ou as linhas mais finas. Se aglutinou, o grafo ficará mais denso e as carreiras mais puxadas para o centro."
    )
    
    threshold_adj_comp = st.slider("Corte de Adjacência Comparativa (Threshold):", min_value=1, max_value=20, value=1, step=1, key="slider_grafo_comp")
    
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
        
    fig_grafo_a = visualizations.plot_network_graph(nodes_a, edges_a, f"Grafo Cenário Base ({cenario_a})", cargos_destaque=cargos_destaque_a)
    fig_grafo_b = visualizations.plot_network_graph(nodes_b, edges_b, f"Grafo Cenário Alvo ({cenario_b})", cargos_destaque=cargos_destaque_b)
    
    col_grafo1, col_grafo2 = st.columns(2)
    with col_grafo1:
        st.plotly_chart(fig_grafo_a, use_container_width=True)
    with col_grafo2:
        st.plotly_chart(fig_grafo_b, use_container_width=True)

    st.markdown("#### Detalhamento Estrutural da Rede")
    st.caption(f"A tabela abaixo contabiliza quantas conexões fortes (acima do corte de {threshold_adj_comp} atribuições em comum) cada carreira formou na teia.")
    
    todas_carreiras_grafo = list(set([n["id"] for n in nodes_a] + [n["id"] for n in nodes_b]))
    
    tabela_grafo = []
    for c in todas_carreiras_grafo:
        deg_a = sum(1 for e in edges_a if e["source"] == c or e["target"] == c)
        
        # O nome do cargo no cenário B pode ser diferente, então usamos o mapeamento
        cb = mapping_a_to_b.get(c, c) 
        deg_b = sum(1 for e in edges_b if e["source"] == cb or e["target"] == cb)
        
        diff = deg_b - deg_a
        if diff > 0:
            status = "🔗 ↗ Mais Conectado"
        elif diff < 0:
            status = "✂️ ↘ Menos Conectado"
        else:
            status = "⚪ ➡ Estável"
            
        tabela_grafo.append({
            "Carreira": c,
            f"Conexões no Grafo ({cenario_a})": deg_a,
            f"Conexões no Grafo ({cenario_b})": deg_b,
            "Variação (Nº de Arestas)": diff,
            "Impacto na Rede": status
        })
        
    df_grafo = pd.DataFrame(tabela_grafo).sort_values(by="Variação (Nº de Arestas)", ascending=False).reset_index(drop=True)
    
    opcoes_status_25 = ["🔗 ↗ Mais Conectado", "✂️ ↘ Menos Conectado", "⚪ ➡ Estável"]
    filtro_status_25 = st.multiselect("Filtrar Impacto na Rede:", opcoes_status_25, default=opcoes_status_25, key="filtro_status_25")
    df_mostrar_25 = df_grafo[df_grafo["Impacto na Rede"].isin(filtro_status_25)]
    
    def highlight_25(row):
        c = row["Carreira"]
        if c in color_map:
            return [f'background-color: {color_map[c]}; color: {text_map[c]}; font-weight: bold;'] * len(row)
        return [''] * len(row)
        
    st.dataframe(
        df_mostrar_25.style.apply(highlight_25, axis=1),
        use_container_width=True,
        column_config={
            "Variação (Nº de Arestas)": st.column_config.NumberColumn(
                "Variação (Nº de Arestas)",
                format="%+d"
            )
        },
        height=(len(df_mostrar_25) + 1) * 35 + 3
    )
    if st.session_state.get('show_explanations', False):
        st.info(explanations.get_explanation("m2_grafo", st.session_state.get('explanation_tone', 'tecnico')))

    st.markdown("---")

    st.subheader(
        "2.6. Árvore Hierárquica Comparativa (Dendrograma)",
        help="**O que é isso?**\nExibe as estruturas hierárquicas de classificação lado a lado. Você pode avaliar como as carreiras mudaram de 'galhos' na árvore evolutiva entre o Cenário Base e o Cenário Alvo."
    )
    
    # O Dendrograma precisa do gower_a e gower_b (já calculados anteriormente)
    # Apenas se houver mais de um cargo para poder clusterizar
    if len(gower_a.columns) > 1 and len(gower_b.columns) > 1:
        fig_dendro_a = visualizations.plot_dendrogram(gower_a, f"Árvore Cenário Base ({cenario_a})", cargos_destaque=[c for c in destaques_completos if c in gower_a.columns] or None)
        fig_dendro_b = visualizations.plot_dendrogram(gower_b, f"Árvore Cenário Alvo ({cenario_b})", cargos_destaque=[c for c in destaques_b if c in gower_b.columns] or None)
        
        col_dendro1, col_dendro2 = st.columns(2)
        with col_dendro1:
            st.plotly_chart(fig_dendro_a, use_container_width=True)
        with col_dendro2:
            st.plotly_chart(fig_dendro_b, use_container_width=True)
            
        st.markdown("#### Detalhamento Estrutural da Árvore")
        st.caption("A tabela abaixo identifica o vizinho funcional mais próximo de cada carreira na árvore hierárquica (o primeiro 'galho' com quem ela se funde) e verifica se houve salto de ramo metodológico.")
        
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
                mudou_galho = "🌳 🔀 Sim (Saltou)" if vizinho_b != viz_a_mapped else "⚪ Não (Manteve)"
                
                tabela_dendro.append({
                    "Carreira": c,
                    f"Vizinho Mais Próximo ({cenario_a})": vizinho_a,
                    f"Distância ({cenario_a})": val_a,
                    f"Novo Vizinho ({cenario_b})": vizinho_b,
                    f"Distância ({cenario_b})": val_b,
                    "Mudança de Ramo?": mudou_galho
                })
        
        if tabela_dendro:
            df_dendro = pd.DataFrame(tabela_dendro).sort_values(by=f"Distância ({cenario_a})").reset_index(drop=True)
            
            opcoes_status_26 = ["🌳 🔀 Sim (Saltou)", "⚪ Não (Manteve)"]
            filtro_status_26 = st.multiselect("Filtrar Mudança de Ramo:", opcoes_status_26, default=opcoes_status_26, key="filtro_status_26")
            df_mostrar_26 = df_dendro[df_dendro["Mudança de Ramo?"].isin(filtro_status_26)]
            
            def highlight_26(row):
                c = row["Carreira"]
                if c in color_map:
                    return [f'background-color: {color_map[c]}; color: {text_map[c]}; font-weight: bold;'] * len(row)
                return [''] * len(row)
                
            st.dataframe(
                df_mostrar_26.style.apply(highlight_26, axis=1),
                use_container_width=True,
                column_config={
                    f"Distância ({cenario_a})": st.column_config.NumberColumn(
                        f"Distância ({cenario_a})",
                        format="%.3f"
                    ),
                    f"Distância ({cenario_b})": st.column_config.NumberColumn(
                        f"Distância ({cenario_b})",
                        format="%.3f"
                    )
                },
                height=(len(df_mostrar_26) + 1) * 35 + 3
            )
            
    else:
        st.warning("Não há carreiras suficientes para gerar a árvore hierárquica.")
    if st.session_state.get('show_explanations', False):
        st.info(explanations.get_explanation("m2_dendro", st.session_state.get('explanation_tone', 'tecnico')))

    st.markdown("<div style='height: 150px;'></div>", unsafe_allow_html=True)
