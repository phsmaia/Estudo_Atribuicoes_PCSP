import sqlite3

try:
    conn = sqlite3.connect("c:\\Users\\maiap\\OneDrive\\Desktop\\Desenvolvimento\\Estudo_Atribuicoes_PCSP\\app_data.db")
    cursor = conn.cursor()
    cursor.execute("ALTER TABLE comments ADD COLUMN language VARCHAR(10) DEFAULT 'PT-BR'")
    conn.commit()
    print("Coluna 'language' adicionada com sucesso.")
except sqlite3.OperationalError as e:
    print(f"Erro (talvez a coluna já exista): {e}")
finally:
    conn.close()
