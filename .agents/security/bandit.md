# SAST com Bandit
- Use Bandit para varrer o código Python em busca de vulnerabilidades de segurança comuns (ex: injeções SQL, credenciais hardcoded, algoritmos criptográficos inseguros).
- Quando um erro do Bandit for reportado, não o ignore. Refatore o código para eliminar a vulnerabilidade.
- Use apenas `# nosec` se tiver certeza absoluta de que é um falso positivo e documente adequadamente o motivo.
- Garanta que todas as consultas a banco de dados utilizem parâmetros parametrizados via SQLAlchemy para prevenir injeção SQL.
- Garanta o uso seguro de módulos criptográficos.
