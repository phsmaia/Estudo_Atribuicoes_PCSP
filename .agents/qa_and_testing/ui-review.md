# UI Review

Esta regra cria um processo formal de QA visual, assegurando que o código do front-end entregue o que o design prometeu, sem regressões estéticas.

## Checklist Visual
Antes de aprovar alterações na interface, audite visualmente:
- **Pixel Perfection:** Os espaçamentos, margens e alinhamentos estão consistentes com o sistema de design estabelecido?
- **Cross-Browser:** A interface funciona uniformemente nos principais motores (Chromium, WebKit/Safari, Firefox)?
- **Responsividade Real:** O layout se adapta perfeitamente do smartphone (320px) ao monitor Ultrawide sem quebrar, sobrepor textos ou estourar a largura da página?

## Integração Orgânica
- Funciona como a "irmã" da nossa **`code-review-checklist.md`**. Enquanto o code review olha para segurança (`bandit`), testes (`TDD`) e backend, a `ui-review` age como a última barreira de defesa do **`frontend-design.md`** e do **`mobile-design.md`** antes de ir para produção.
