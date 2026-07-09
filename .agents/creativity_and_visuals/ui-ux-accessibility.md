# UI/UX Accessibility

Esta regra garante que o projeto seja utilizável por todas as pessoas, aderindo a padrões globais de acessibilidade, demonstrando maturidade técnica para recrutadores.

## Diretrizes Rigorosas
- **Contraste:** Siga as diretrizes WCAG AA para contraste de texto e fundo (mínimo de 4.5:1 para texto normal).
- **Navegação por Teclado:** Toda a interface deve ser 100% navegável usando apenas a tecla `Tab` e `Enter`. O foco (`:focus`) deve ser visível.
- **Leitores de Tela:** Utilize tags HTML5 semânticas (`<nav>`, `<main>`, `<article>`) e atributos ARIA quando componentes customizados não possuírem semântica nativa.

## Sinergia e Conflitos
- **Resolução:** Esta regra atua como um limite estrito sobre as regras de `frontend-design.md` e `algorithmic-art.md`. A estética nunca deve sacrificar a acessibilidade.
