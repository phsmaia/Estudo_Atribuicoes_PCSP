# Postmortem Writing

A redação de um *Postmortem* (Documento de Pós-Morte) é um passo obrigatório dentro da nossa cultura de Kaizen e Depuração Sistemática após a resolução de qualquer bug crítico ou incidente em produção no projeto.

## Cultura "Blameless"
Os documentos de postmortem devem possuir um tom estrito **sem culpa (Blameless)**. O objetivo é consertar o processo e o sistema, não apontar falhas individuais. Assuma sempre que um erro humano decorreu de um erro no design ou no ferramental do sistema.

## Estrutura Obrigatória do Documento
Sempre que um incidente crítico for solucionado, um resumo deve ser produzido com os seguintes tópicos:
1. **Impacto:** O que parou de funcionar e por qual período de tempo?
2. **Causa Raiz:** O que causou a quebra tecnicamente? (Use as evidências colhidas pela depuração sistemática).
3. **Detecção:** Como o erro foi descoberto? Nossos logs estruturados e alertas do rastreamento de erros (Sentry) avisaram com antecedência, ou dependemos de reclamação manual?
4. **Resolução:** O que foi feito de imediato para restaurar o fluxo?
5. **Ação Preventiva (Kaizen):** Quais refatorações de código, testes (Python Testing Patterns) automatizados, ou ajustes de infraestrutura foram criados para impedir matematicamente a reincidência do problema?
