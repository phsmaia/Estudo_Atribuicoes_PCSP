# Padrões para Jupyter Notebook

## Princípios
- **Reprodutibilidade:** Um notebook deve executar de cima para baixo sem erros. Evite dependências de execução fora de ordem.
- **Documentação Clara:** Use células Markdown para explicar o "porquê", não apenas o "como". Documente as fontes de dados, suposições e conclusões para cada seção.
- **Commits Limpos:** Limpe todas as saídas antes de commitar para o controle de versão, a menos que a saída seja explicitamente necessária para fins de demonstração. Saídas enormes (como conjuntos de dados inline ou gráficos interativos grandes) incham o repositório git.
- **Modularidade do Código:** Se um bloco de código em um notebook se tornar muito grande ou for reutilizado frequentemente, refatore-o em um script Python separado (ex: `processamento_dados.py`) e importe-o.

## Melhores Práticas
- Use uma convenção de nomenclatura consistente para os notebooks (ex: `01-limpeza-de-dados.ipynb`).
- Mantenha o número de importações no topo do notebook.
- Use declarações `assert` ou verificações básicas para garantir a integridade dos dados durante a análise exploratória.
