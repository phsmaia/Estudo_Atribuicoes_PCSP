import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import i18n

def plot_binary_heatmap(df: pd.DataFrame, title: str, colorscale: str = "Teal", dic_reverso: dict = None, cargos_destaque: list = None) -> go.Figure:
    """
    Renderiza um mapa de calor interativo (Plotly) para as matrizes binárias de atribuições.
    A interatividade garante clareza (tooltips nas células).
    """
    df_temp = df.copy()
    if 'Carreira' in df_temp.columns:
        df_temp = df_temp.set_index('Carreira')
    
    # Garantir formato numérico
    df_temp = df_temp.apply(pd.to_numeric, errors='coerce').fillna(0)
    
    # Criação de um hover text customizado
    hover_text = []
    for index, row in df_temp.iterrows():
        hover_row = []
        for col in df_temp.columns:
            # Pega o texto completo se o dic_reverso existir, senão usa a própria coluna
            nome_real = dic_reverso.get(col, col) if dic_reverso else col
            hover_row.append(f"<b>{i18n.t('hover_career')}:</b> {index}<br><b>{i18n.t('hover_assignment')}:</b> {nome_real}<br><b>{i18n.t('hover_value')}:</b> {row[col]}")
        hover_text.append(hover_row)
        
    fig = go.Figure(data=go.Heatmap(
        z=df_temp.values,
        x=df_temp.columns,
        y=df_temp.index,
        colorscale=colorscale,
        xgap=2, ygap=2,
        text=hover_text,
        hoverinfo="text",
        showscale=False
    ))
    
    # Ajuste de layout para legibilidade
    fig.update_layout(
        title=title,
        title_font_size=20,
        margin=dict(l=150, r=20, t=50, b=150),
    )
    fig.update_yaxes(autorange="reversed")
    
    # Ajuste dos ticks no eixo X para ficar vertical caso os textos sejam grandes
    fig.update_xaxes(tickangle=45)
    
    if cargos_destaque:
        colors = ["Gold", "Cyan", "Magenta", "Lime", "Orange", "Pink", "Red", "Blue", "Green", "Yellow"]
        for i, cargo in enumerate(cargos_destaque):
            if cargo in df_temp.index:
                idx = list(df_temp.index).index(cargo)
                color = colors[i % len(colors)]
                fig.add_shape(type="rect",
                    x0=-0.5, y0=idx-0.5, x1=len(df_temp.columns)-0.5, y1=idx+0.5,
                    line=dict(color=color, width=2), fillcolor="rgba(0,0,0,0)"
                )
    
    return fig

def plot_correlation_heatmap(matriz_corr: pd.DataFrame, title: str) -> go.Figure:
    """
    Gera um mapa de calor de correlação estatística entre carreiras.
    """
    fig = go.Figure(data=go.Heatmap(
        z=matriz_corr.values,
        x=matriz_corr.columns,
        y=matriz_corr.index,
        colorscale="RdBu_r",
        zmin=-1, zmax=1,
        xgap=1, ygap=1,
        hovertemplate=f"<b>{i18n.t('hover_career_a')}:</b> %{{y}}<br><b>{i18n.t('hover_career_b')}:</b> %{{x}}<br><b>Correlação:</b> %{{z:.2f}}<extra></extra>"
    ))
    fig.update_layout(
        title=title,
        title_font_size=20,
        margin=dict(l=100, r=20, t=50, b=100)
    )
    return fig

