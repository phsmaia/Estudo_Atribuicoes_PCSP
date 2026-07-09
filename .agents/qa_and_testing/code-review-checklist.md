# Code Review Checklist

Esta regra atua como a barreira de qualidade final antes de qualquer alteração ser integrada à branch principal (main/master).

## Checklist Obrigatório
Antes de aprovar um Merge Request ou finalizar um desenvolvimento, valide:
- [ ] O código segue o **Protocolo de Commit** (`commit-protocol.md`)?
- [ ] O código possui testes automatizados que cobrem os caminhos felizes e de erro (`python-testing-patterns.md`)?
- [ ] Não há vazamento de dados ou falhas apontadas pelas ferramentas de segurança (`bandit.md`, `gitleaks.md`)?
- [ ] A documentação e o README foram atualizados (`technical-writing.md`)?

## Sinergia
- Esta checklist é a materialização do **Kaizen**. Ela garante que nenhuma alteração piore a base de código, forçando a melhoria contínua através de revisão rigorosa.
