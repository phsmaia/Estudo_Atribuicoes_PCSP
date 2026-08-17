# Força reload 2
import pandas as pd
import streamlit as st
import os

@st.cache_data(show_spinner=False)
def load_csv_data(filepath: str) -> pd.DataFrame:
    """
    Carrega dados de um arquivo CSV, utilizando os padrões de encoding e separador do projeto.
    Utiliza cache do Streamlit para evitar re-leitura de disco em cada iteração.
    """
    if not os.path.exists(filepath):
        st.error(f"Arquivo não encontrado: {filepath}")
        return pd.DataFrame()
        
    try:
        try:
            df = pd.read_csv(filepath, encoding='utf-8-sig', sep=';')
        except UnicodeDecodeError:
            df = pd.read_csv(filepath, encoding='iso-8859-1', sep=';')
        
        # Mapeamento para indicar aos usuários a antiga nomenclatura das novas atribuições
        rename_map = {
            "Assessoramento Técnico Papiloscópico": "Assessoramento Técnico Papiloscópico (ℹ️ Antiga perícia papiloscópica de local)",
            "Suporte a desastres": "Suporte a desastres (ℹ️ Antiga perícia papiloscópica em desastres)",
            "Edição de relatórios de assessoramento e exame papiloscópicos não periciais": "Edição de relatórios papiloscópicos (ℹ️ Antigos laudos periciais papiloscópicos)"
        }
        df = df.rename(columns=rename_map)
        
        return df
    except Exception as e:
        st.error(f"Erro ao ler o arquivo {filepath}: {e}")
        return pd.DataFrame()

@st.cache_data(show_spinner=False)
def get_all_datasets(base_dir: str = ".") -> dict:
    """
    Carrega os principais datasets mapeados no projeto.
    Retorna um dicionário com os DataFrames.
    """
    datasets = {
        "editais": load_csv_data(os.path.join(base_dir, "Atribuicoes_Carreiras_Editais.CSV")),
        "atual_sem_correcao": load_csv_data(os.path.join(base_dir, "01 - Atrib Atual No Cor.CSV")),
        "atual_com_correcao": load_csv_data(os.path.join(base_dir, "02 - Atrib Atual With Cor.CSV")),
        "lonpc_sem_correcao": load_csv_data(os.path.join(base_dir, "03 - Atrib LONPC No Cor.CSV")),
        "lonpc_com_correcao": load_csv_data(os.path.join(base_dir, "04 - Atrib LONPC With Cor.CSV")),
        "reestruturacao_papis_nao_peritos": load_csv_data(os.path.join(base_dir, "05 - Atrib 2024 Grupo Estudo PCSP Papis nao peritos.CSV")),
        "reestruturacao_papis_peritos": load_csv_data(os.path.join(base_dir, "06 - Atrib 2024 Grupo Estudo PCSP Papi como peritos.CSV")),
        "rest_2025_gov_r1_papis_nao_peritos": load_csv_data(os.path.join(base_dir, "07 - Atrib Rest 2025 Gov R1 Papis nao peritos.csv")),
        "rest_2025_gov_r1_papis_peritos": load_csv_data(os.path.join(base_dir, "08 - Atrib Rest 2025 Gov R1 Papis como peritos.CSV")),
        "rest_2025_gov_r2_papis_nao_peritos": load_csv_data(os.path.join(base_dir, "09 - Atrib Rest 2025 Gov R2 Papis nao peritos.CSV")),
        "rest_2025_gov_r2_papis_peritos": load_csv_data(os.path.join(base_dir, "10 - Atrib Rest 2025 Gov R2 Papis como peritos.CSV")),
        "decreto_1967_dgp_2012": load_csv_data(os.path.join(base_dir, "11 - Atrib Decreto 47788-1967 original e DGP 30-2012.CSV")),
        "decreto_1967_com_correcao": load_csv_data(os.path.join(base_dir, "12 - Atrib Decreto 47788-1967 com correcoes e DGP 30-2012.CSV"))
    }
    return datasets