def plot_network_graph(nodes_data: list, edges_data: list, title: str, cargos_destaque: list = None) -> go.Figure:
    """
    Renderiza um grafo interativo usando as coordenadas previamente calculadas pelo NetworkX.
    """
    # Arestas
    edge_traces = []
    for edge in edges_data:
        x0, y0 = next((n["x"], n["y"]) for n in nodes_data if n["id"] == edge["source"])
        x1, y1 = next((n["x"], n["y"]) for n in nodes_data if n["id"] == edge["target"])
        
        peso = edge["weight"]
        # Espessura escalonada via raiz quadrada para evitar linhas de 30px
        import math
        largura = max(0.5, 0.5 + math.sqrt(peso)) if peso > 0 else 0.5
        
        line_color = '#888'
        if cargos_destaque:
            if edge["source"] in cargos_destaque or edge["target"] in cargos_destaque:
                line_color = '#ccc'
                largura = largura * 1.5
            else:
                line_color = 'rgba(50,50,50,0.1)'
        
        # O hovertext será mostrado no centro da aresta
        mid_x = (x0 + x1) / 2
        mid_y = (y0 + y1) / 2
        
        edge_traces.append(go.Scatter(
            x=[x0, x1, None],
            y=[y0, y1, None],
            line=dict(width=largura, color=line_color),
            hoverinfo='none',
            mode='lines'
        ))
        
        # Ponto invisível no meio da linha para ativar o Hovertext
        texto_hover = f"<b>{edge['source']} ↔ {edge['target']}</b><br>{i18n.t('hover_force')}: {peso:.2f}<br>{i18n.t('hover_common')}: {edge['hovertext']}"
        edge_traces.append(go.Scatter(
            x=[mid_x],
            y=[mid_y],
            mode='markers',
            marker=dict(size=0.1, color='rgba(0,0,0,0)'),
            text=[texto_hover],
            hoverinfo='text',
            showlegend=False
        ))

    node_x = [n["x"] for n in nodes_data]
    node_y = [n["y"] for n in nodes_data]
    node_text = [n["id"] for n in nodes_data]
    
    node_colors = px.colors.qualitative.Plotly
    cores_nos = []
    tamanhos_nos = []
    text_colors = []
    for i, n in enumerate(nodes_data):
        if cargos_destaque and n["id"] in cargos_destaque:
            idx_color = cargos_destaque.index(n["id"]) % len(node_colors)
            cores_nos.append(node_colors[idx_color])
            tamanhos_nos.append(35)
            text_colors.append("white")
        elif cargos_destaque:
            cores_nos.append("rgba(100,100,100,0.5)") # Faded se não for destaque
            tamanhos_nos.append(10)
            text_colors.append("rgba(100,100,100,0.5)")
        else:
            cores_nos.append(node_colors[i % len(node_colors)])
            tamanhos_nos.append(20)
            text_colors.append("white")

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        textposition="top center",
        hoverinfo='text',
        text=node_text,
        textfont=dict(color=text_colors, size=12),
        marker=dict(
            showscale=False,
            color=cores_nos,
            size=tamanhos_nos,
            line_width=2))


    fig = go.Figure(data=edge_traces + [node_trace],
             layout=go.Layout(
                title=title,
                title_font_size=20,
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20,l=5,r=5,t=40),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                )
    return fig

def plot_adjacency_heatmap(adj_matrix: pd.DataFrame, title: str, text_matrix: pd.DataFrame = None, cargos_destaque: list = None, colorscale="YlGnBu") -> go.Figure:
    """
    Gera um mapa de calor para a matriz de adjacência (número de atribuições em comum).
    """
    import numpy as np
    adj_array = adj_matrix.to_numpy(dtype=float, copy=True)
    np.fill_diagonal(adj_array, np.nan)
    adj_vis = pd.DataFrame(adj_array, index=adj_matrix.index, columns=adj_matrix.columns)
    
    # Se uma matriz de textos (atributos compartilhados) foi enviada, injetamos como customdata
    custom_data = text_matrix.values if text_matrix is not None else None
    
    hovertemplate = f"<b>{i18n.t('hover_career_a')}:</b> %{{y}}<br><b>{i18n.t('hover_career_b')}:</b> %{{x}}<br><b>{i18n.t('hover_shared_assignments')}:</b> %{{z}}<extra></extra>"
    if custom_data is not None:
        hovertemplate = f"<b>{i18n.t('hover_career_a')}:</b> %{{y}}<br><b>{i18n.t('hover_career_b')}:</b> %{{x}}<br><b>{i18n.t('hover_qty_assignments')}:</b> %{{z}}<br><b>{i18n.t('hover_common')}:</b><br>%{{customdata}}<extra></extra>"
    
    fig = go.Figure(data=go.Heatmap(
        z=adj_vis.values,
        x=adj_vis.columns,
        y=adj_vis.index,
        customdata=custom_data,
        colorscale=colorscale,
        xgap=1, ygap=1,
        hovertemplate=hovertemplate
    ))
    fig.update_layout(
        title=title,
        title_font_size=20,
        margin=dict(l=100, r=20, t=50, b=100)
    )
    fig.update_yaxes(autorange="reversed")
    
    if cargos_destaque:
        colors = ["Gold", "Cyan", "Magenta", "Lime", "Orange", "Pink", "Red", "Blue", "Green", "Yellow"]
        for i, cargo in enumerate(cargos_destaque):
            if cargo in adj_vis.index:
                idx = list(adj_vis.index).index(cargo)
                color = colors[i % len(colors)]
                # Linha
                fig.add_shape(type="rect",
                    x0=-0.5, y0=idx-0.5, x1=len(adj_vis.columns)-0.5, y1=idx+0.5,
                    line=dict(color=color, width=2), fillcolor="rgba(0,0,0,0)"
                )
                # Coluna
                fig.add_shape(type="rect",
                    x0=idx-0.5, y0=-0.5, x1=idx+0.5, y1=len(adj_vis.index)-0.5,
                    line=dict(color=color, width=2), fillcolor="rgba(0,0,0,0)"
                )
    
    return fig

