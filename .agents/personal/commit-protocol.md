# Protocolo Pré-Commit

Antes de realizar qualquer commit, o sistema/desenvolvedor deve obrigatoriamente seguir este checklist, nesta ordem:

1. **Revisão e Refatoração (Clean Code):** Revise o código que foi alterado. Garanta que ele está enxuto, eficiente, legível e seguro. Remova códigos mortos, variáveis não utilizadas e *logs* temporários de debug (ex: `console.log`, `print`).

1.5. **Inclusão de Arquivos Novos (Untracked Files):** Sempre verifique a existência de arquivos não rastreados com `git status`. Se houver arquivos novos que compõem o escopo do repositório (ex: novas imagens, scripts definitivos, assets), inclua-os explicitamente com `git add <arquivo>`. Não deixe arquivos cruciais esquecidos.

2. **Prevenção contra Vazamento de Dados (Secrets & PII):** Verifique rigorosamente se as alterações contêm chaves de API, senhas, tokens ou dados pessoais (PII) sensíveis. Qualquer dado desse tipo deve ser removido do código-fonte e tratado via variáveis de ambiente (`.env`).

3. **Análise de Segurança:** Avalie as mudanças em busca de vulnerabilidades comuns (ex: falta de validação de input, dependências inseguras). O código a ser salvo não pode introduzir novos riscos ao sistema.

1. **Cobertura e Execução de Testes:**
   Como estamos usando **Docker**, caso hajam testes automatizados (ex: `pytest`), você deve rodá-los dentro do container antes de commitar:
   ```bash
   docker compose exec app pytest
   ```

5. **Atualização da Documentação:** Atualize o `CHANGELOG.md` descrevendo claramente o que foi alterado. Revise o `README.md` e atualize-o caso a mudança impacte a forma de instalar, rodar ou usar o projeto.

6. **Padronização do Commit (Conventional Commits) via Docker:** 
   Se você quiser garantir que as validações do `pre-commit` (Bandit, Commitizen, etc.) sejam feitas usando o ambiente do Docker (caso você não tenha o Python configurado nativamente no Windows), você pode abrir o terminal interativo do container para realizar o commit de lá de dentro:
   ```bash
   # Entra no terminal interativo do container
   docker compose exec app bash
   
   # Lá dentro, faça seu commit (o pre-commit já estará instalado)
   git add .
   cz commit
   ```
   *Nota: Se você já instalou o pre-commit nativamente no Windows com `pip install pre-commit`, pode apenas continuar fazendo `git commit` ou `cz commit` normalmente pelo terminal do Windows.*
