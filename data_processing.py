import pandas as pd
import streamlit as st

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
from scipy.spatial.distance import squareform
from scipy.cluster.hierarchy import linkage

@st.cache_data(show_spinner=False)
def calcular_distancias_gower(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula a matriz de distâncias usando o algoritmo de Gower.
    """
    df_temp = df.copy()
    if 'Carreira' in df_temp.columns:
        df_temp = df_temp.set_index('Carreira')
    df_temp = df_temp.apply(pd.to_numeric, errors='coerce').fillna(0)
    
    # Cast explícito para float para evitar UFuncOutputCastingError do Numpy 2.0 no Gower
    df_temp = df_temp.astype(float)
    
    # A matriz de Gower retorna distâncias (0 = idêntico, 1 = dissimilar)
    dist_matrix = gower.gower_matrix(df_temp)
    
    # Converte em dataframe para facilidade
    df_gower = pd.DataFrame(dist_matrix, index=df_temp.index, columns=df_temp.index)
    return df_gower
