import streamlit as st
import streamlit.components.v1 as components
import random
from database import get_db_session, Interaction, Comment, CommentStatus
from user_tracking import get_user_hash
import i18n
import json
import analytics

def inject_global_loader():
    # Removido em favor do novo sistema de carregamento direcionado no app.py
    pass

import time

def render_like_button(section_name: str, key_suffix: str = ""):
    """Renderiza apenas o botão discreto de curtir policial."""
    user_hash, ip = get_user_hash()
    db = get_db_session()
    
    safe_key = f"{section_name.replace(' ', '_').replace('/', '_').replace('.', '_')}_{key_suffix}"
    
    has_liked = db.query(Interaction).filter_by(section_name=section_name, user_hash=user_hash).first()
    likes_count = db.query(Interaction).filter_by(section_name=section_name).count()
    
    col1, col2 = st.columns([85, 15])
    
    with col2:
        # Mostra o total de curtidas logo acima do botão para ficar alinhado
        st.markdown(f"<div style='font-size: 0.85rem; color: var(--text-color); opacity: 0.8; margin-bottom: 5px;'>Total de Curtidas: <b style='color: #4da6ff; font-size: 1rem;'>{likes_count}</b></div>", unsafe_allow_html=True)
        
        if has_liked:
            # Estado já curtido: ícone de tiro/explosão e texto
            if st.button(f"💥 {i18n.t('btn_liked')}", key=f"btn_like_{safe_key}_on"):
                db.delete(has_liked)
                db.commit()
                st.rerun()
                
            # Injeta CSS/JS para o efeito visual de sirene (nonce garante a execução no rerun)
            components.html(f"""
            <script>
            // Nonce para forçar re-render do iframe pelo Streamlit: {time.time()}
            const btns = window.parent.document.querySelectorAll('div[data-testid="stButton"] button p');
            btns.forEach(p => {{
                if (p.innerText.includes('💥')) {{
                    const btn = p.closest('button');
                    if (btn) btn.classList.add('liked-police-btn');
                }}
            }});
            if (!window.parent.document.getElementById('police-btn-css')) {{
                const style = window.parent.document.createElement('style');
                style.id = 'police-btn-css';
                style.innerHTML = `
                    .liked-police-btn {{
                        animation: strobe_like 1.2s infinite !important;
                        border: 1px solid rgba(128,128,128,0.3) !important;
                    }}
                    .liked-police-btn p {{
                        color: var(--text-color) !important;
                        font-weight: bold !important;
                    }}
                    @keyframes strobe_like {{
                        0%, 10% {{ box-shadow: 0 0 15px rgba(255, 0, 50, 0.5); background: rgba(255, 0, 50, 0.15); border-color: rgba(255,0,50,0.5) !important; }}
                        11%, 15% {{ box-shadow: none; background: transparent; border-color: rgba(128,128,128,0.3) !important; }}
                        16%, 25% {{ box-shadow: 0 0 15px rgba(255, 0, 50, 0.5); background: rgba(255, 0, 50, 0.15); border-color: rgba(255,0,50,0.5) !important; }}
                        
                        26%, 49% {{ box-shadow: none; background: transparent; border-color: rgba(128,128,128,0.3) !important; }}
                        
                        50%, 60% {{ box-shadow: 0 0 15px rgba(0, 100, 255, 0.5); background: rgba(0, 100, 255, 0.15); border-color: rgba(0,100,255,0.5) !important; }}
                        61%, 65% {{ box-shadow: none; background: transparent; border-color: rgba(128,128,128,0.3) !important; }}
                        66%, 75% {{ box-shadow: 0 0 15px rgba(0, 100, 255, 0.5); background: rgba(0, 100, 255, 0.15); border-color: rgba(0,100,255,0.5) !important; }}
                        
                        76%, 100% {{ box-shadow: none; background: transparent; border-color: rgba(128,128,128,0.3) !important; }}
                    }}
                `;
                window.parent.document.head.appendChild(style);
            }}
            </script>
            """, height=0)
        else:
            # Estado não curtido: Escudo (sóbrio, tático e bem visível) e texto neutro
            if st.button(f"🛡️ {i18n.t('btn_like')}", key=f"btn_like_{safe_key}_off"):
                new_like = Interaction(section_name=section_name, user_hash=user_hash, ip_address=ip)
                db.add(new_like)
                db.commit()
                analytics.log_event("like", {"section": section_name})
                st.rerun()
                
    db.close()