def plot_gower_heatmap(df_gower: pd.DataFrame, title: str, cargos_destaque: list = None) -> go.Figure:
    """
    Gera um mapa de calor da Matriz de Gower. Valores próximos a 0 significam
    maior similaridade, enquanto valores próximos a 1 significam maior distância.
    A escala de cores é ajustada para dar foco em 0 (ex: cores mais quentes).
    """
    # Gower distance is symmetric with 0 on the diagonal
    gower_vis = df_gower
    fig = go.Figure(data=go.Heatmap(
        z=gower_vis.values,
        x=gower_vis.columns,
        y=gower_vis.index,
        colorscale="RdYlBu",
        zmin=0.0, zmax=1.0,
        xgap=1, ygap=1,
        hovertemplate=f"<b>{i18n.t('hover_career_a')}:</b> %{{y}}<br><b>{i18n.t('hover_career_b')}:</b> %{{x}}<br><b>{i18n.t('hover_gower_dist')}:</b> %{{z:.4f}}<extra></extra>"
    ))
    fig.update_layout(
        title=title,
        title_font_size=20,
        margin=dict(l=100, r=20, t=50, b=100)
    )
    # Reverte o eixo y para bater com as outras matrizes (Delegado no topo)
    fig.update_yaxes(autorange="reversed")
    
    if cargos_destaque:
        colors = ["Gold", "Cyan", "Magenta", "Lime", "Orange", "Pink", "Red", "Blue", "Green", "Yellow"]
        for i, cargo in enumerate(cargos_destaque):
            if cargo in df_gower.index:
                idx = list(df_gower.index).index(cargo)
                color = colors[i % len(colors)]
                # Linha
                fig.add_shape(type="rect",
                    x0=-0.5, y0=idx-0.5, x1=len(df_gower.columns)-0.5, y1=idx+0.5,
                    line=dict(color=color, width=2), fillcolor="rgba(0,0,0,0)"
                )
                # Coluna
                fig.add_shape(type="rect",
                    x0=idx-0.5, y0=-0.5, x1=idx+0.5, y1=len(df_gower.index)-0.5,
                    line=dict(color=color, width=2), fillcolor="rgba(0,0,0,0)"
                )
                
    return fig

