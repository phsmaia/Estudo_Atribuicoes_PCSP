# Continuous Integration (CI)

Esta regra garante que a execução das validações não dependa da memória humana, automatizando o controle de qualidade.

## Automação Obrigatória
- Configure uma pipeline de CI (ex: GitHub Actions) que rode automaticamente a cada *push* ou *Pull Request*.
- **A pipeline deve executar obrigatoriamente:**
  1. O *linter* e formatadores (`lint-and-validate.md`).
  2. A suíte de testes do Pytest (`python-testing-patterns.md`).
  3. As varreduras de segurança estática: `bandit` e `gitleaks` (da nossa seção de Segurança).
  4. A auditoria de dependências com `pip-audit`.

## Falha Zero
- Nenhum código pode ser integrado se a pipeline de CI falhar. A CI é o juiz final da estabilidade do Poirot.
