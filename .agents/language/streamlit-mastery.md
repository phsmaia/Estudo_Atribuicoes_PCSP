# Domínio do Streamlit

## Princípios
- **Separação de Preocupações:** Mantenha a lógica de processamento de dados separada da lógica de renderização da interface. Não processe dataframes enormes diretamente dentro de um `st.write` ou componente de UI.
- **Gerenciamento de Estado:** Use `st.session_state` adequadamente para gerenciar interações, seleções e configurações do usuário que devem persistir entre reexecuções.
- **Desempenho & Caching:** 
  - Use `@st.cache_data` para funções que carregam dados ou fazem cálculos pesados do pandas.
  - Use `@st.cache_resource` para conexões de banco de dados ou modelos de machine learning.
- **Responsividade:** Certifique-se de que o dashboard usa elementos de layout de forma eficaz (`st.columns`, `st.container`, `st.expander`) para permanecer legível em diferentes tamanhos de tela.
- **Reexecuções Limpas:** Garanta que as interações não causem reexecuções desnecessárias ou custosas.

## Melhores Práticas
- Nunca mude objetos em cache diretamente; retorne uma cópia se a mutação for necessária ou use os parâmetros `ttl` / `max_entries`.
- Forneça indicadores de carregamento (`st.spinner`) para processos demorados para melhorar a experiência do usuário.
