import pandas as pd
import streamlit as st
import numpy as np

@st.cache_data(show_spinner=False)
def remover_atribuicoes_comuns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Identifica e remove atribuições (colunas) que possuam valor 1 em todas as carreiras.
    Essas atribuições são comuns a todos e não possuem valor discriminatório.
    """
    # Identifica as colunas que têm 1 em todas as linhas
    cols_all_ones = df.loc[:, (df == 1).all()].columns.tolist()
    if cols_all_ones:
        return df.drop(cols_all_ones, axis=1)
    return df

@st.cache_data(show_spinner=False)
def condensar_dataframe(df_original: pd.DataFrame) -> tuple[pd.DataFrame, list]:
    """
    Compara as colunas do dataframe e aglutina aquelas que possuem valores idênticos
    para todos os cargos. Reduz a dimensionalidade sem perda de informação estrutural.
    Retorna o DataFrame condensado e o histórico de reduções.
    """
    df_condensed = df_original.copy()
    
    # Remove colunas comuns antes de condensar, caso não tenha sido feito
    df_condensed = remover_atribuicoes_comuns(df_condensed)

    loop_keeper = 0
    historico_juncoes = []
    cont_reducoes = 0

    while loop_keeper == 0:
        loop_keeper = 1 
        columns = list(df_condensed.columns)

        for i in range(len(columns)):
            for j in range(i + 1, len(columns)): 
                # Se as colunas são idênticas (mesmo vetor de distribuição)
                if df_condensed[columns[i]].equals(df_condensed[columns[j]]):
                    cont_reducoes += 1
                    nome_atribuicao_juntada = columns[i] + ' / ' +  columns[j]
                    historico_juncoes.append(f"Redução Nº {cont_reducoes}: ({columns[i]} / {columns[j]})")
                    
                    df_condensed = df_condensed.rename(columns={columns[i]: nome_atribuicao_juntada})
                    df_condensed = df_condensed.drop(columns[j], axis=1)
                    
                    loop_keeper = 0
                    break
            if loop_keeper == 0:
                break

    return df_condensed, historico_juncoes

@st.cache_data(show_spinner=False)
def gerar_matriz_correlacao(df: pd.DataFrame) -> pd.DataFrame:
    """
    Gera uma matriz de correlação baseada no dataframe binário.
    Cargos nas linhas e colunas serão transpostos se necessário.
    """
    # Set Carreira como index temporariamente para correlação
    df_temp = df.copy()
    if 'Carreira' in df_temp.columns:
        df_temp = df_temp.set_index('Carreira')
    
    # Garantir valores numéricos
    df_temp = df_temp.apply(pd.to_numeric, errors='coerce').fillna(0)
    
    # Correlacionar carreiras baseando-se nas atribuições
    # A correlação é feita entre as linhas (cargos), por isso transpomos (T)
    matriz_corr = df_temp.T.corr()
    return matriz_corr

def gerar_dicionario_siglas(colunas) -> dict:
    """
    Gera um dicionário mapeando nomes originais longos de atribuições para siglas curtas (A_01, A_02).
    """
    return {col: f"A_{str(i+1).zfill(2)}" for i, col in enumerate(colunas) if col != 'Carreira'}

@st.cache_data(show_spinner=False)
def aplicar_siglas_dataframe(df: pd.DataFrame, dic_siglas: dict) -> pd.DataFrame:
    """
    Renomeia as colunas de um dataframe usando o dicionário de siglas.
    """
    return df.rename(columns=dic_siglas)

import networkx as nx

@st.cache_data(show_spinner=False)
def gerar_dados_grafo(matriz_corr: pd.DataFrame, threshold: float = 0.5, text_matrix: pd.DataFrame = None) -> tuple[list, list, dict]:
    """
    Utiliza NetworkX para processar a matriz de correlação como um grafo.
    Filtra arestas com base no threshold numérico.
    Retorna nós, arestas e posições (X, Y) do spring_layout para renderização em UI.
    """
    G = nx.Graph()
    
    # Adicionando nós
    cargos = matriz_corr.columns.tolist()
    G.add_nodes_from(cargos)
    
    # Adicionando arestas com base no threshold
    for i in range(len(cargos)):
        for j in range(i + 1, len(cargos)):
            peso = matriz_corr.iloc[i, j]
            if peso >= threshold:
                c1, c2 = cargos[i], cargos[j]
                
                texto_hover = ""
                if text_matrix is not None and c1 in text_matrix.index and c2 in text_matrix.columns:
                    texto_hover = text_matrix.loc[c1, c2]
                    
                G.add_edge(c1, c2, weight=peso, hovertext=texto_hover)
                
    # Calculando layout espacial (K = 3.0 para afastar fortemente os agrupamentos densos)
    pos = nx.spring_layout(G, k=3.0, iterations=100, seed=42)
    
    nodes_data = [{"id": n, "x": pos[n][0], "y": pos[n][1]} for n in G.nodes()]
    edges_data = [{"source": u, "target": v, "weight": d['weight'], "hovertext": d.get('hovertext', '')} for u, v, d in G.edges(data=True)]
    
    return nodes_data, edges_data, pos

@st.cache_data(show_spinner=False)
def gerar_matriz_adjacencia(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula a matriz de adjacência (número de atribuições compartilhadas).
    Produto escalar da matriz binária.
    """
    df_temp = df.copy()
    if 'Carreira' in df_temp.columns:
        df_temp = df_temp.set_index('Carreira')
    df_temp = df_temp.apply(pd.to_numeric, errors='coerce').fillna(0)
    
    # Adjacência = df dot df.T
    adj = df_temp.dot(df_temp.T)
    return adj

