import streamlit as st
import bcrypt
import pandas as pd
import plotly.express as px
from datetime import datetime
from database import get_db_session, Comment, Interaction, CommentStatus, AnalyticsSession

def check_password():
    """Retorna True se o usuário tiver a senha correta."""
    def password_entered():
        user_pw = st.session_state["admin_password"].encode('utf-8')
        default_hash = bcrypt.hashpw(b"admin123", bcrypt.gensalt()).decode('utf-8')
        stored_hash = st.secrets.get("ADMIN_PASSWORD_HASH", default_hash).encode('utf-8')
        
        try:
            if bcrypt.checkpw(user_pw, stored_hash):
                st.session_state["admin_logged_in"] = True
                del st.session_state["admin_password"]
            else:
                st.session_state["admin_logged_in"] = False
        except ValueError:
            st.session_state["admin_logged_in"] = False
            st.error("Erro interno ao validar senha. Verifique se o hash no secrets está correto.")

    if st.session_state.get("admin_logged_in", False):
        return True

    st.text_input("Senha do Administrador", type="password", on_change=password_entered, key="admin_password")
    return False

def show_admin_panel():
    st.title("Painel de Administração e Moderação")
    
    if not check_password():
        return
        
    col_out, col_test = st.columns([1, 2])
    with col_out:
        if st.button("Sair (Logout)"):
            if "admin_logged_in" in st.session_state:
                del st.session_state["admin_logged_in"]
            st.rerun()
    with col_test:
        if st.button("🔬 Entrar no Modo Teste de Persona"):
            st.session_state["persona_test_mode"] = True
            st.rerun()

    st.write("Bem-vindo! Aqui você gerencia comentários e interações da plataforma.")
    
    tabs = st.tabs(["Moderação de Comentários", "Estatísticas de Interação", "Tráfego e Acessos"])
    
    with tabs[0]:
        db = get_db_session()
        st.subheader("Dashboard de Moderação")
        
        total_pendentes = db.query(Comment).filter(Comment.status == CommentStatus.PENDING).count()
        total_aprovados = db.query(Comment).filter(Comment.status == CommentStatus.APPROVED).count()
        total_rejeitados = db.query(Comment).filter(Comment.status == CommentStatus.REJECTED).count()
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Pendentes", total_pendentes)
        c2.metric("Aprovados", total_aprovados)
        c3.metric("Rejeitados", total_rejeitados)
        st.divider()
        
        f1, f2 = st.columns(2)
        with f1:
            status_filter = st.selectbox("Filtrar por Status", ["Pendentes", "Aprovados", "Rejeitados", "Todos"])
        with f2:
            date_filter = st.date_input("A partir de (Data)", value=None)
            
        query = db.query(Comment)
        if status_filter == "Pendentes":
            query = query.filter(Comment.status == CommentStatus.PENDING)
        elif status_filter == "Aprovados":
            query = query.filter(Comment.status == CommentStatus.APPROVED)
        elif status_filter == "Rejeitados":
            query = query.filter(Comment.status == CommentStatus.REJECTED)
            
        if date_filter:
            min_date = datetime.combine(date_filter, datetime.min.time())
            query = query.filter(Comment.timestamp >= min_date)
            
        filtered_comments = query.order_by(Comment.timestamp.desc()).all()
        
        if not filtered_comments:
            st.info("Nenhum comentário encontrado com esses filtros.")
        else:
            for comment in filtered_comments:
                status_icon = "⏳" if comment.status == CommentStatus.PENDING else ("✅" if comment.status == CommentStatus.APPROVED else "❌")
                with st.expander(f"{status_icon} [{comment.timestamp.strftime('%d/%m %H:%M')}] {comment.section_name} - IP: {comment.ip_address}"):
                    st.write(f"**Por (Hash):** {comment.user_hash[:8]}")
                    st.write(f"**Comentário:**\n {comment.text}")
                    
                    if comment.status == CommentStatus.PENDING:
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("✅ Aprovar", key=f"approve_{comment.id}"):
                                comment.status = CommentStatus.APPROVED
                                db.commit()
                                st.rerun()
                        with col2:
                            if st.button("❌ Rejeitar", key=f"reject_{comment.id}"):
                                comment.status = CommentStatus.REJECTED
                                db.commit()
                                st.rerun()
        db.close()
                                
    with tabs[1]:
        st.subheader("Inteligência de Interações (Curtidas)")
        db = get_db_session()
        
        all_likes = pd.read_sql(db.query(Interaction).statement, db.bind)
        all_comments = pd.read_sql(db.query(Comment).statement, db.bind)
        all_sessions = pd.read_sql(db.query(AnalyticsSession).statement, db.bind)
        
        if not all_likes.empty:
            all_likes['timestamp'] = pd.to_datetime(all_likes['timestamp'])
            
            st.markdown("##### Seções Mais Curtidas")
            likes_por_secao = all_likes['section_name'].value_counts().reset_index()
            likes_por_secao.columns = ['Seção', 'Curtidas']
            fig_sec = px.bar(likes_por_secao, x='Curtidas', y='Seção', orientation='h')
            fig_sec.update_layout(yaxis={'categoryorder':'total ascending'}, plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_sec, use_container_width=True)
            
            if not all_sessions.empty:
                st.markdown("##### Quem curte o quê?")
                merged = pd.merge(all_likes, all_sessions[['user_hash', 'inferred_persona']], on='user_hash', how='left')
                merged['inferred_persona'] = merged['inferred_persona'].fillna('Desconhecido')
                persona_likes = merged['inferred_persona'].value_counts().reset_index()
                persona_likes.columns = ['Persona', 'Curtidas']
                
                fig_persona_like = px.pie(persona_likes, names='Persona', values='Curtidas', hole=0.4)
                st.plotly_chart(fig_persona_like, use_container_width=True)
            
            st.markdown("##### Evolução de Interações")
            timeline_likes = all_likes.copy()
            timeline_likes['Data'] = timeline_likes['timestamp'].dt.floor('d')
            likes_agg = timeline_likes.groupby('Data').size().reset_index(name='Curtidas')
            
            if not all_comments.empty:
                all_comments['timestamp'] = pd.to_datetime(all_comments['timestamp'])
                timeline_comments = all_comments.copy()
                timeline_comments['Data'] = timeline_comments['timestamp'].dt.floor('d')
                comments_agg = timeline_comments.groupby('Data').size().reset_index(name='Comentários')
                timeline_df = pd.merge(likes_agg, comments_agg, on='Data', how='outer').fillna(0)
            else:
                timeline_df = likes_agg
                timeline_df['Comentários'] = 0
                
            fig_time = px.line(timeline_df, x='Data', y=['Curtidas', 'Comentários'], markers=True)
            st.plotly_chart(fig_time, use_container_width=True)
            
        else:
            st.info("Ainda não há interações (curtidas) registradas para gerar estatísticas.")
            
        st.divider()
        st.write("Exportar Dados Brutos:")
        if not all_likes.empty:
            st.download_button("Baixar CSV de Curtidas", all_likes.to_csv(index=False), "curtidas.csv", "text/csv")
        if not all_comments.empty:
            st.download_button("Baixar CSV de Comentários", all_comments.to_csv(index=False), "comentarios.csv", "text/csv")
            
        db.close()
        
    with tabs[2]:
        st.subheader("Dashboard de Tráfego")
        
        db = get_db_session()
        sessions = pd.read_sql(db.query(AnalyticsSession).statement, db.bind)
        db.close()
        
        if not sessions.empty:
            sessions['start_time'] = pd.to_datetime(sessions['start_time'])
            
            st.markdown("##### Mapa de Calor (Calendário Semanal)")
            sessions['Dia_Semana'] = sessions['start_time'].dt.day_name()
            sessions['Hora'] = sessions['start_time'].dt.hour
            
            dias_map = {
                'Monday': '1-Seg', 'Tuesday': '2-Ter', 'Wednesday': '3-Qua',
                'Thursday': '4-Qui', 'Friday': '5-Sex', 'Saturday': '6-Sab', 'Sunday': '7-Dom'
            }
            sessions['Dia_Ord'] = sessions['Dia_Semana'].map(dias_map)
            
            heatmap_data = sessions.groupby(['Dia_Ord', 'Hora']).size().reset_index(name='Acessos')
            
            todos_dias = sorted(list(dias_map.values()))
            matriz = pd.DataFrame(index=todos_dias, columns=list(range(24))).fillna(0)
            
            for _, row in heatmap_data.iterrows():
                matriz.at[row['Dia_Ord'], row['Hora']] = row['Acessos']
                
            fig_heat = px.imshow(matriz, 
                                 labels=dict(x="Hora do Dia", y="Dia da Semana", color="Acessos"),
                                 x=list(range(24)), y=todos_dias,
                                 color_continuous_scale="Blues", aspect="auto")
            fig_heat.update_xaxes(dtick=1)
            st.plotly_chart(fig_heat, use_container_width=True)
            
            st.divider()
            
            st.markdown("##### Linha do Tempo")
            granularity = st.radio("Granularidade", ["Dia", "Hora", "Minuto"], horizontal=True)
            if granularity == "Dia":
                sessions['Período'] = sessions['start_time'].dt.floor('d')
            elif granularity == "Hora":
                sessions['Período'] = sessions['start_time'].dt.floor('h')
            elif granularity == "Minuto":
                sessions['Período'] = sessions['start_time'].dt.floor('min')
                
            agrupado = sessions.groupby('Período').size().reset_index(name='Acessos')
            fig = px.line(agrupado, x='Período', y='Acessos', markers=True)
            fig.update_traces(line_color="#0068c9")
            st.plotly_chart(fig, use_container_width=True)
            
            st.divider()
            st.subheader("Dispositivos e Personas")
            c1, c2 = st.columns(2)
            with c1:
                fig_os = px.pie(sessions, names='os_name', title="Sistemas Operacionais", hole=0.3)
                st.plotly_chart(fig_os, use_container_width=True)
            with c2:
                fig_persona = px.pie(sessions, names='inferred_persona', title="Personas Inferidas", hole=0.3)
                st.plotly_chart(fig_persona, use_container_width=True)
        else:
            st.info("Ainda não há dados de acesso registrados.")
