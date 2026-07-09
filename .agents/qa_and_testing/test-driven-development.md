# Test-Driven Development (TDD)

Esta regra dita o ciclo de vida da escrita de código no projeto, garantindo que o comportamento esperado seja definido antes da implementação.

## O Ciclo Red-Green-Refactor
1. **Red:** Escreva um teste que falhe (usando as diretrizes de `python-testing-patterns.md`).
2. **Green:** Escreva o código mínimo necessário para o teste passar.
3. **Refactor:** Limpe o código, removendo duplicações (aplicando o `kaizen.md`).

## Integração Orgânica
- **Com a Depuração Sistemática (`systematic-debugging.md`):** Quando um bug for encontrado, a primeira etapa do TDD ("Red") é obrigatoriamente a escrita de um teste que reproduza esse bug. Nunca altere o código de produção antes do teste do bug falhar.