@st.dialog("💬 Comentários e Sugestões")
def modal_comentarios(global_topic: str):
    if st.session_state.get("light_mode"):
        st.markdown("""<style>
        div[role="dialog"], div[data-testid="stModal"] > div, div[data-testid="stDialog"] > div { background-color: #FFFFFF !important; border: 1px solid #CED4DA !important; }
        div[role="dialog"] *, div[data-testid="stModal"] *, div[data-testid="stDialog"] * { color: #1E2329 !important; }
        </style>""", unsafe_allow_html=True)
        
    st.markdown(f"**Deixe seu feedback sobre:** {global_topic}")
    
    """
    Modal (pop-up central) nativo do Streamlit que é muito superior ao popover 
    para ler e escrever textos.
    """
    user_hash, ip = get_user_hash()
    db = get_db_session()
    
    st.markdown(f"### {i18n.t('modal_title')}")
    st.subheader(i18n.t("modal_community"))
    
    st.write(i18n.t("modal_report"))
    st.caption(i18n.t("modal_privacy"))
    st.warning(i18n.t("disclaimer_comments"), icon="⚠️")
    
    st.markdown("""
        <style>
        /* Distribui o espaço das abas de forma igualitária e centralizada */
        div[data-testid="stTabs"] button[data-baseweb="tab"] {
            flex: 1;
            justify-content: center;
        }
        </style>
    """, unsafe_allow_html=True)
    
    tabs = st.tabs(["📖 Ler Comentários", "✏️ Escrever Comentário"])
    
    with tabs[0]:
        current_lang = st.session_state.get("language", "PT-BR")
        filter_opts = [i18n.t("modal_lang_all"), "PT-BR", "EN"]
        default_idx = filter_opts.index(current_lang) if current_lang in filter_opts else 0
        
        col_lang, col_sec = st.columns(2)
        with col_lang:
            selected_filter = st.selectbox(i18n.t("modal_filter_lang"), filter_opts, index=default_idx, key="comment_lang_filter")
            
        with col_sec:
            distinct_sections = [r[0] for r in db.query(Comment.section_name).filter(Comment.status==CommentStatus.APPROVED).distinct().all()]
            sec_final = ["Todos", i18n.t("modal_general")]
            for s in sorted(distinct_sections):
                if s not in sec_final:
                    sec_final.append(s)
            selected_sec = st.selectbox("Filtro de Seção", sec_final, key="comment_sec_filter")
        
        query = db.query(Comment).filter_by(status=CommentStatus.APPROVED)
        if selected_filter != i18n.t("modal_lang_all"):
            query = query.filter_by(language=selected_filter)
        if selected_sec != "Todos":
            query = query.filter_by(section_name=selected_sec)
            
        approved_comments = query.order_by(Comment.timestamp.asc()).all()
        
        if approved_comments:
            for c in approved_comments:
                st.info(f"**Anônimo** em {c.timestamp.strftime('%d/%m %H:%M')}:\n\n_{c.section_name}_\n\n{c.text}")
        else:
            st.write(i18n.t("modal_no_comments"))
            
    with tabs[1]:
        # Opções dinâmicas baseadas no modo de visão (global_topic)
        opcoes_secao = [i18n.t("modal_general")]
        if "1" in global_topic:
            opcoes_secao += ["1.1 Matriz de Atribuições", "1.2 Matriz Adjacência", "1.3 Explorador", "1.4 Grafo", "1.5 Gower", "1.6 Régua", "1.7 Dendograma", "1.8 UpSet"]
        elif "2" in global_topic:
            opcoes_secao += ["2.1 Comparativo Direito", "2.2 Similaridade Geral", "2.3 Discrepâncias"]
        elif "3" in global_topic:
            opcoes_secao += ["3.1 Distribuição", "3.2 Linha do tempo", "3.3 Mudanças"]
        elif "4" in global_topic:
            opcoes_secao += ["4.1 Rastreamento", "4.2 Evolução Específica"]
            
        st.info(i18n.t("modal_current_mode").replace("{global_topic}", global_topic))
        section_to_comment = st.selectbox(i18n.t("modal_select_topic"), opcoes_secao, key="comment_sec_modal")
        comment_text = st.text_area(i18n.t("modal_your_report"), key="comment_txt_modal")
        
        if st.button(i18n.t("modal_btn_send"), key="send_comment_modal"):
            if len(comment_text.strip()) < 3:
                st.error(i18n.t("modal_err_short"))
            else:
                new_comment = Comment(
                    section_name=f"{global_topic} - {section_to_comment}",
                    user_hash=user_hash,
                    ip_address=ip,
                    text=comment_text,
                    language=current_lang,
                    status=CommentStatus.PENDING
                )
                db.add(new_comment)
                db.commit()
                analytics.log_event("comment", {"section": f"{global_topic} - {section_to_comment}", "text_len": len(comment_text)})
                st.success(i18n.t("modal_success"))
    db.close()


