# Python Observability

Esta regra estabelece o padrão de instrumentação do código para garantirmos visibilidade e rastreabilidade total no projeto, suportando ativamente a nossa depuração sistemática.

## 1. Logs Estruturados
Substitua o uso de `print()` ou o módulo `logging` padrão por bibliotecas modernas focadas em **Structured Logging**, como **`structlog`** ou **`loguru`**.
- **Formato:** Em ambientes de produção/servidor, o output dos logs deve ser obrigatoriamente formatado em **JSON**, garantindo conformidade com a regra de Security Audit Logging.
- **Contexto:** Adicione contexto aos logs utilizando IDs de correlação (ex: UUID por requisição/tarefa) para que um fluxo possa ser traçado do começo ao fim.

## 2. Rastreamento de Erros (Error Tracking)
O projeto deve utilizar ferramentas de rastreamento de exceções, como o **Sentry** (através do pacote `sentry-sdk`).
- **Captura Automática:** Certifique-se de que a biblioteca esteja configurada no *entrypoint* da aplicação para capturar `Unhandled Exceptions` (exceções não tratadas).
- **Riqueza de Detalhes:** Ao logar erros estruturados, garanta que o contexto de *stack trace*, variáveis de ambiente e estado atual (informações do usuário ou da transação) sejam anexados. Isso remove o "achismo" durante a depuração sistemática.