def plot_distance_histogram(df_dist: pd.DataFrame, title: str, full_scale: bool = True) -> go.Figure:
    """
    Gera um gráfico de bolinhas (Dot Plot / Jitter Scatter) da distribuição das distâncias
    para entender o comportamento da métrica, com cores e hover detalhado.
    """
    import numpy as np
    
    # Extract upper triangle values (excluding diagonal) to avoid duplication
    arr = df_dist.values
    mask = np.triu(np.ones_like(arr, dtype=bool), k=1)
    
    rows, cols = np.where(mask)
    distances = arr[rows, cols]
    
    # Criar textos de hover com os pares de cargos
    cargos = df_dist.index.tolist()
    pairs = [f"{cargos[r]} ↔ {cargos[c]}" for r, c in zip(rows, cols)]
    
    # Criar um eixo Y aleatório (jitter) para espalhar as bolinhas
    jitter_y = np.random.uniform(-0.5, 0.5, size=len(distances))
    
    fig = go.Figure()
    
    # Adicionar zonas de similaridade (mesmo padrão da Régua Gower)
    fig.add_vrect(x0=-0.05, x1=0.15, fillcolor="rgba(0, 255, 0, 0.1)", line_width=0, layer="below", annotation_text=i18n.t("zone_very_high", default="Muito Alta"), annotation_position="top left", annotation_font_size=10, annotation_font_color="#00cc00")
    fig.add_vrect(x0=0.15, x1=0.35, fillcolor="rgba(144, 238, 144, 0.1)", line_width=0, layer="below", annotation_text=i18n.t("zone_high", default="Alta"), annotation_position="top left", annotation_font_size=10, annotation_font_color="#90ee90")
    fig.add_vrect(x0=0.35, x1=0.50, fillcolor="rgba(255, 255, 0, 0.1)", line_width=0, layer="below", annotation_text=i18n.t("zone_moderate", default="Moderada"), annotation_position="top left", annotation_font_size=10, annotation_font_color="#cccc00")
    fig.add_vrect(x0=0.50, x1=0.65, fillcolor="rgba(255, 165, 0, 0.1)", line_width=0, layer="below", annotation_text=i18n.t("zone_low", default="Baixa"), annotation_position="top left", annotation_font_size=10, annotation_font_color="#ff9900")
    fig.add_vrect(x0=0.65, x1=1.05, fillcolor="rgba(255, 0, 0, 0.1)", line_width=0, layer="below", annotation_text=i18n.t("zone_very_low", default="Muito Baixa"), annotation_position="top left", annotation_font_size=10, annotation_font_color="#ff4444")
    
    # Adicionar as bolinhas com escala de cor
    fig.add_trace(go.Scatter(
        x=distances,
        y=jitter_y,
        mode='markers',
        text=pairs,
        marker=dict(
            color=distances,
            colorscale='RdYlGn_r', # Verde para distâncias baixas, Vermelho para altas
            cmin=0.0,
            cmax=1.0,
            size=10,
            opacity=0.8,
            line=dict(width=1, color='rgba(255, 255, 255, 0.8)')
        ),
        hovertemplate="<b>Par:</b> %{text}<br><b>" + i18n.t('dist_value', default='Distância') + ":</b> %{x:.3f}<extra></extra>"
    ))
    
    # Linhas de média e mediana
    mean_dist = np.mean(distances)
    median_dist = np.median(distances)
    
    fig.add_vline(x=mean_dist, line_width=2, line_dash="dash", line_color="red", 
                  annotation_text=f"{i18n.t('lbl_average', default='Média')}: {mean_dist:.2f}", annotation_position="bottom right",
                  annotation_font_color="red")
                  
    fig.add_vline(x=median_dist, line_width=2, line_dash="dot", line_color="orange", 
                  annotation_text=f"{i18n.t('lbl_median', default='Mediana')}: {median_dist:.2f}", annotation_position="bottom left",
                  annotation_font_color="orange")
    
    xaxis_dict = dict(
        showgrid=True,
        gridcolor='rgba(255, 255, 255, 0.1)'
    )
    if full_scale:
        xaxis_dict['range'] = [-0.05, 1.05]
        xaxis_dict['tickmode'] = 'linear'
        xaxis_dict['dtick'] = 0.1
    else:
        min_dist = np.min(distances) if len(distances) > 0 else 0
        max_dist = np.max(distances) if len(distances) > 0 else 1
        padding = (max_dist - min_dist) * 0.1
        if padding == 0:
            padding = 0.1
        xaxis_dict['range'] = [max(-0.05, min_dist - padding), min(1.05, max_dist + padding)]
        
    fig.update_layout(
        title=title,
        title_font_size=16,
        xaxis_title=i18n.t("dist_value", default="Valor da Distância"),
        yaxis_title="",
        margin=dict(l=20, r=20, t=60, b=20),
        height=300,
        xaxis=xaxis_dict,
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-0.6, 0.8])
    )
    return fig

