# Python Testing Patterns

Esta regra define os padrões e as melhores práticas para a escrita de testes no projeto, garantindo confiabilidade, consistência e alinhamento com a nossa depuração sistemática.

## Ferramentas Principais
- Use **pytest** como o framework principal de testes.
- Use **pytest-mock** (wrapper para `unittest.mock`) para criação de mocks estruturados.
- Use **pytest-cov** para monitorar a cobertura dos testes.

## Padrões de Organização (Arrange-Act-Assert)
Estruture todos os testes no padrão **AAA**:
- **Arrange (Preparar):** Configure os dados, mocks e dependências necessárias.
- **Act (Agir):** Execute o código que está sendo testado.
- **Assert (Afirmar):** Valide os resultados ou o estado gerado pela ação.

## Melhores Práticas
1. **Mocks e Isolamento:** Isole os testes unitários de dependências externas (como banco de dados, rede e sistema de arquivos) usando mocks apropriados.
2. **Uso de Fixtures:** Extraia lógicas comuns de setup/teardown para `fixtures` do pytest (geralmente localizadas em um arquivo `conftest.py`), para evitar duplicação de código.
3. **Parametrização:** Use `@pytest.mark.parametrize` para testar múltiplas entradas e saídas no mesmo cenário sem duplicar funções de teste.
4. **Nomes Descritivos:** Nomes de métodos de teste devem ser extremamente descritivos (ex: `test_calculate_total_with_valid_discount_returns_correct_value`).
5. **Teste de Exceções:** Sempre teste os caminhos de falha. Use `pytest.raises()` para verificar se as exceções corretas estão sendo lançadas com as mensagens esperadas.

## Relacionamento com Kaizen e Depuração
Qualquer nova funcionalidade ou correção de bug **deve** incluir testes automatizados. Ao corrigir um bug usando a depuração sistemática, escreva um teste que reproduza o problema (falhando com o bug presente) e passe após a correção.
