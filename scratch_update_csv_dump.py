import pandas as pd
import json

def main():
    df = pd.read_csv('Tabela_Conversao_Cargos.CSV', sep=';', encoding='iso-8859-1')
    
    # We want to map it to JSON for easy loading in JS or Python.
    records = df.to_dict(orient='records')
    
    with open('csv_dump.json', 'w', encoding='utf-8') as f:
        json.dump(records, f, indent=4, ensure_ascii=False)
        
    print("csv_dump.json updated!")

if __name__ == '__main__':
    main()