def plot_gower_ruler(df_gower: pd.DataFrame, reference_career: str = "Delegado de Polícia", cargos_destaque: list = None, full_scale: bool = True) -> go.Figure:
    """
    Cria uma régua 1D (Scatter plot) baseada na distância de Gower de todos os cargos
    em relação a um cargo de referência (Delegado de Polícia, assumindo x=0).
    """
    if reference_career not in df_gower.columns:
        return go.Figure()
    
    # Extrair as distâncias em relação ao cargo de referência
    dist_serie = df_gower[reference_career].sort_values()
    
    fig = go.Figure()
    
    # Adicionar Zonas de Similaridade (Fundo Colorido)
    # Verde (0 a 0.33) - Alta Similaridade
    fig.add_vrect(x0=0, x1=0.33, fillcolor="green", opacity=0.1, layer="below", line_width=0,
                  annotation_text=i18n.t("zone_high_sim", default="Alta Similaridade"), annotation_position="top left",
                  annotation_font_color="green", annotation_font_size=10)
    # Amarelo (0.33 a 0.66) - Similaridade Moderada
    fig.add_vrect(x0=0.33, x1=0.66, fillcolor="yellow", opacity=0.1, layer="below", line_width=0,
                  annotation_text=i18n.t("zone_mod_sim", default="Similaridade Moderada"), annotation_position="top left",
                  annotation_font_color="goldenrod", annotation_font_size=10)
    # Vermelho (0.66 a 1.0+) - Baixa Similaridade
    fig.add_vrect(x0=0.66, x1=1.05, fillcolor="red", opacity=0.1, layer="below", line_width=0,
                  annotation_text=i18n.t("zone_low_sim", default="Baixa Similaridade"), annotation_position="top left",
                  annotation_font_color="red", annotation_font_size=10)
    
    # Adicionamos os pontos ao scatter. O eixo X é a distância, o eixo Y pode ser 0.
    media_dist = dist_serie.mean()
    mediana_dist = dist_serie.median()
    
    fig.add_shape(type="line", x0=media_dist, x1=media_dist, y0=-1, y1=len(dist_serie),
                  line=dict(color="red", width=2, dash="dash"))
    fig.add_annotation(x=media_dist, y=len(dist_serie)-0.5, text=f"{i18n.t('hover_mean')} ({media_dist:.2f})", showarrow=False, font=dict(color="red"), yshift=10)
    
    fig.add_shape(type="line", x0=mediana_dist, x1=mediana_dist, y0=-1, y1=len(dist_serie),
                  line=dict(color="orange", width=2, dash="dash"))
    fig.add_annotation(x=mediana_dist, y=-0.5, text=f"{i18n.t('hover_median')} ({mediana_dist:.2f})", showarrow=False, font=dict(color="orange"), yshift=-10)

    tamanhos = []
    cores = []
    for c in dist_serie.index:
        if cargos_destaque and c in cargos_destaque:
            tamanhos.append(20)
            cores.append("gold")
        elif cargos_destaque:
            tamanhos.append(8)
            cores.append("rgba(100,100,100,0.5)")
        else:
            tamanhos.append(12)
            cores.append(dist_serie.loc[c])
            
    fig.add_trace(go.Scatter(
        x=dist_serie.values,
        y=dist_serie.index,
        mode='markers',
        marker=dict(
            size=tamanhos, 
            color=cores, 
            colorscale='Viridis' if not cargos_destaque else None, 
            showscale=not bool(cargos_destaque)
        ),
        text=dist_serie.index,
        hovertemplate=f"<b>{i18n.t('hover_career')}:</b> %{{text}}<br><b>{i18n.t('hover_gower_dist')}:</b> %{{x:.3f}}<extra></extra>"
    ))
    
    # Substituir o título dinâmico com o i18n da seção 1.6
    fig.update_layout(
        title=f"{i18n.t('sub_ruler')} (Ref: {reference_career})",
        title_font_size=18,
        xaxis_title=i18n.t('hover_gower_dist'),
        yaxis_title=None,
        yaxis=dict(showgrid=True, gridcolor='rgba(0, 0, 0, 0.25)', gridwidth=1),
        margin=dict(l=150, r=50, t=50, b=50),
        height=500,
        autosize=True
    )
    
    if full_scale:
        fig.update_layout(xaxis=dict(range=[-0.05, 1.05]))
    else:
        min_val = dist_serie.min()
        max_val = dist_serie.max()
        padding = (max_val - min_val) * 0.05
        if padding == 0: 
            padding = 0.05
        fig.update_layout(xaxis=dict(range=[max(-0.05, min_val - padding), max_val + padding]))
                  
    return fig

import plotly.figure_factory as ff
from scipy.spatial.distance import squareform

