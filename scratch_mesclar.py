import pandas as pd
import sys
sys.path.append('c:\\Users\\maiap\\OneDrive\\Desktop\\Desenvolvimento\\Estudo_Atribuicoes_PCSP')
import data_loader
import data_processing

datasets = data_loader.get_all_datasets()
df_cenario = datasets["original_clean"]
df_conv = datasets["tabela_conversao"]

filtro_cargos = ["Perito Criminal", "Papiloscopista Policial"]
if 'Carreira' in df_cenario.columns:
    df_cenario = df_cenario[df_cenario['Carreira'].isin(filtro_cargos)]
else:
    df_cenario = df_cenario.loc[filtro_cargos]

print("Columns before:", df_cenario.shape[1])

# Mesclagem da Camada Histórica (Decreto 1967)
df_cenario = data_processing.mesclar_com_1967(df_cenario, "Original", datasets["decreto_1967_dgp_2012"], df_conv)

print("Columns after:", df_cenario.shape[1])
print("Sample columns added:", [c for c in df_cenario.columns if c not in datasets["original_clean"].columns][:5])
