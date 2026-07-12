# Streamlit Analytics In-App

## Padrão Ouro de Analytics em Streamlit
Quando o projeto exigir rastreamento de uso, curtidas ou moderação em Streamlit, utilize este padrão em vez de depender de integrações complexas de terceiros.

1. **Banco de Dados (SQLite + SQLAlchemy)**:
   - Crie tabelas de `AnalyticsSession` (rastreio de sessão, hash de usuário IP+UserAgent, SO, browser), `Interaction` (curtidas em seções) e `Comment` (com status Pendente, Aprovado, Rejeitado).
   - Use `hashlib.sha256` combinado com IP e Data para gerar um `user_hash` anônimo diário.

2. **Rastreamento Invisível (`app.py`)**:
   - Defina as lógicas de sessão e `log_event()` em um arquivo `analytics.py`.
   - Invoque `log_event("action", data)` a cada mudança de estado dos botões (`st.radio`, `st.toggle`, `st.multiselect`) detectando `st.session_state` modificado.
   - O `st.radio` de navegação DEVE ter um `key` (ex: `key="modo_visao"`) para evitar dessincronização de índice em reruns.

3. **Dashboard de Admin Fantasma (`admin_panel.py`)**:
   - Isole o admin usando um query param: `if "admin" in st.query_params:`
   - Proteja com senha usando `st.text_input(type="password")` validado contra um hash `bcrypt` salvo em `st.secrets`.
   - **Abas**:
     - *Moderação*: `st.selectbox` de Status e `st.date_input`. 
     - *Interações*: Gráficos de barras (`px.bar`) para seções mais curtidas. Gráfico de pizza (`px.pie`) via `pd.merge` no `user_hash` cruzando sessões (Persona) e curtidas.
     - *Tráfego*: Gráfico em linha do tempo agrupando `dt.floor('d'|'h'|'min')`. E o poderoso **Heatmap Semanal**: Dias da Semana no eixo Y contra Horas (0-23) no eixo X.