import textwrap

@st.cache_data(show_spinner=False)
def obter_atribuicoes_comuns_textuais(df: pd.DataFrame, dic_siglas: dict, expandir_textos: bool) -> pd.DataFrame:
    """
    Gera uma matriz quadrática contendo a string de quais atribuições 
    são compartilhadas entre cada par de carreiras.
    """
    df_temp = df.copy()
    if 'Carreira' in df_temp.columns:
        df_temp = df_temp.set_index('Carreira')
    df_temp = df_temp.apply(pd.to_numeric, errors='coerce').fillna(0)
    
    cargos = df_temp.index.tolist()
    text_matrix = pd.DataFrame(index=cargos, columns=cargos, dtype=str)
    
    for i in range(len(cargos)):
        for j in range(len(cargos)):
            c1, c2 = cargos[i], cargos[j]
            # Quais colunas ambos tem 1?
            comuns = df_temp.columns[(df_temp.loc[c1] == 1) & (df_temp.loc[c2] == 1)].tolist()
            
            linhas_texto = []
            for col in comuns:
                if expandir_textos:
                    # Quebra a string em linhas de 60 chars para não estourar a tela
                    wrapped = textwrap.fill(col, width=60)
                    linhas_texto.append(wrapped.replace('\n', '<br>'))
                else:
                    linhas_texto.append(dic_siglas.get(col, col))
            
            import i18n
            # Se for expandido, adiciona bullet points. Se não, separa por vírgula.
            if expandir_textos:
                texto_final = "<br>• ".join([""] + linhas_texto) if linhas_texto else i18n.t("none_text")
            else:
                texto_final = ", ".join(linhas_texto) if linhas_texto else i18n.t("none_text")
                
            text_matrix.loc[c1, c2] = texto_final
            
    return text_matrix

import gower
from scipy.spatial.distance import pdist, squareform
from scipy.cluster.hierarchy import linkage

def overlap_dist(u, v):
    u = u.astype(bool)
    v = v.astype(bool)
    a = np.sum(u & v)
    b = np.sum(u & ~v)
    c = np.sum(~u & v)
    min_ab_ac = min(a+b, a+c)
    if min_ab_ac == 0:
        return 1.0 # Distância máxima
    return 1.0 - (a / min_ab_ac)

@st.cache_data(show_spinner=False)
def calcular_distancias(df: pd.DataFrame, metric: str = 'jaccard', _cache_buster: int = 1) -> pd.DataFrame:
    """
    Calcula a matriz de distâncias usando a métrica escolhida. (Cache invalidado)
    """
    df_temp = df.copy()
    if 'Carreira' in df_temp.columns:
        df_temp = df_temp.set_index('Carreira')
    df_temp = df_temp.apply(pd.to_numeric, errors='coerce').fillna(0)
    
    # Cast explícito para float
    df_temp = df_temp.astype(float)
    
    # Remover colunas sem variância (mesmo valor para todos os cargos)
    # Isso evita divisão por zero no cálculo de distâncias como Gower
    nunique = df_temp.nunique()
    df_temp = df_temp.loc[:, nunique > 1]
    
    if metric == 'gower':
        # Mantendo gower por compatibilidade, embora seja simétrico
        dist_matrix = gower.gower_matrix(df_temp)
    else:
        # Se for string reconhecida pelo pdist ou função
        metric_arg = overlap_dist if metric == 'overlap' else metric
        dist_array = pdist(df_temp, metric=metric_arg)
        dist_matrix = squareform(dist_array)
        
    df_dist = pd.DataFrame(dist_matrix, index=df_temp.index, columns=df_temp.index)
    return df_dist

from scipy.cluster.hierarchy import cophenet
import numpy as np

