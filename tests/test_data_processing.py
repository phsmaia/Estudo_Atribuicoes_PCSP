import pytest
import pandas as pd
import numpy as np
from data_processing import remover_atribuicoes_comuns, condensar_dataframe, gerar_matriz_adjacencia, calcular_distancias

def test_remover_atribuicoes_comuns():
    # Setup
    df = pd.DataFrame({
        'Atr_1': [1, 1, 1],
        'Atr_2': [1, 0, 1],
        'Atr_3': [0, 0, 0],
        'Atr_4': [1, 1, 1]
    }, index=['Cargo A', 'Cargo B', 'Cargo C'])
    
    # Exec
    df_result = remover_atribuicoes_comuns(df)
    
    # Assert
    # Atr_1 and Atr_4 should be removed because they are all 1s
    assert 'Atr_1' not in df_result.columns
    assert 'Atr_4' not in df_result.columns
    assert 'Atr_2' in df_result.columns
    assert 'Atr_3' in df_result.columns

def test_condensar_dataframe():
    # Setup
    df = pd.DataFrame({
        'Atr_1': [1, 0, 1],
        'Atr_2': [1, 0, 1], # Identical to Atr_1
        'Atr_3': [0, 1, 0]
    }, index=['Cargo A', 'Cargo B', 'Cargo C'])
    
    # Exec
    df_condensed, historico = condensar_dataframe(df)
    
    # Assert
    assert 'Atr_1 / Atr_2' in df_condensed.columns
    assert 'Atr_3' in df_condensed.columns
    assert 'Atr_1' not in df_condensed.columns
    assert 'Atr_2' not in df_condensed.columns
    assert len(historico) == 1
    assert "Redução Nº 1" in historico[0]

def test_gerar_matriz_adjacencia():
    # Setup
    df = pd.DataFrame({
        'Atr_1': [1, 1, 0],
        'Atr_2': [1, 0, 0],
        'Atr_3': [0, 1, 1]
    }, index=['Cargo A', 'Cargo B', 'Cargo C'])
    
    # Exec
    adj = gerar_matriz_adjacencia(df)
    
    # Assert
    # Cargo A tem Atr_1, Atr_2 -> soma = 2
    assert adj.loc['Cargo A', 'Cargo A'] == 2
    # Cargo B tem Atr_1, Atr_3 -> soma = 2
    assert adj.loc['Cargo B', 'Cargo B'] == 2
    # Cargo C tem Atr_3 -> soma = 1
    assert adj.loc['Cargo C', 'Cargo C'] == 1
    
    # A interseciona B em Atr_1 -> 1
    assert adj.loc['Cargo A', 'Cargo B'] == 1
    # B interseciona C em Atr_3 -> 1
    assert adj.loc['Cargo B', 'Cargo C'] == 1
    # A e C não intersecionam -> 0
    assert adj.loc['Cargo A', 'Cargo C'] == 0

def test_calcular_distancias():
    # Setup
    df = pd.DataFrame({
        'Atr_1': [1, 1, 0],
        'Atr_2': [1, 0, 0],
        'Atr_3': [0, 1, 1]
    }, index=['Cargo A', 'Cargo B', 'Cargo C'])
    
    # Exec
    dist = calcular_distancias(df, metric='jaccard')
    
    # Assert
    # Diagonal should be 0
    assert np.isclose(dist.loc['Cargo A', 'Cargo A'], 0.0)
    # Symmetry
    assert np.isclose(dist.loc['Cargo A', 'Cargo B'], dist.loc['Cargo B', 'Cargo A'])
    # Valid bounds
    assert (dist.values >= 0).all()
    assert (dist.values <= 1).all()