def render_floating_comments(global_topic: str):
    """
    Injeta um HUD Flutuante no canto inferior esquerdo usando JS puro (da mesma forma
    que as referências funcionam no canto direito). Ao ser clicado, o JS aciona
    um botão escondido do Streamlit para abrir a Modal central!
    """
    
    # 1. Botão fantasma que ativa a Modal
    # Precisamos criar de forma que ele não ocupe espaço nenhum na tela
    st.markdown("<div id='ghost_btn_container' style='display:none;'>", unsafe_allow_html=True)
    btn_ghost = st.button("open_hidden_modal", key="btn_open_comments")
    st.markdown("</div>", unsafe_allow_html=True)

    # Hack de CSS para zerar o espaço ocupado pelo botão 
    st.markdown("""
        <style>
        /* Procura pelo container do botão fantasma e o colapsa.
           Atenção: Não podemos dar display:none direto no botão pq o JS precisa clicar nele */
        div[data-testid="stVerticalBlock"] > div:has(#ghost_btn_container) {
            height: 0px !important;
            min-height: 0px !important;
            margin: 0 !important;
            padding: 0 !important;
            overflow: hidden !important;
            opacity: 0 !important;
            pointer-events: none !important;
        }
        </style>
    """, unsafe_allow_html=True)

    if btn_ghost:
        modal_comentarios(global_topic)
        
    # 2. Injeção do HUD Flutuante no ROOT do DOM (como as referências)
    hud_html = """
    <script>
        const oldCommentsHUD = window.parent.document.getElementById('hud-floating-comments');
        if (oldCommentsHUD) {
            oldCommentsHUD.remove();
        }

        setInterval(() => {
            const buttons = window.parent.document.querySelectorAll('button p');
            for(let b of buttons) {
                if(b.innerText === "open_hidden_modal") {
                    let parent = b.closest('.stButton');
                    if(parent) parent.style.display = 'none';
                    else b.parentElement.parentElement.style.display = 'none';
                }
            }
        }, 300);

        const btnHUD = window.parent.document.createElement('div');
        btnHUD.id = 'hud-floating-comments';
        btnHUD.innerHTML = `
            <style>
            #hud-floating-comments {
                position: fixed;
                bottom: 25px;
                left: 25px;
                background: var(--background-color, rgba(14, 17, 23, 0.90));
                backdrop-filter: blur(15px);
                border: 1px solid var(--text-color, rgba(255, 255, 255, 0.15));
                border-radius: 30px;
                padding: 0 20px;
                z-index: 999999;
                box-shadow: 0 4px 15px rgba(0,0,0,0.3);
                transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
                width: 170px;
                height: 50px;
                display: flex;
                align-items: center;
                justify-content: center;
                cursor: pointer;
                font-family: sans-serif;
                color: var(--text-color, #E0E0E0);
                font-weight: bold;
                font-size: 0.95rem;
                gap: 8px;
            }
            #hud-floating-comments:hover {
                border: 1px solid #4da6ff;
                color: #4da6ff;
                transform: translateY(-2px);
                box-shadow: 0 8px 25px rgba(0,0,0,0.6);
            }
            </style>
            <span style="font-size: 1.2rem;">💬</span> {{BTN_COMMENTS}}
        `;
        
        btnHUD.onclick = function() {
            // Evita duplos cliques travando o botão temporariamente
            if (this.style.opacity === '0.8') return;
            
            // Cria um popup visual logo acima do botão
            const statusPopup = window.parent.document.createElement('div');
            statusPopup.id = 'hud-loading-popup';
            statusPopup.innerHTML = '<span style="display: inline-block; animation: spin 1s linear infinite;">🚨</span> {{HUD_LOADING}}';
            statusPopup.style.cssText = 'position: fixed; bottom: 85px; left: 25px; background: #cc0000; color: white; padding: 8px 15px; border-radius: 8px; font-weight: bold; z-index: 999999; box-shadow: 0 4px 15px rgba(204, 0, 0, 0.6); animation: slideUp 0.3s ease-out; font-family: sans-serif; font-size: 0.95rem;';
            
            // Remove popup antigo se houver (para evitar sujeira)
            const oldPopup = window.parent.document.getElementById('hud-loading-popup');
            if(oldPopup) oldPopup.remove();
            
            window.parent.document.body.appendChild(statusPopup);

            this.style.opacity = '0.8';
            this.style.cursor = 'wait';
            
            // Injeta a keyframe animation no documento pai se não existir
            if (!window.parent.document.getElementById('hud-anim-css')) {
                const styleElement = window.parent.document.createElement('style');
                styleElement.id = 'hud-anim-css';
                styleElement.innerHTML = `
                    @keyframes spin { 
                        0% { transform: rotate(0deg) scale(1); opacity: 1; } 
                        50% { transform: rotate(180deg) scale(1.3); opacity: 0.7; }
                        100% { transform: rotate(360deg) scale(1); opacity: 1; } 
                    }
                    @keyframes slideUp { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
                `;
                window.parent.document.head.appendChild(styleElement);
            }

            // Busca os botões do DOM e clica naquele que é o nosso fantasma
            const buttons = window.parent.document.querySelectorAll('button p');
            for(let b of buttons) {
                if(b.innerText === "open_hidden_modal") {
                    b.parentElement.click();
                    break;
                }
            }
            
            // Restaura o estado normal depois de 4 segundos
            setTimeout(() => {
                this.style.opacity = '1';
                this.style.cursor = 'pointer';
                const p = window.parent.document.getElementById('hud-loading-popup');
                if(p) p.remove();
            }, 4000);
        };
        
        window.parent.document.body.appendChild(btnHUD);
    </script>
    """.replace("{{BTN_COMMENTS}}", i18n.t("btn_comments")).replace("{{HUD_LOADING}}", random.choice(i18n.t("loading_msgs")))
    
    components.html(hud_html, height=0)

def get_loading_message():
    return random.choice(i18n.t("loading_msgs"))

def render_interactions(section_name: str):
    render_floating_comments(section_name)
