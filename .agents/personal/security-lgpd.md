# Segurança e LGPD

## Privacidade e Coleta de Dados Primordial
Para este e quaisquer outros projetos desenvolvidos no ecossistema:

1. **Anonimização e Pseudonimização (LGPD)**:
   - Jamais armazene IPs de usuários em texto limpo de forma persistente, a não ser que haja um tempo de expiração curto (ex: purga diária) ou base legal explícita.
   - Utilize a abordagem de Hashing (`hashlib.sha256`) combinando IP + User-Agent + Salt Diário para criar um `user_hash` (Sessão), que perde a rastreabilidade exata do indivíduo mas permite continuidade analítica sem expor PII (Personally Identifiable Information).
   - Os logs de banco de dados não devem coletar dados pessoais diretos sem consentimento (opt-in explícito).

2. **Segurança de Painéis de Controle (Admin)**:
   - Nunca hardcode senhas no código fonte. 
   - Painéis administrativos isolados devem validar autenticação via *hashes criptográficos* (`bcrypt` ou `argon2`), comparando o input do usuário com o hash salvo em variáveis de ambiente ou `secrets.toml`.
   - Gerencie o estado de login através do `st.session_state` e destrua a chave de acesso (`del st.session_state["admin_logged_in"]`) assim que o usuário clicar em Logout para prevenir ataques de fixação de sessão.

3. **Prevenção contra Injeções**:
   - Toda e qualquer entrada de usuário (comentários, inputs) deve ser sanitizada. 
   - No Streamlit, ao exibir textos de banco de dados, garanta que não haja tags HTML sendo renderizadas inadvertidamente (a menos que seja via `unsafe_allow_html=True` em ambientes onde o conteúdo é 100% gerado/controlado pela própria aplicação e não por *user input*).
