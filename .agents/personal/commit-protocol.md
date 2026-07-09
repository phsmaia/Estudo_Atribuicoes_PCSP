# Protocolo Pré-Commit

Antes de realizar qualquer commit, o sistema/desenvolvedor deve obrigatoriamente seguir este checklist, nesta ordem:

1. **Revisão e Refatoração (Clean Code):** Revise o código que foi alterado. Garanta que ele está enxuto, eficiente, legível e seguro. Remova códigos mortos, variáveis não utilizadas e *logs* temporários de debug (ex: `console.log`, `print`).

2. **Prevenção contra Vazamento de Dados (Secrets & PII):** Verifique rigorosamente se as alterações contêm chaves de API, senhas, tokens ou dados pessoais (PII) sensíveis. Qualquer dado desse tipo deve ser removido do código-fonte e tratado via variáveis de ambiente (`.env`).

3. **Análise de Segurança:** Avalie as mudanças em busca de vulnerabilidades comuns (ex: falta de validação de input, dependências inseguras). O código a ser salvo não pode introduzir novos riscos ao sistema.

4. **Cobertura e Execução de Testes:** Avalie a necessidade de criar novos testes unitários ou de integração para o código alterado/criado e implemente-os (eles devem ser adições permanentes). Em seguida, execute toda a suíte de testes para garantir que nenhuma funcionalidade anterior foi quebrada.

5. **Atualização da Documentação:** Atualize o `CHANGELOG.md` descrevendo claramente o que foi alterado. Revise o `README.md` e atualize-o caso a mudança impacte a forma de instalar, rodar ou usar o projeto.

6. **Padronização do Commit (Conventional Commits):** Realize o commit seguindo as regras internacionais do *Conventional Commits* (usando prefixos como `feat:`, `fix:`, `refactor:`, `docs:`). O título deve ser claro e direto. O corpo do commit deve conter comentários relevantes que expliquem o *porquê* da mudança, agregando valor histórico ao projeto.
