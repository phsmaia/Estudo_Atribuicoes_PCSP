# Pandas & Processamento de Dados Pro

## Princípios
- **Vetorização Primeiro:** Sempre prefira operações vetorizadas sobre loops iterativos (ex: `iterrows`, `apply`). Loops no Pandas são lentos e não otimizados.
- **Eficiência de Memória:** Use dtypes apropriados. Reduza tipos numéricos quando possível, e use tipos `category` para colunas com baixa cardinalidade.
- **Tratamento de Dados Ausentes:** Seja explícito sobre o tratamento de valores NaN. Use `fillna()` ou `dropna()` com base na lógica do domínio, e documente claramente o motivo pelo qual uma certa abordagem foi adotada.
- **Encadeamento:** Use encadeamento de métodos onde torna o código mais legível (ex: usando `pipe()`, `assign()`), mas evite cadeias excessivamente longas que dificultem a depuração.
- **Imutabilidade:** Evite `inplace=True`. Raramente fornece benefícios de desempenho e frequentemente leva a um código confuso. Reatribua as variáveis em vez disso.

## Melhores Práticas
- Ao filtrar dataframes para o Streamlit, certifique-se de que as visualizações filtradas sejam criadas eficientemente para garantir atualizações rápidas na interface.
- Use nomes explícitos de colunas em vez de posições de índice.
