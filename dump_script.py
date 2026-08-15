import pandas as pd
df = pd.read_csv(r'c:\Users\maiap\OneDrive\Desktop\Desenvolvimento\Estudo_Atribuicoes_PCSP\05 - Atrib 2024 Grupo Estudo PCSP Papis nao peritos.CSV', encoding='iso-8859-1', sep=';')
with open(r'c:\Users\maiap\OneDrive\Desktop\Desenvolvimento\Estudo_Atribuicoes_PCSP_2024\cargos.txt', 'w') as f:
    f.write(str(df['Carreira'].tolist() if 'Carreira' in df.columns else df.iloc[:,0].tolist()))
