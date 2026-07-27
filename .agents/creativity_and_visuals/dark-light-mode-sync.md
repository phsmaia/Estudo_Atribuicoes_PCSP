# Sincronização de Modos Dark e Light

## Princípios
- **Implementação Obrigatória em Modo Duplo:** Toda vez que uma nova funcionalidade, tabela, gráfico ou elemento de interface for adicionado ou modificado, ele DEVE ser explicitamente testado e estilizado tanto para o Modo Dark quanto para o Modo Light.
- **Consistência Visual:** Garanta que as paletas de cores, as taxas de contraste e a identidade visual (como cores específicas atribuídas a cargos ou categorias) permaneçam harmonizadas em ambos os modos. Evite depender do tema automático padrão do Streamlit sem verificação.
- **Estilos Inline e CSS:** Ao usar estilos inline (ex: `span style='color: ...'`) ou ao injetar CSS global com `!important`, sempre verifique se essas regras não quebram a legibilidade no modo oposto.
- **Contraste de Fundo:** Se cores vivas/neon forem usadas para gráficos no Modo Dark, forneça um fundo suave (ex: `rgba(..., 0.15)`) estilo *badge* (etiqueta) ao renderizá-las sobre fundos brancos no Modo Light para preservar a legibilidade.
