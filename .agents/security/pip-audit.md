# Auditoria de Dependências com pip-audit
- Use pip-audit para verificar vulnerabilidades conhecidas (CVEs) nas dependências do projeto.
- Se o pip-audit sinalizar uma vulnerabilidade, atualize imediatamente o pacote problemático no `requirements.txt` para a versão corrigida.
- Evite fixar dependências em versões vulneráveis, a menos que haja uma exceção estritamente documentada e gerenciada.
- Execute `pip-audit` regularmente tanto no `requirements.txt` quanto no `requirements-dev.txt`.
