# Registro de Auditoria de Segurança
- Use o módulo embutido `logging` do Python para manter um rastro de auditoria de eventos de segurança críticos (logins, acesso a dados sensíveis, erros, etc.).
- Os logs devem ser estruturados (ex: formato JSON quando possível ou texto claramente analisável) contendo timestamp, usuário/ator, ação e resultado.
- Nunca registre senhas puras, números completos de cartão de crédito ou PII desprotegida. Mascare dados sensíveis antes de passá-los para o logger.
- Defina os níveis de log apropriados: `INFO` para eventos de auditoria de rotina, `WARNING` para atividades suspeitas e `ERROR` ou `CRITICAL` para falhas de segurança ou crashes.