def plot_dendrogram(df_gower: pd.DataFrame, title: str, cargos_destaque: list = None, linkage_method: str = 'single') -> go.Figure:
    """
    Gera um dendograma a partir da matriz de distâncias de Gower.
    """
    # Certificar-se que a matriz é simétrica (a gower as vezes tem floats com infimas diferenças)
    dist_array = (df_gower.values + df_gower.values.T) / 2
    # Preencher a diagonal com exatos 0s
    import numpy as np
    np.fill_diagonal(dist_array, 0)
    
    labels = []
    for lbl in df_gower.index:
        if cargos_destaque and lbl in cargos_destaque:
            labels.append(f"<b><span style='color:gold'>{lbl}</span></b>")
        else:
            labels.append(lbl)
    
    # Squareform requer distância sem a diagonal
    condensed_dist = squareform(dist_array)
    
    # Para usar o Plotly, precisamos criar um linkage
    from scipy.cluster.hierarchy import linkage, cophenet
    Z = linkage(condensed_dist, method=linkage_method)
    
    # Calcular Correlação Cofenética
    c, coph_dists = cophenet(Z, condensed_dist)
    import i18n
    
    if c >= 0.90:
        coph_color = "#00cc00" # Verde
    elif c >= 0.75:
        coph_color = "#ffcc00" # Amarelo escuro/Ouro
    elif c >= 0.50:
        coph_color = "#ff9900" # Laranja
    else:
        coph_color = "#ff3333" # Vermelho
        
    c_label = i18n.t('coph_corr_label', 'Correlação Cofenética:')
    coph_text = f"<span style='color:{coph_color}'><b>{c_label} {c:.3f}</b></span>"
    
    # Plotly figure factory aceita a matriz condensada ou dados crus.
    # Como já temos distâncias, a forma mais segura no Plotly é via scipy -> plotly dendrogram manual,
    # ou deixar o plotly calcular a hierarquia mas enviando a matriz squareform e uma função linkage custom.
    # Em implementações diretas:
    fig = ff.create_dendrogram(
        dist_array,
        labels=labels,
        orientation='left',
        linkagefun=lambda x: linkage(squareform(x) if x.ndim == 2 else x, method=linkage_method)
    )
    
    fig.update_layout(
        title=f"{title}<br><sup>{coph_text}</sup>",
        title_font_size=18,
        height=600,
        margin=dict(l=250, r=50, t=50, b=50),
        autosize=True
    )
    
    # Injetando as alturas nos ramos (Dendograma Plotly gera Scatters em formato de U)
    annotations = []
    for trace in fig.data:
        x = trace.x
        y = trace.y
        # No formato 'left', a linha vertical une os dois sub-ramos e seus X são idênticos
        if len(x) == 4 and len(y) == 4:
            if x[1] == x[2] and x[1] > 0:
                dist = x[1]
                mid_y = (y[1] + y[2]) / 2
                annotations.append(dict(
                    x=dist,
                    y=mid_y,
                    xref='x',
                    yref='y',
                    text=f"{dist:.2f}",
                    showarrow=False,
                    xanchor='left',
                    yanchor='middle',
                    font=dict(size=10, color="red"),
                    bgcolor="rgba(255, 255, 255, 0.8)",
                    bordercolor="rgba(0, 0, 0, 0)",
                    borderpad=2,
                    xshift=5
                ))
                
    fig.update_layout(annotations=annotations)
    
    return fig

