import pandas as pd
import data_loader

datasets = data_loader.get_all_datasets('.')
df_1967 = datasets['decreto_1967_dgp_2012']
print(df_1967['Carreira'].tolist())
