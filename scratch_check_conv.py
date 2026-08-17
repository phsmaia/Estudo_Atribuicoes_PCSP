import pandas as pd
import os
os.chdir('c:\\Users\\maiap\\OneDrive\\Desktop\\Desenvolvimento\\Estudo_Atribuicoes_PCSP')
import data_loader
import data_processing

datasets = data_loader.get_all_datasets()
df_conv = datasets["tabela_conversao"]
print("Colunas de df_conv:", df_conv.columns.tolist())

col_map = {
    "Atual Sem Correção": "Atual Sem Correção",
    "Atual Com Correção": "Atual Com Correção"
}
col_name = col_map.get("Atual Sem Correção")
print("col_name:", col_name)

if col_name and col_name in df_conv.columns:
    try:
        conv_clean = df_conv.dropna(subset=[col_name, 'Decreto 47788 / 1967'])
        mapping = dict(zip(conv_clean[col_name], conv_clean['Decreto 47788 / 1967']))
        print("Mapeamento gerado com sucesso! Tamanho:", len(mapping))
        print("Mapeamento para Perito Criminal:", mapping.get('Perito Criminal'))
        print("Mapeamento para Papiloscopista Policial:", mapping.get('Papiloscopista Policial'))
    except Exception as e:
        print("ERRO:", e)
else:
    print("Coluna não encontrada!")

# Teste com o dataset 1967
df_1967 = datasets["decreto_1967_dgp_2012"]
print("Colunas 1967 (primeiras 5):", df_1967.columns.tolist()[:5])

# Tentando achar Perito Criminal no df_1967
print("Tem Perito Criminal no 1967?", df_1967[df_1967['Carreira'] == 'Perito Criminal'].empty == False)
