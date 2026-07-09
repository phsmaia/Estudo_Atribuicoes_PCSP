# Gráficos Interativos (Plotly/Altair)

## Princípios
- **Consistência Visual:** Mantenha uma paleta de cores consistente em todas as visualizações no dashboard. Use cores que correspondam ao tema do aplicativo e evite combinações agressivas ou difíceis de ler.
- **Clareza em vez de Complexidade:** Mantenha as visualizações limpas. Não sobrecarregue um único gráfico com muitas dimensões. Se ficar muito complexo, divida-o em vários gráficos.
- **Tooltips Informativos:** Gráficos interativos devem fornecer tooltips claros e concisos. Evite despejar JSON puro ou números não formatados; formate moedas, porcentagens e datas de maneira agradável.
- **Responsividade:** Garanta que os gráficos sejam redimensionados corretamente dentro do layout do Streamlit sem causar rolagem horizontal, a menos que seja explicitamente intencional.

## Melhores Práticas
- Forneça títulos e rótulos de eixos para cada gráfico.
- Garanta que as legendas sejam visíveis e posicionadas corretamente sem sobrepor os dados.
- Otimize as funções de plotagem para não bloquear a thread principal da interface com cálculos pesados; faça os cálculos previamente no Pandas.