@st.cache_data(show_spinner=False)
def get_cophenetic_comparison_table(df: pd.DataFrame, _cache_buster: int = 2) -> pd.DataFrame:
    """
    Gera uma tabela com os índices cofenéticos para diferentes métricas e métodos de linkage. (Cache Invalidado)
    """
    metrics = ['gower', 'jaccard', 'sokalsneath', 'dice', 'overlap', 'cosine']
    linkages = ['single', 'complete', 'average']
    
    results = []
    for m in metrics:
        try:
            df_dist = calcular_distancias(df, metric=m)
            dist_array = (df_dist.values + df_dist.values.T) / 2
            np.fill_diagonal(dist_array, 0)
            
            # Replace NaNs with 1.0 (max distance) to avoid linkage failure
            dist_array = np.nan_to_num(dist_array, nan=1.0)
            
            condensed_dist = squareform(dist_array)
            
            row = {"Métrica": m}
            for l in linkages:
                try:
                    Z = linkage(condensed_dist, method=l)
                    c, _ = cophenet(Z, condensed_dist)
                    if np.isnan(c):
                        c = 0.0
                    row[l.capitalize()] = c
                except Exception:
                    row[l.capitalize()] = 0.0
            results.append(row)
        except Exception:
            continue
            
    df_results = pd.DataFrame(results)
    if df_results.empty:
        return df_results
        
    df_results['Métrica'] = df_results['Métrica'].map({
        'gower': 'Gower',
        'jaccard': 'Jaccard',
        'sokalsneath': 'Sokal & Sneath',
        'dice': 'Sørensen-Dice',
        'overlap': 'Overlap',
        'cosine': 'Cosine'
    })
    
    # Calculate global ranking
    all_vals = []
    for l in linkages:
        col = l.capitalize()
        all_vals.extend([x for x in df_results[col] if pd.notnull(x)])
    
    # Sort descending and get unique values for ranking
    all_vals = sorted(list(set(all_vals)), reverse=True)
    
    # Format table with 2 decimal places and rank
    for l in linkages:
        col = l.capitalize()
        formatted_col = []
        for val in df_results[col]:
            if pd.notnull(val):
                rank = all_vals.index(val) + 1
                formatted_col.append(f"{val:.2f} ({rank}º)")
            else:
                formatted_col.append("N/A")
        df_results[col] = formatted_col
        
    return df_results
def get_cargo_color_hex(cargo_name, cargos_destaque_list):
    """Retorna a cor associada ao cargo com base na paleta do grafo."""
    if cargos_destaque_list and cargo_name in cargos_destaque_list:
        import plotly.express as px
        palette = px.colors.qualitative.Bold
        return palette[cargos_destaque_list.index(cargo_name) % len(palette)]
    return None

def df_to_inline_html(df, row_style_func=None, col_style_func=None):
    """
    Gera uma tabela HTML com estilos INLINE, burlando a limpeza do DOMPurify.
    row_style_func(row) -> list of style strings for each cell
    col_style_func(val) -> style string for a single cell (used if row_style_func is None)
    """
    html = '<table class="light-table-container" style="width:100%; border-collapse: collapse; text-align:left; font-size: 14px; background-color: #FFFFFF;">'
    html += '<thead style="background-color: #F0F2F6; color: #1E2329;"><tr style="border-bottom: 1px solid #CED4DA;">'
    
    if df.index.name:
        html += f'<th style="padding: 8px; border: 1px solid #CED4DA;">{df.index.name}</th>'
    else:
        html += '<th style="padding: 8px; border: 1px solid #CED4DA;"></th>'
        
    for c in df.columns:
        html += f'<th style="padding: 8px; border: 1px solid #CED4DA;">{c}</th>'
    html += '</tr></thead><tbody>'
    
    for idx, row in df.iterrows():
        styles = []
        if row_style_func:
            styles = row_style_func(row)
        else:
            styles = [col_style_func(row[c]) if col_style_func else '' for c in df.columns]
            
        html += '<tr style="border-bottom: 1px solid #EEE; color: #1E2329;">'
        html += f'<td style="padding: 8px; border: 1px solid #CED4DA; background-color: #FFFFFF;"><b>{idx}</b></td>'
        
        for i, col in enumerate(df.columns):
            val = row[col]
            style_str = styles[i] if i < len(styles) else ''
            
            # Garante background branco se não houver estilo de cor
            if "background-color" not in style_str:
                style_str += " background-color: #FFFFFF;"
                
            html += f'<td style="padding: 8px; border: 1px solid #CED4DA; {style_str}">{val}</td>'
        html += '</tr>'
        
    html += '</tbody></table>'
    return html