def plot_upset_bar_chart(df: pd.DataFrame, title: str, dic_reverso: dict = None, cargos_destaque: list = None) -> go.Figure:
    """
    Simula a essência de um UpSet Plot usando um Bar Chart horizontal interativo no Plotly.
    Calcula as interseções reais entre os conjuntos de cargos.
    O DataFrame de entrada deve ter os cargos como índice (rows) e as atribuições nas colunas.
    """
    import streamlit as st
    lang = st.session_state.get('language', 'PT-BR') if 'language' in st.session_state else 'PT-BR'
    
    # Converter para booleano
    df_bool = df > 0
    total_attrs = len(df.columns)
    
    # Transpor: linhas = atribuições, colunas = carreiras
    df_attrs = df_bool.T
    
    if df_attrs.empty:
        return go.Figure()
        
    cols = list(df_attrs.columns)
    
    # Agrupar para descobrir o tamanho da interseção
    combination_counts = df_attrs.groupby(cols).size().reset_index(name='count')
    
    # Agrupar para descobrir EXATAMENTE QUAIS SÃO as atribuições daquela interseção
    # Como o index original do df_attrs são as siglas (ou nomes), pegamos a lista do index
    attr_lists = df_attrs.groupby(cols).apply(lambda x: list(x.index)).reset_index(name='attributes_list')
    
    # Mesclar as contagens com a lista de nomes
    combination_counts = combination_counts.merge(attr_lists, on=cols)
    
    # Filtrar onde pelo menos um cargo possui a atribuição (ignorar a linha onde todos são False)
    combination_counts['has_any'] = combination_counts[cols].any(axis=1)
    combination_counts = combination_counts[combination_counts['has_any']]
    
    def make_label(row):
        c_list = [c for c in cols if row[c]]
        
        if len(c_list) == len(cols):
            return i18n.t_lang("upset_all_roles", lang)
        elif len(c_list) == 1:
            return c_list[0] + f" {i18n.t_lang('upset_exclusive', lang)}"
        elif len(c_list) == 2:
            return c_list[0] + " + " + c_list[1]
        else:
            return f"[{len(c_list)} {i18n.t_lang('upset_roles_count', lang)}] " + " + ".join([c[:8]+"." for c in c_list])
            
    def make_hover(row):
        # Transforma a lista de siglas em nomes originais
        raw_list = row['attributes_list']
        if dic_reverso:
            text_list = [dic_reverso.get(a, a) for a in raw_list]
        else:
            text_list = raw_list
            
        # Limita a exibição no hover para não estourar a tela (ex: max 15 atribuições)
        max_show = 15
        display_list = text_list[:max_show]
        joined = "<br> - " + "<br> - ".join([t[:90] + "..." if len(t) > 90 else t for t in display_list])
        if len(text_list) > max_show:
            diff = len(text_list) - max_show
            joined += f"<br><i>{i18n.t('upset_more_attr').format(count=diff)}</i>"
            
        c_list = [c for c in cols if row[c]]
        cargos_str = "<br>".join(c_list)
        pct = (row['count'] / total_attrs) * 100
        
        return cargos_str, joined, pct
            
    combination_counts['label'] = combination_counts.apply(make_label, axis=1)
    
    # Extrai tupla do hover para múltiplas customdatas
    hover_data = combination_counts.apply(make_hover, axis=1)
    combination_counts['cargos_str'] = [x[0] for x in hover_data]
    combination_counts['atributos_str'] = [x[1] for x in hover_data]
    combination_counts['pct'] = [x[2] for x in hover_data]
    
    # Ordenar pela contagem
    combination_counts = combination_counts.sort_values(by='count', ascending=True)
    
    # Limitar top 30
    if len(combination_counts) > 30:
        combination_counts = combination_counts.tail(30)
        title += " (Top 30 Interseções)"
        
    marker_colors = []
    if cargos_destaque:
        # Usa as mesmas cores padronizadas dos outros gráficos
        colors = ["Gold", "Cyan", "Magenta", "Lime", "Orange", "Pink", "Red", "Blue", "Green", "Yellow"]
        for c_str in combination_counts['cargos_str']:
            destaques_no_grupo = [cargo for cargo in cargos_destaque if cargo in c_str]
            if len(destaques_no_grupo) == 1:
                idx = cargos_destaque.index(destaques_no_grupo[0])
                marker_colors.append(colors[idx % len(colors)])
            elif len(destaques_no_grupo) > 1:
                marker_colors.append("#FFFFFF") # Branco se aglutinar múltiplos destaques
            else:
                marker_colors.append("rgba(100,100,100,0.5)")
    else:
        marker_colors = combination_counts['count']
        
    fig = go.Figure(go.Bar(
        x=combination_counts['count'],
        y=combination_counts['label'],
        orientation='h',
        customdata=combination_counts[['cargos_str', 'atributos_str', 'pct']].values,
        hovertemplate=(
            f"<b>{i18n.t('hover_represent')}:</b> %{{customdata[2]:.1f}}%<br>"
            f"<b>{i18n.t('hover_roles_involved')}:</b> %{{customdata[0]}}<br>"
            f"<b>{i18n.t('hover_shared_attr')}:</b> %{{x}}<br><br>"
            f"<b>{i18n.t('hover_shared_assignments')}:</b>%{{customdata[1]}}"
            "<extra></extra>"
        ),
        marker=dict(
            color=marker_colors,
            colorscale='Blues' if not cargos_destaque else None,
            showscale=not bool(cargos_destaque),
            colorbar=dict(title="Volume") if not cargos_destaque else None
        )
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title=i18n.t('hover_shared_attr'),
        yaxis_title=None,
        margin=dict(l=250, r=20, t=50, b=50),
        height=max(400, len(combination_counts) * 35),
        autosize=True
    )
    return fig
