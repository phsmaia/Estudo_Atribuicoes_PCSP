# Verificação de Segredos com Gitleaks
- Use Gitleaks (via pre-commit) para detectar chaves de API, senhas e tokens comitados acidentalmente.
- Nunca faça commit de segredos hardcoded para o repositório.
- Se o Gitleaks bloquear um commit, remova o segredo do código e carregue-o de variáveis de ambiente usando `python-dotenv`.
- Caso um segredo real seja comitado, considere-o comprometido e rotacione-o imediatamente.
