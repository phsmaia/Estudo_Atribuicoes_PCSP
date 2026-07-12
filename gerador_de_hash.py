import bcrypt
import getpass

print("\n" + "="*50)
print("🔐 GERADOR DE HASH PARA O PAINEL DE ADMINISTRAÇÃO")
print("="*50 + "\n")

# getpass permite digitar a senha sem mostrá-la na tela
senha = getpass.getpass("Digite a senha desejada (ela não aparecerá na tela enquanto você digita): ")

if not senha.strip():
    print("❌ Erro: A senha não pode ser vazia.")
else:
    hash_senha = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    print("\n✅ Hash gerado com sucesso!\n")
    print("Copie a linha abaixo EXATAMENTE como está e substitua no seu arquivo .streamlit/secrets.toml:\n")
    print(f'ADMIN_PASSWORD_HASH = "{hash_senha}"\n')
