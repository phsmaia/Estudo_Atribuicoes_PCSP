import pandas as pd
df_1967 = pd.read_csv("11 - Atrib Decreto 47788-1967 original e DGP 30-2012.CSV", sep=';', encoding='iso-8859-1')
print("1967 columns:", len(df_1967.columns))

df_base = pd.read_csv("01 - Atrib Atual No Cor.CSV", sep=';', encoding='iso-8859-1')
df_base = df_base[df_base['Carreira'].isin(["Perito Criminal", "Papiloscopista Policial"])]
print("Base columns:", len(df_base.columns))

df_combined = df_base.copy()
mapping = {"Perito Criminal": "Perito Criminal", "Papiloscopista Policial": "Pesquisador Datiloscópico"}

for idx, row in df_combined.iterrows():
    carreira_1967 = mapping.get(row['Carreira'])
    if carreira_1967:
        safe_map = {"Pesquisador Datiloscópico": "Pesquisador", "Perito Criminal": "Perito Criminal"}
        safe_term = safe_map.get(carreira_1967, carreira_1967)
        matches = df_1967[df_1967['Carreira'].str.contains(safe_term, na=False, case=False)]
        
        if not matches.empty:
            row_1967 = matches.iloc[0]
            for col in df_1967.columns:
                if col != 'Carreira' and row_1967.get(col, 0) == 1:
                    if col not in df_combined.columns:
                        df_combined[col] = 0
                    df_combined.at[idx, col] = 1

print("Combined columns:", len(df_combined.columns))
print("Combined shape:", df_combined.shape)
print("Are 1967 columns all zeros in df_combined?", df_combined.iloc[:, 30:].eq(0).all().all())
