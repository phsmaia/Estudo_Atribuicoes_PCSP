# Mobile Design (Mobile First)

Esta regra garante que a experiência do usuário em dispositivos móveis seja tão premium e funcional quanto no desktop, evitando o "encolhimento preguiçoso" de interfaces.

## Práticas Obrigatórias
- **Touch Targets:** Todos os elementos clicáveis (botões, links, ícones) devem ter um tamanho mínimo de *44x44 pixels* para garantir toques precisos sem frustração.
- **Hierarquia Visual:** Em telas menores, o conteúdo mais importante deve estar no topo. Abandone sidebars complexas em favor de menus *Off-canvas* ou *Bottom navigation*.
- **Sem Hover:** Dispositivos móveis não possuem `:hover`. Qualquer informação crucial revelada por hover no desktop deve estar visível ou acessível por um toque simples no mobile.

## Integração Orgânica
- Expande o escopo do **`frontend-design.md`**, garantindo que a estética "Wow" sobreviva em telas pequenas. Age em conjunto com **`ui-ux-accessibility.md`** (tamanhos de toque são um padrão de acessibilidade física).
