import streamlit as st
import streamlit.components.v1 as components
import networkx as nx
import importlib
import explanations
importlib.reload(explanations)
import pandas as pd
import data_loader
import data_processing
importlib.reload(data_processing)
import json
import analytics
import visualizations
import logger
import os
import i18n
import interaction_ui
importlib.reload(i18n)
importlib.reload(interaction_ui)
importlib.reload(visualizations)
import floating_toc
importlib.reload(floating_toc)
from floating_toc import render_toc


# Roteamento do painel de administração oculto
if "admin" in st.query_params:
    if not st.session_state.get("persona_test_mode", False):
        import admin_panel
        import importlib
        importlib.reload(admin_panel)
        admin_panel.show_admin_panel()
        st.stop()

# Sincroniza idioma a partir da URL (se houver) apenas na primeira carga
if "language" not in st.session_state:
    if "lang" in st.query_params:
        st.session_state.language = st.query_params["lang"]
    else:
        st.session_state.language = "PT-BR"

try:
    df_conv = pd.read_csv('Tabela_Conversao_Cargos.CSV', sep=';', encoding='iso-8859-1')
    df_conv.to_json('csv_dump.json', orient='records', force_ascii=False)

    
except Exception as e:
    with open('erro.txt', 'w') as f: f.write(str(e))
    pass

# Iniciar o banco de dados de log
logger.init_db()

# Configuração Básica da Página
st.set_page_config(page_title="Estudo de Atribuições PCSP", layout="wide")

# --- MODO TESTE DE PERSONA (UI) ---
persona_placeholder = None
if st.session_state.get("persona_test_mode", False):
    st.sidebar.markdown("### 🔬 Modo Teste de Persona")
    st.sidebar.caption("Navegue pela aplicação para ver a inferência mudar em tempo real baseada no seu comportamento.")
    
    persona_placeholder = st.sidebar.empty()
    
    if st.sidebar.button("Sair do Teste (Voltar ao Admin)"):
        st.session_state["persona_test_mode"] = False
        st.rerun()
    st.sidebar.markdown("---")

# --- RODAPÉ FLUTUANTE DE CONTATOS E REFERÊNCIAS (Injeção Direta no DOM) ---
footer_html = """
<script>
    // Tenta remover o footer antigo caso o Streamlit faça um re-run da tela
    const oldFooter = window.parent.document.getElementById('hud-floating-footer');
    if (oldFooter) {
        oldFooter.remove();
    }

    // Constrói o HUD puro no root do navegador, imune aos containers do Streamlit
    const footer = window.parent.document.createElement('div');
    footer.id = 'hud-floating-footer';
    footer.innerHTML = `
        <style>
        #hud-floating-footer {
            position: fixed;
            bottom: 25px;
            right: 25px;
            background: rgba(14, 17, 23, 0.90);
            backdrop-filter: blur(15px);
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 30px;
            padding: 0 20px;
            z-index: 999999;
            box-shadow: 0 4px 15px rgba(0,0,0,0.5);
            transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
            width: 240px;
            height: 50px;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: flex-start;
            font-family: sans-serif;
        }
        #hud-floating-footer:hover {
            width: 320px;
            height: max-content;
            border-radius: 15px;
            padding: 20px;
            align-items: flex-start;
        }
        .hud-icon {
            display: flex;
            align-items: center;
            justify-content: center;
            width: 100%;
            height: 50px;
            cursor: pointer;
            flex-shrink: 0;
            color: #E0E0E0;
            font-weight: bold;
            font-size: 0.95rem;
            gap: 8px;
        }
        #hud-floating-footer:hover .hud-icon {
            display: none;
        }
        .hud-content {
            opacity: 0;
            transition: opacity 0.3s ease;
            transition-delay: 0.1s;
            display: none;
            width: 100%;
        }
        #hud-floating-footer:hover .hud-content {
            opacity: 1;
            display: block;
        }
        .hud-content a {
            color: #4da6ff;
            text-decoration: none;
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 8px;
            font-size: 0.95rem;
            padding: 6px;
            border-radius: 5px;
            transition: background 0.2s;
        }
        .hud-content a:hover {
            text-decoration: underline;
            background: rgba(255,255,255,0.05);
        }
        .hud-content h4 {
            margin: 0 0 10px 0;
            color: #E0E0E0;
            font-size: 1rem;
            border-bottom: 1px solid #333;
            padding-bottom: 5px;
        }
        </style>
        
        <div class="hud-icon">
            <span style="font-size: 1.2rem;">📚</span> __FOOTER_TITLE__
        </div>
        <div class="hud-content">
            <h4>__REF_TITLE__</h4>
            <span style="font-size: 0.75rem; color: #A0A0A0; display: block; margin: -5px 0 8px 0; font-style: italic;">__REF_DESC__</span>
            <a href="https://github.com/phsmaia/Estudo_Atribuicoes_PCSP" target="_blank">__REPO__</a>
            <a href="https://periodicos.pf.gov.br/index.php/RBCP/pt_BR/article/view/4693" target="_blank">__ARTICLE__</a>
            <a href="https://zenodo.org/records/14284483" target="_blank">__DATA__</a>
            <h4 style="margin-top: 15px;">__CONTACT_TITLE__</h4>
            <span style="font-size: 0.75rem; color: #A0A0A0; display: block; margin: -5px 0 8px 0; font-style: italic;">__CONTACT_DESC__</span>
            <a href="mailto:maia.phs@gmail.com">📧 maia.phs@gmail.com</a>
            <a href="https://www.linkedin.com/in/pedromaiapapilodata/" target="_blank">__LINKEDIN__</a>
        </div>
    `;
    window.parent.document.body.appendChild(footer);
</script>
"""
for placeholder, key in [
    ('__FOOTER_TITLE__', 'footer_title'),
    ('__REF_TITLE__', 'footer_ref_title'),
    ('__REF_DESC__', 'footer_ref_desc'),
    ('__REPO__', 'footer_repo'),
    ('__ARTICLE__', 'footer_article'),
    ('__DATA__', 'footer_data'),
    ('__CONTACT_TITLE__', 'footer_contact_title'),
    ('__CONTACT_DESC__', 'footer_contact_desc'),
    ('__LINKEDIN__', 'footer_linkedin')
]:
    footer_html = footer_html.replace(placeholder, i18n.t(key))

components.html(footer_html, height=0)
import interaction_ui
import json

targeted_loader_js = f"""
<script>
    if (!window.parent.document.getElementById('targeted-loader-engine')) {{
        const script = window.parent.document.createElement('script');
        script.id = 'targeted-loader-engine';
        script.innerHTML = `
            if (!window.__lastWidgetTracker) {{
                window.__lastWidgetTracker = true;
                window.__lastWidget = null;
                window.document.addEventListener('mousedown', function(e) {{
                    let t = e.target;
                    while(t && t !== window.document) {{
                        const testid = t.getAttribute ? t.getAttribute('data-testid') : null;
                        if (testid && testid.startsWith('st')) {{
                            window.__lastWidget = t;
                            break;
                        }}
                        t = t.parentNode;
                    }}
                }}, true);
            }}
            
            window.__hud_msgs = {json.dumps(i18n.t("loading_msgs"))};
            window.document.addEventListener('mousedown', function(e) {{
                let target = e.target;
                let isTrigger = false;
                while(target && target !== window.document) {{
                    if (target.getAttribute) {{
                        const testid = (target.getAttribute('data-testid') || '').toLowerCase();
                        const role = (target.getAttribute('role') || '').toLowerCase();
                        const bsweb = (target.getAttribute('data-baseweb') || '').toLowerCase();
                        const cls = (target.className || '');
                        const clsStr = typeof cls === 'string' ? cls.toLowerCase() : '';
                        
                        if (
                            testid.includes('radio') || testid.includes('checkbox') || testid.includes('select') || 
                            testid.includes('slider') || testid.includes('segment') || testid.includes('tab') || testid.includes('button') ||
                            role.includes('radio') || role.includes('tab') || role.includes('slider') || 
                            role.includes('combobox') || role.includes('listbox') || role.includes('option') || 
                            role.includes('switch') || role.includes('checkbox') || role.includes('button') ||
                            bsweb.includes('radio') || bsweb.includes('checkbox') || bsweb.includes('select') || 
                            bsweb.includes('slider') || bsweb.includes('tab') || bsweb.includes('button') ||
                            clsStr.includes('st-core-button') || clsStr.includes('radio') || clsStr.includes('segmentedcontrol') || clsStr.includes('tab')
                        ) {{
                            if (!testid.includes('markdown')) {{
                                isTrigger = true;
                                break;
                            }}
                        }}
                    }}
                    target = target.parentNode;
                }}
                
                if (!isTrigger) return;
                
                // Clear any existing custom loaders
                const oldLoaders = window.parent.document.querySelectorAll('.custom-inline-loader');
                oldLoaders.forEach(l => l.remove());

                // Adiciona o CSS de sirene intermitente se não existir
                if (!window.parent.document.getElementById('hud-strobe-css')) {{
                    const style = window.parent.document.createElement('style');
                    style.id = 'hud-strobe-css';
                    style.innerHTML = "" + 
                        "@keyframes hud_strobe {{ " +
                            "0%, 10% {{ box-shadow: 0 0 15px rgba(255, 0, 50, 0.9); background: rgba(255, 0, 50, 0.95); }} " +
                            "11%, 15% {{ box-shadow: none; background: rgba(0, 0, 0, 0.8); }} " +
                            "16%, 25% {{ box-shadow: 0 0 15px rgba(255, 0, 50, 0.9); background: rgba(255, 0, 50, 0.95); }} " +
                            "26%, 49% {{ box-shadow: none; background: rgba(0, 0, 0, 0.8); }} " +
                            "50%, 60% {{ box-shadow: 0 0 15px rgba(0, 100, 255, 0.9); background: rgba(0, 100, 255, 0.95); }} " +
                            "61%, 65% {{ box-shadow: none; background: rgba(0, 0, 0, 0.8); }} " +
                            "66%, 75% {{ box-shadow: 0 0 15px rgba(0, 100, 255, 0.9); background: rgba(0, 100, 255, 0.95); }} " +
                            "76%, 100% {{ box-shadow: none; background: rgba(0, 0, 0, 0.8); }} " +
                        "}} " +
                        ".custom-inline-loader {{ " +
                            "position: fixed; top: 25px; left: 50%; transform: translateX(-50%); z-index: 9999999; " +
                            "color: white; padding: 8px 20px; border-radius: 30px; font-size: 1rem; font-weight: bold; " +
                            "animation: hud_strobe 1.2s infinite; border: 1px solid rgba(255,255,255,0.2); " +
                            "box-shadow: 0 4px 15px rgba(0,0,0,0.5); display: flex; align-items: center; gap: 10px; " +
                            "pointer-events: none; " +
                        "}}";
                    window.parent.document.head.appendChild(style);
                }}

                const msgs = window.__hud_msgs || ["Carregando..."];
                const randMsg = msgs[Math.floor(Math.random() * msgs.length)];
                
                const loaderHTML = '<div class="custom-inline-loader"><span style="display:inline-block; animation: spinLoader 1s linear infinite;">🚨</span> ' + randMsg + '</div>';
                
                window.parent.document.body.insertAdjacentHTML('beforeend', loaderHTML);
                
                if (!window.document.getElementById('loader-anim-css')) {{
                    const style = window.document.createElement('style');
                    style.id = 'loader-anim-css';
                    style.innerHTML = '@keyframes spinLoader {{ 100% {{ transform: rotate(360deg); }} }}';
                    window.document.head.appendChild(style);
                }}
                
                // BUGFIX: Remove loader automaticamente após 3.5s para evitar que ele fique preso na tela
                setTimeout(() => {{
                    const loadersToClean = window.parent.document.querySelectorAll('.custom-inline-loader');
                    loadersToClean.forEach(l => l.remove());
                }}, 3500);
            }}, true);
        `;
        window.parent.document.head.appendChild(script);
    }} else {{
        window.parent.__hud_msgs = {json.dumps(i18n.t("loading_msgs"))};
    }}
</script>
"""
components.html(targeted_loader_js, height=0)

# Injeção de CSS para destaques críticos (Transparência Matemática e Status Bar)
st.markdown("""
<style>
/* Animação Premium: Fade & Focus (Sem alteração geométrica) */
@keyframes smoothCascadeFocus {
    0% { opacity: 0; filter: blur(5px); }
    100% { opacity: 1; filter: blur(0); }
}

div[data-testid="stVerticalBlock"] > div {
    opacity: 0; 
    animation: smoothCascadeFocus 0.7s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

/* Fundo Elegante e Trava contra barras de rolagem artificiais */
.stApp {
    background: radial-gradient(circle at 50% 0%, #121c2b 0%, #0e1117 60%) !important;
}

/* --- Ambient Police Lights (Subtle & Cinematic) --- */
.stApp::before {
    content: "";
    position: fixed;
    top: 0; left: 0; width: 100vw; height: 100vh;
    pointer-events: none;
    z-index: 9999;
    mix-blend-mode: screen;
    background: radial-gradient(circle at 15% 20%, rgba(255, 0, 0, 0.25), transparent 60%),
                radial-gradient(circle at 85% 80%, rgba(255, 0, 0, 0.15), transparent 60%);
    animation: ambientRed 8s infinite alternate ease-in-out;
}

.stApp::after {
    content: "";
    position: fixed;
    top: 0; left: 0; width: 100vw; height: 100vh;
    pointer-events: none;
    z-index: 9999;
    mix-blend-mode: screen;
    background: radial-gradient(circle at 85% 20%, rgba(0, 80, 255, 0.25), transparent 60%),
                radial-gradient(circle at 15% 80%, rgba(0, 80, 255, 0.15), transparent 60%);
    animation: ambientBlue 10s infinite alternate ease-in-out;
}

@keyframes ambientRed {
    0% { opacity: 0.3; transform: scale(1); }
    100% { opacity: 0.7; transform: scale(1.1); }
}

@keyframes ambientBlue {
    0% { opacity: 0.7; transform: scale(1.1); }
    100% { opacity: 0.3; transform: scale(1); }
}

/* Atrasos escalonados */
div[data-testid="stVerticalBlock"] > div:nth-child(1) { animation-delay: 0.05s; }
div[data-testid="stVerticalBlock"] > div:nth-child(2) { animation-delay: 0.15s; }
div[data-testid="stVerticalBlock"] > div:nth-child(3) { animation-delay: 0.25s; }
div[data-testid="stVerticalBlock"] > div:nth-child(4) { animation-delay: 0.35s; }
div[data-testid="stVerticalBlock"] > div:nth-child(5) { animation-delay: 0.45s; }

/* Sticky Container Header */
div[data-testid="stLayoutWrapper"]:has(div#sticky-header-anchor):has(div[data-testid="stRadio"]) {
    position: sticky;
    top: 0;
    z-index: 999;
    background-color: rgba(14, 17, 23, 0.95);
    padding: 15px 20px 10px 20px;
    border-radius: 12px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.15);
    box-shadow: 0 8px 32px rgba(0,0,0,0.4);
    margin-bottom: 25px;
    backdrop-filter: blur(10px);
}

/* Remover espaço em branco superior do Streamlit */
.block-container {
    padding-top: 2rem !important;
    padding-bottom: 2rem !important;
}
header[data-testid="stHeader"] {
    background: transparent !important;
    height: 0px !important;
}

.transparency-box {
    background-color: #2D2D2D;
    border-left: 5px solid #0072B2;
    padding: 15px;
    border-radius: 5px;
    margin-bottom: 20px;
}
.transparency-box h4 {
    margin-top: 0;
    color: #0072B2;
}

/* Estilo da Barra de Status Discreta */
.status-bar-container {
    display: flex;
    justify-content: center;
    flex-wrap: wrap;
    gap: 10px;
    padding: 5px 0px 10px 0px;
    margin-bottom: 5px;
    border-bottom: 1px solid #333;
}
.status-badge {
    background-color: #1E1E1E;
    color: #A0A0A0;
    border: 1px solid #444;
    border-radius: 12px;
    padding: 4px 10px;
    font-size: 0.75rem;
    font-weight: 500;
    display: flex;
    align-items: center;
    gap: 5px;
}
.status-badge strong {
    color: #E0E0E0;
    font-weight: 600;
}

</style>
""", unsafe_allow_html=True)

# --- CARREGAMENTO DE DADOS COM SPLASH SCREEN ---
if "first_load_done" not in st.session_state:
    msgs_json = json.dumps(i18n.t("loading_msgs"))
    title_str = i18n.t("title")
    
    splash_html = f"""
    <script>
    if (!window.parent.document.getElementById('custom-splash-screen')) {{
        const splash = window.parent.document.createElement('div');
        splash.id = 'custom-splash-screen';
        splash.innerHTML = `
            <style>
            #custom-splash-screen {{
                position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
                background: #0b0f19;
                z-index: 9999999; display: flex; flex-direction: column;
                align-items: center; justify-content: center; color: white;
                font-family: sans-serif; overflow: hidden;
            }}
            .police-lights {{
                position: absolute; top: 0; left: 0; width: 100%; height: 100%;
                background: transparent;
                animation: strobe 1.2s infinite;
                pointer-events: none;
            }}
            @keyframes strobe {{
                0%, 10% {{ background: radial-gradient(circle at 15% 50%, rgba(255, 0, 50, 0.25) 0%, transparent 40%), radial-gradient(circle at 85% 50%, rgba(0, 100, 255, 0) 0%, transparent 40%); opacity: 1; transform: scale(1.05); }}
                11%, 15% {{ background: transparent; opacity: 0.3; transform: scale(1); }}
                16%, 25% {{ background: radial-gradient(circle at 15% 50%, rgba(255, 0, 50, 0.25) 0%, transparent 40%), radial-gradient(circle at 85% 50%, rgba(0, 100, 255, 0) 0%, transparent 40%); opacity: 1; transform: scale(1.05); }}
                
                26%, 49% {{ background: transparent; opacity: 0.3; transform: scale(1); }}
                
                50%, 60% {{ background: radial-gradient(circle at 15% 50%, rgba(255, 0, 50, 0) 0%, transparent 40%), radial-gradient(circle at 85% 50%, rgba(0, 100, 255, 0.25) 0%, transparent 40%); opacity: 1; transform: scale(1.05); }}
                61%, 65% {{ background: transparent; opacity: 0.3; transform: scale(1); }}
                66%, 75% {{ background: radial-gradient(circle at 15% 50%, rgba(255, 0, 50, 0) 0%, transparent 40%), radial-gradient(circle at 85% 50%, rgba(0, 100, 255, 0.25) 0%, transparent 40%); opacity: 1; transform: scale(1.05); }}
                
                76%, 100% {{ background: transparent; opacity: 0.3; transform: scale(1); }}
            }}
            .fingerprint-btn {{
                width: 90px; height: 90px; border-radius: 50%;
                border: 2px solid rgba(77, 166, 255, 0.3);
                display: flex; align-items: center; justify-content: center;
                margin-bottom: 25px; cursor: pointer; position: relative;
                background: rgba(14, 17, 23, 0.5); backdrop-filter: blur(5px);
                transition: all 0.3s ease;
            }}
            .fingerprint-btn svg {{
                width: 45px; height: 45px; stroke: #4da6ff; fill: none; transition: all 0.3s ease;
            }}
            .fingerprint-btn:hover {{
                border-color: #4da6ff; box-shadow: 0 0 20px rgba(77, 166, 255, 0.4);
            }}
            .fingerprint-btn.scanning {{
                border-color: #00ffcc; box-shadow: 0 0 30px rgba(0, 255, 204, 0.6);
            }}
            .fingerprint-btn.scanning svg {{ stroke: #00ffcc; }}
            .scan-line {{
                position: absolute; top: 10%; left: 15%; width: 70%; height: 3px;
                background: #00ffcc; box-shadow: 0 0 12px #00ffcc;
                animation: scanAnim 1.5s infinite ease-in-out;
                display: none; border-radius: 2px;
            }}
            .fingerprint-btn.scanning .scan-line {{ display: block; }}
            @keyframes scanAnim {{ 0% {{ top: 15%; }} 50% {{ top: 85%; }} 100% {{ top: 15%; }} }}
            
            .progress-bar-container {{
                width: 300px; height: 6px; background: rgba(255,255,255,0.1);
                border-radius: 3px; margin: 25px 0; overflow: hidden; position: relative;
            }}
            .progress-bar-fill {{
                position: absolute; top: 0; left: 0; height: 100%; background: #4da6ff;
                width: 30%; animation: loadIndeterminate 1.5s infinite ease-in-out;
                border-radius: 3px;
                transition: background 0.3s ease, box-shadow 0.3s ease;
            }}
            .progress-bar-fill.scanning {{
                background: #00ffcc;
                box-shadow: 0 0 10px rgba(0, 255, 204, 0.6);
            }}
            @keyframes loadIndeterminate {{ 0% {{ left: -30%; }} 100% {{ left: 100%; }} }}
            </style>
            
            <div class="police-lights"></div>
            
            <div class="fingerprint-btn" id="interactive-badge" title="Pressione para escaneamento biométrico (Interativo)">
                <!-- Ícone SVG de Impressão Digital / Distintivo -->
                <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5">
                    <path d="M18.9 7a8 8 0 0 1 1.1 5v1a6 6 0 0 0 .8 3M8 11a4 4 0 0 1 8 0v1a10 10 0 0 0 2 6"/><path d="M12 11v2a14 14 0 0 0 2.5 8M8 15a18 18 0 0 0 1.8 6m-4.9-2a22 22 0 0 1-.9-7v-1a8 8 0 0 1 12-6.95"/>
                </svg>
                <div class="scan-line"></div>
            </div>
            
            <h2 style="margin-bottom: 10px; color: #E0E0E0; text-align: center; text-transform: uppercase; letter-spacing: 2px;">{title_str}</h2>
            <div class="progress-bar-container"><div class="progress-bar-fill"></div></div>
            <div id="splash-msg" style="color: #4da6ff; font-weight: bold; font-size: 1.1rem; height: 30px;">Carregando...</div>
        `;
        window.parent.document.body.appendChild(splash);
        
        // Interatividade divertida do botão
        const badge = window.parent.document.getElementById('interactive-badge');
        const msgEl = window.parent.document.getElementById('splash-msg');
        const pbFill = window.parent.document.querySelector('.progress-bar-fill');
        
        badge.addEventListener('mousedown', () => {{
            badge.classList.add('scanning');
            if(pbFill) pbFill.classList.add('scanning');
            msgEl.innerText = "🕵️‍♂️ Analisando biometria...";
            msgEl.style.color = "#00ffcc";
        }});
        badge.addEventListener('mouseup', () => {{
            badge.classList.remove('scanning');
            if(pbFill) pbFill.classList.remove('scanning');
            msgEl.style.color = "#4da6ff";
        }});
        badge.addEventListener('mouseleave', () => {{
            badge.classList.remove('scanning');
            if(pbFill) pbFill.classList.remove('scanning');
            msgEl.style.color = "#4da6ff";
        }});
        
        const msgs = {msgs_json};
        msgEl.innerText = msgs[0];
        
        setInterval(() => {{
            if (!badge.classList.contains('scanning')) {{
                msgEl.innerText = msgs[Math.floor(Math.random() * msgs.length)];
            }}
        }}, 2000);
        
        setTimeout(() => {{
            const btns = window.parent.document.querySelectorAll('.stButton button p');
            for (let b of btns) {{
                if (b.innerText === 'continue_load') {{
                    b.parentElement.click();
                    break;
                }}
            }}
        }}, 200);
    }}
    </script>
    """
    components.html(splash_html, height=0)
    
    st.markdown("<div style='display:none;'>", unsafe_allow_html=True)
    btn = st.button("continue_load", key="btn_continue_load")
    st.markdown("</div>", unsafe_allow_html=True)
    
    if btn:
        st.session_state.first_load_done = True
        st.rerun()
    st.stop()
else:
    remove_splash_js = """
    <script>
    const splash = window.parent.document.getElementById('custom-splash-screen');
    if (splash) {
        splash.style.opacity = '0';
        splash.style.transition = 'opacity 0.5s ease';
        setTimeout(() => splash.remove(), 500);
    }
    </script>
    """
    components.html(remove_splash_js, height=0)

datasets = data_loader.get_all_datasets()
opcoes_cenarios = [
    "Atual Sem Correção",
    "Atual Com Correção",
    "LONPC Sem Correção",
    "LONPC Com Correção",
    "Reestruturação 2024"
]

mapa_cenarios = {
    "Atual Sem Correção": datasets["atual_sem_correcao"],
    "Atual Com Correção": datasets["atual_com_correcao"],
    "LONPC Sem Correção": datasets["lonpc_sem_correcao"],
    "LONPC Com Correção": datasets["lonpc_com_correcao"],
    "Reestruturação 2024": datasets["reestruturacao"]
}

# --- CABEÇALHO GLOBAL E ROTEAMENTO ---
st.markdown("""
    <style>
    .block-container {
        padding-top: 0rem !important; 
        margin-top: 0rem !important;
        padding-bottom: 1rem !important;
    }
    
    header[data-testid="stHeader"] {
        display: none;
    }
    
    header[data-testid="stHeader"] {
        display: none;
    }
    </style>
""", unsafe_allow_html=True)

# Container Exclusivo para o Header Sticky
with st.container():
    st.markdown("<div id='sticky-header-anchor'></div>", unsafe_allow_html=True)
    
    col_title, col_btn = st.columns([70, 30], vertical_alignment="center")
    with col_title:
        st.markdown(f"<h3 style='margin: 0; padding: 0; font-size: 1.4rem; color: #E0E0E0;'>{i18n.t('title')}</h3>", unsafe_allow_html=True)
    def _muda_idioma():
        val = st.session_state.lang_radio
        st.session_state.language = 'PT-BR' if 'PT-BR' in val else 'EN'
        analytics.log_event("change_language", {"language": st.session_state.language})

    with col_btn:
        c1, c2 = st.columns([6, 4], vertical_alignment="center")
        with c1:
            st.markdown(
                "<div style='text-align: right; font-size: 0.95rem; font-weight:600; color: #aaa; margin-top: -13px;'>Idioma / Language 🌐 <span title='Clique para alternar o idioma do painel / Click to switch dashboard language' style='cursor: help; display: inline-flex; align-items: center; justify-content: center; width: 16px; height: 16px; border-radius: 50%; border: 1px solid #aaa; font-size: 0.7rem; margin-left: 2px;'>?</span></div>", 
                unsafe_allow_html=True
            )
        with c2:
            st.radio(
                "lang_label", 
                options=["PT-BR", "EN"], 
                index=0 if st.session_state.get('language', 'PT-BR') == 'PT-BR' else 1,
                key="lang_radio",
                on_change=_muda_idioma,
                horizontal=True, 
                label_visibility="collapsed"
            )
                
    status_bar_placeholder = st.empty()
    # Removemos o HTML do layout inicial porque o render final dos badges ocorre lá embaixo
    status_bar_placeholder.markdown("<div style='border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 10px; margin-bottom: 10px;'></div>", unsafe_allow_html=True)

    # Recupera ou inicializa a fonte da verdade para o modo atual
    if 'last_modo_visao' not in st.session_state:
        st.session_state.last_modo_visao = "mode_1"
    else:
        # Fallback caso last_modo_visao seja uma string traduzida em vez de key
        if st.session_state.last_modo_visao not in ["mode_1", "mode_2", "mode_3", "mode_4"]:
            for k in ["mode_1", "mode_2", "mode_3", "mode_4"]:
                if st.session_state.last_modo_visao == i18n.t(k):
                    st.session_state.last_modo_visao = k
                    break

    # Se o widget de rádio existe na sessão, confiamos nele. 
    # Se o usuário trocou o modo, a chave 'modo_visao_radio' já estará atualizada antes desta linha rodar.
    if "modo_visao_radio" in st.session_state:
        if st.session_state.modo_visao_radio in ["mode_1", "mode_2", "mode_3", "mode_4"]:
            st.session_state.last_modo_visao = st.session_state.modo_visao_radio
    else:
        # Se não existe, o Streamlit perdeu o estado (bug do unmount do popover). Restauramos do backup.
        st.session_state["modo_visao_radio"] = st.session_state.last_modo_visao

    current_mode_for_layout = st.session_state.last_modo_visao
        
    if current_mode_for_layout == "mode_3":
        col_menu_global = st.container()
        col_menu_especifico = st.container()
    else:
        col_menu_global, col_menu_especifico = st.columns(2)
        
    with col_menu_global.popover(i18n.t('modes_and_explanations'), use_container_width=True):
        st.markdown(f"<h4 style='margin:0; margin-bottom:10px; font-size:1.1rem; color:#ccc;'>{i18n.t('view_modes')}</h4>", unsafe_allow_html=True)
        opcoes_modos_keys = ["mode_1", "mode_2", "mode_3", "mode_4"]

                    
        modo_visao_key = st.radio(
            i18n.t("nav_analytic"),
            opcoes_modos_keys,
            format_func=lambda x: i18n.t(x),
            key="modo_visao_radio",
            horizontal=False,
            label_visibility="collapsed"
        )
        modo_visao = i18n.t(modo_visao_key)
        
        if st.session_state.last_modo_visao != modo_visao_key:
            analytics.log_event("change_mode", {"mode": modo_visao_key})
            st.session_state.last_modo_visao = modo_visao_key
            
        st.divider()
        
        show_exp = st.toggle(i18n.t("explanation_mode"), key="show_explanations")
        if 'last_show_exp' not in st.session_state:
            st.session_state.last_show_exp = show_exp
        if st.session_state.last_show_exp != show_exp:
            analytics.log_event("toggle_explanations", {"enabled": show_exp})
            st.session_state.last_show_exp = show_exp
            
        if st.session_state.get('show_explanations', False):
            tone = st.radio(i18n.t("reading_tone"), ["tecnico", "leigo"], format_func=lambda x: i18n.t("tone_academic") if x == "tecnico" else i18n.t("tone_layman"), horizontal=True, label_visibility="collapsed", key="explanation_tone")
            if 'last_tone' not in st.session_state:
                st.session_state.last_tone = tone
            if st.session_state.last_tone != tone:
                analytics.log_event("toggle_explanations", {"tone": tone})
                st.session_state.last_tone = tone
        
    is_sample_biased_global = False
    
    # --- CONTROLES SUPERIORES (APENAS EXPLORADOR INDIVIDUAL) ---
    if modo_visao == i18n.t("mode_1"):
        with col_menu_especifico.popover(i18n.t("config_analytic"), use_container_width=True):
            col1, col2, col3 = st.columns([1, 1, 1.5])
            
            with col1:
                cenario_sel = st.selectbox(i18n.t("select_scenario"), opcoes_cenarios, format_func=lambda x: i18n.t(x), key="cenario_sel")
                df_cenario = mapa_cenarios.get(cenario_sel)
                cargos_disponiveis = df_cenario['Carreira'].tolist() if df_cenario is not None and 'Carreira' in df_cenario.columns else (df_cenario.index.tolist() if df_cenario is not None else [])
                
                cientifica_keywords = ["Perito", "Médico", "Fotógrafo", "Desenhista", "Necropsia", "Necrópsia", "Atendente"]
                cargos_cientifica = [c for c in cargos_disponiveis if any(k in c for k in cientifica_keywords)]
                cargos_pc = [c for c in cargos_disponiveis if c not in cargos_cientifica]
                
            with col2:
                opcoes_grupos = ["filter_all", "filter_no_cientifica", "filter_only_cientifica", "filter_custom"]
                grupo_sel = st.selectbox(
                    i18n.t("fast_filter"),
                    opcoes_grupos,
                    format_func=lambda x: i18n.t(x),
                    key="grupo_sel"
                )
                
                if grupo_sel == "filter_all":
                    default_cargos = cargos_disponiveis
                elif grupo_sel == "filter_no_cientifica":
                    default_cargos = cargos_pc
                elif grupo_sel == "filter_only_cientifica":
                    default_cargos = cargos_cientifica
                else:
                    default_cargos = []
                    
                incluir_comuns = st.checkbox(i18n.t("include_generic"), value=False)
                
            with col1:
                opcoes_matriz = ["condensed", "original"]
                tipo_matriz_raw = st.selectbox(
                    i18n.t("matrix_format"), 
                    opcoes_matriz, 
                    format_func=lambda x: i18n.t(x),
                    disabled=incluir_comuns,
                    key="tipo_matriz_raw"
                )
                tipo_matriz = "Original" if "original" in tipo_matriz_raw or incluir_comuns else "Condensada"
                
            with col2:
                expandir_textos = st.checkbox(i18n.t("expand_texts"), value=True)
                
                traduzir_cargos = st.session_state.get('language', 'PT-BR') == 'EN'
                
            with col3:
                if 'last_cenario_sel' not in st.session_state:
                    st.session_state.last_cenario_sel = cenario_sel
                if 'last_grupo_sel' not in st.session_state:
                    st.session_state.last_grupo_sel = grupo_sel
                
                if st.session_state.last_cenario_sel != cenario_sel or st.session_state.last_grupo_sel != grupo_sel:
                    st.session_state.filtro_cargos = default_cargos
                    st.session_state.last_cenario_sel = cenario_sel
                    st.session_state.last_grupo_sel = grupo_sel

                filtro_cargos = st.multiselect(
                    i18n.t("roles_analyze"), 
                    cargos_disponiveis,
                    default=default_cargos,
                    format_func=lambda x: i18n.traduzir_cargo(x) if st.session_state.get('language', 'PT-BR') == 'EN' else x,
                    key="filtro_cargos"
                )
                
                if 'last_filtro_cargos' not in st.session_state:
                    st.session_state.last_filtro_cargos = filtro_cargos
                if st.session_state.last_filtro_cargos != filtro_cargos:
                    analytics.log_event("filter_change", {"filter": "cargos", "values": filtro_cargos})
                    st.session_state.last_filtro_cargos = filtro_cargos

                cargos_destaque = st.multiselect(
                    i18n.t("visual_highlight"),
                    filtro_cargos if filtro_cargos else cargos_disponiveis,
                    format_func=lambda x: i18n.traduzir_cargo(x) if st.session_state.get('language', 'PT-BR') == 'EN' else x,
                    key="cargos_destaque"
                )
                
                if cargos_destaque:
                    css_tags = ""
                    for cargo in cargos_destaque:
                        css_tags += f'''
                        span[data-baseweb="tag"][aria-label^="{cargo}"] {{
                            background-color: rgba(255, 152, 0, 0.3) !important;
                            border: 1px solid #ff9800 !important;
                        }}
                        span[data-baseweb="tag"][aria-label^="{cargo}"] span {{
                            color: #ffb74d !important;
                        }}
                        '''
                    st.markdown(f"<style>{css_tags}</style>", unsafe_allow_html=True)
                    
            if 'filtro_cargos' in locals() and 'cargos_disponiveis' in locals():
                if filtro_cargos and len(filtro_cargos) < len(cargos_disponiveis):
                    is_sample_biased_global = True

    elif modo_visao == i18n.t("mode_2"):
        traduzir_cargos = st.session_state.get('language', 'PT-BR') == 'EN'
        with col_menu_especifico.popover(i18n.t("config_compare"), use_container_width=True):
            col_a, col_b = st.columns(2)
            cenario_a = col_a.selectbox(i18n.t("scenario_a"), opcoes_cenarios, index=0, format_func=lambda x: i18n.t(x), key="cenario_a_sel")
            cenario_b = col_b.selectbox(i18n.t("scenario_b"), opcoes_cenarios, index=1, format_func=lambda x: i18n.t(x), key="cenario_b_sel")
            
            df_a = mapa_cenarios.get(cenario_a)
            if df_a is not None and 'Carreira' in df_a.columns:
                cargos_base = df_a['Carreira'].tolist()
            else:
                cargos_base = df_a.index.tolist() if df_a is not None else []
                
            col_c, col_d = st.columns(2)
            carreira_sel_comparativo = col_c.selectbox(i18n.t("career_detail"), cargos_base, index=None, placeholder=i18n.t("none_overview"), format_func=lambda x: i18n.traduzir_cargo(x) if traduzir_cargos else x, key="carreira_sel_comparativo_sel")
            cargos_destaque_2 = col_d.multiselect(i18n.t("visual_highlight"), cargos_base, help=i18n.t("highlight_help"), format_func=lambda x: i18n.traduzir_cargo(x) if traduzir_cargos else x, key="cargos_destaque_2_sel")
            
        if carreira_sel_comparativo:
            import json
            with open('csv_dump.json', 'r', encoding='utf-8') as f:
                mapa_dict = json.load(f)
            cargo_foco_b = carreira_sel_comparativo
            for row in mapa_dict:
                val_a = row.get(cenario_a)
                if val_a == "Investigador de Polícia (+ Agente de Telecomunicações Policial + Agente Policial + Carcereiro Policial)":
                    val_a = "Investigador de Polícia (+ Apoio)"
                if val_a == carreira_sel_comparativo:
                    val_b = row.get(cenario_b)
                    if val_b == "Investigador de Polícia (+ Agente de Telecomunicações Policial + Agente Policial + Carcereiro Policial)":
                        val_b = "Investigador de Polícia (+ Apoio)"
                    cargo_foco_b = val_b
                    break
            # translate for tracking badge if needed
            c_sel_trans = i18n.traduzir_cargo(carreira_sel_comparativo) if traduzir_cargos else carreira_sel_comparativo
            c_foco_trans = i18n.traduzir_cargo(cargo_foco_b) if traduzir_cargos else cargo_foco_b
            rastreio_html = f"<div title='{i18n.t('tracking_title')}' style='cursor: help; background: rgba(0, 114, 178, 0.2); border: 1px solid #0072B2; padding: 6px 15px; border-radius: 8px; font-size: 0.85rem; color: #E0E0E0; width: 100%; margin-top: 5px;'>{i18n.t('tracking_main')} <strong style='color: #4da6ff;'>{c_sel_trans}</strong> ({i18n.t(cenario_a)}) ➔ <strong style='color: #4da6ff;'>{c_foco_trans}</strong> ({i18n.t(cenario_b)}) <span style='float:right'>ℹ️</span></div>"
        else:
            rastreio_html = ""
            
        badge_destaque_2 = ""
        if cargos_destaque_2:
            str_dest_2 = ", ".join([i18n.traduzir_cargo(c).replace(' de Polícia', '').replace(' Policial', '') if traduzir_cargos else c.replace(' de Polícia', '').replace(' Policial', '') for c in cargos_destaque_2])
            badge_destaque_2 = f" <div class='status-badge' style='background: rgba(255, 152, 0, 0.2); border: 1px solid rgba(255, 152, 0, 0.5); color: #ffb74d;'>{i18n.t('highlights_lbl')} <strong>{str_dest_2}</strong></div>"

        badge_vies_html = f"<div class='status-badge' style='background: rgba(220, 53, 69, 0.2); border: 1px solid rgba(220, 53, 69, 0.5); color: #ff6b6b;'>{i18n.t('badge_bias')}</div>" if is_sample_biased_global else ""
        status_bar_placeholder.markdown(f"""
        <div id='sticky-header-anchor'></div>
        <div style='display: flex; flex-direction: column;'>
            <div style='display: flex; justify-content: space-between; align-items: flex-end; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 10px; margin-bottom: 5px; flex-wrap: wrap; gap: 10px;'>
                <div style='display: flex; gap: 5px; flex-wrap: wrap;'>{badge_vies_html}
                    <div class='status-badge' title='{i18n.t("mode2_tooltip")}' style='cursor: help;'>{i18n.t("badge_mode")} <strong>{i18n.t("mode_2").split(". ")[1]}</strong> <span style='font-size:0.7rem'>ℹ️</span></div>
                    <div class='status-badge' title='{i18n.t("scenario_origin_tooltip")}' style='cursor: help;'>{i18n.t("badge_scenario_a")}<strong>{i18n.t(cenario_a)}</strong></div>
                    <div class='status-badge' title='{i18n.t("scenario_dest_tooltip")}' style='cursor: help;'>{i18n.t("badge_scenario_b")}<strong>{i18n.t(cenario_b)}</strong></div>{badge_destaque_2}
                </div>
            </div>
            {rastreio_html}
        </div>
        """, unsafe_allow_html=True)
            
    # --- CONTROLES MODO 3 ---
    elif modo_visao == i18n.t("mode_3"):
        badge_vies_html = f"<div class='status-badge' style='background: rgba(220, 53, 69, 0.2); border: 1px solid rgba(220, 53, 69, 0.5); color: #ff6b6b;'>{i18n.t('badge_bias')}</div>" if is_sample_biased_global else ""
        status_bar_placeholder.markdown(f"""
        <div id='sticky-header-anchor'></div>
        <div style='display: flex; justify-content: space-between; align-items: flex-end; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 10px; margin-bottom: 10px; flex-wrap: wrap; gap: 10px;'>
            <div style='display: flex; gap: 5px; flex-wrap: wrap;'>{badge_vies_html}
                <div class='status-badge'>{i18n.t('badge_mode_3')}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # --- CONTROLES MODO 4 ---
    elif modo_visao == i18n.t("mode_4"):
        import json
        import os
        cargos_base_long = []
        try:
            if os.path.exists('csv_dump.json'):
                with open('csv_dump.json', 'r', encoding='utf-8') as f:
                    lista_mapa = json.load(f)
                    cargos_base_long = [row['Atual Sem Correção'] for row in lista_mapa]
        except Exception:
            pass
            
        with col_menu_especifico.popover(i18n.t("m4_config_title"), use_container_width=True):
            st.markdown(f"<p style='margin-top:-10px; color:#aaa; font-size:0.9rem;'>{i18n.t('m4_config_desc')}</p>", unsafe_allow_html=True)
            filtro_cargos_long = st.multiselect(
                i18n.t("m4_filter_roles"), 
                cargos_base_long, 
                default=cargos_base_long,
                format_func=lambda x: i18n.traduzir_cargo(x) if st.session_state.get('language', 'PT-BR') == 'EN' else x
            )
            cargos_destaque_long = st.multiselect(
                i18n.t("m4_highlight_roles"), 
                cargos_base_long, 
                help=i18n.t("m4_highlight_help"),
                format_func=lambda x: i18n.traduzir_cargo(x) if st.session_state.get('language', 'PT-BR') == 'EN' else x
            )
            
        if 'filtro_cargos_long' in locals() and 'cargos_base_long' in locals():
            if filtro_cargos_long and len(filtro_cargos_long) < len(cargos_base_long):
                is_sample_biased_global = True

        badge_vies_html = f"<div class='status-badge' style='background: rgba(220, 53, 69, 0.2); border: 1px solid rgba(220, 53, 69, 0.5); color: #ff6b6b;'>{i18n.t('badge_bias')}</div>" if is_sample_biased_global else ""
        status_bar_placeholder.markdown(f"""
        <div id='sticky-header-anchor'></div>
        <div style='display: flex; justify-content: space-between; align-items: flex-end; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 10px; margin-bottom: 10px; flex-wrap: wrap; gap: 10px;'>
            <div style='display: flex; gap: 5px; flex-wrap: wrap;'>{badge_vies_html}
                <div class='status-badge'>{i18n.t('badge_mode_4')}</div>
                <div class='status-badge'>{i18n.t('badge_filtered_roles')} <strong>{len(filtro_cargos_long)}</strong></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Navegação Interna Condicional (Substitui as bolinhas flutuantes)
    st.markdown("<div style='margin-top: 5px;'></div>", unsafe_allow_html=True)
    
    if modo_visao == i18n.t("mode_1"):
        nav_options = ["sub_matrix", "sub_adj", "sub_dyn", "sub_graph", "sub_gower", "sub_ruler", "sub_dendro", "sub_upset"]
    elif modo_visao == i18n.t("mode_2"):
        nav_options = ["sub_delta_title", "sub_dist_title", "sub_flow_title", "sub_radar_title", "sub_network_comp_title", "sub_tree_comp_title"]
    elif modo_visao == i18n.t("mode_3"):
        nav_options = ["m3_sub_gower_title", "m3_sub_vol_title", "m3_sub_share_title", "m3_sub_coph_title"]
    else:
        nav_options = ["m4_sub_volume_title", "m4_sub_exclusive_title", "m4_sub_shared_title", "m4_sub_adj_title", "m4_sub_gower_title", "m4_sub_neighbor_title"]
        
    current_section = st.radio(
        "📍 Navegação Rápida:" if st.session_state.get('language', 'PT-BR') == 'PT-BR' else "📍 Quick Navigation:", 
        options=nav_options, 
        format_func=lambda x: i18n.t(x),
        key=f"nav_section_radio_{modo_visao}",
        horizontal=True,
        help="Escolha uma seção para visualizá-la. O sistema carregará apenas a seção escolhida para economizar recursos e agilizar sua navegação." if st.session_state.get('language', 'PT-BR') == 'PT-BR' else "Choose a section to view. The system will load only the selected section to save resources and speed up your navigation."
    )

if is_sample_biased_global:
    st.warning(explanations.get_bias_warning(language=st.session_state.get('language', 'PT-BR')), icon="⚠️")

if modo_visao == i18n.t("mode_2"):
    with st.spinner("⏳ Carregando visão..." if st.session_state.get('language', 'PT-BR') == 'PT-BR' else "⏳ Loading view..."):
        import comparative_view
        import importlib
        importlib.reload(comparative_view)
        comparative_view.render_comparativo_axb(opcoes_cenarios, mapa_cenarios, cenario_a, cenario_b, carreira_sel_comparativo, cargos_destaque_2, current_section)
elif modo_visao == i18n.t("mode_3"):
    with st.spinner("⏳ Carregando visão..." if st.session_state.get('language', 'PT-BR') == 'PT-BR' else "⏳ Loading view..."):
        import timeline_view
        import importlib
        importlib.reload(timeline_view)
        timeline_view.render_timeline_mode(opcoes_cenarios, mapa_cenarios, current_section)
elif modo_visao == i18n.t("mode_4"):
    with st.spinner("⏳ Carregando visão..." if st.session_state.get('language', 'PT-BR') == 'PT-BR' else "⏳ Loading view..."):
        import longitudinal_view
        import importlib
        importlib.reload(longitudinal_view)
        longitudinal_view.render_longitudinal_mode(opcoes_cenarios, mapa_cenarios, filtro_cargos_long, cargos_destaque_long, current_section)

# Registrar log invisível de visita
if 'visit_logged' not in st.session_state:
    cenario_para_log = cenario_sel if 'cenario_sel' in locals() else modo_visao
    logger.log_visit(cenario_para_log)

if modo_visao == i18n.t("mode_1") and df_cenario is not None and not df_cenario.empty:
    with st.spinner("⏳ Carregando visão..." if st.session_state.get('language', 'PT-BR') == 'PT-BR' else "⏳ Loading view..."):
        # Higienização de Nomes Longos que quebram a interface
        if 'Carreira' in df_cenario.columns:
            df_cenario['Carreira'] = df_cenario['Carreira'].replace({
                "Investigador de Polícia (+ Agente de Telecomunicações Policial + Agente Policial + Carcereiro Policial)": "Investigador de Polícia (+ Apoio)"
            })

        # Aplicação de Filtros de Cargos
        if filtro_cargos:
            if 'Carreira' in df_cenario.columns:
                df_cenario = df_cenario[df_cenario['Carreira'].isin(filtro_cargos)]
            else:
                df_cenario = df_cenario.loc[filtro_cargos]
                
        # Processamento Matemático Principal
        if incluir_comuns:
            col_sums = df_cenario.sum(axis=0)
            num_reais = len(df_cenario)
            colunas_comuns = df_cenario.columns[col_sums == num_reais].tolist()
            colunas_outras = [c for c in df_cenario.columns if c not in colunas_comuns]
            df_original_limpo = df_cenario[colunas_comuns + colunas_outras].copy()
            df_condensado = df_original_limpo
        else:
            df_original_limpo = data_processing.remover_atribuicoes_comuns(df_cenario)
            df_condensado, historico = data_processing.condensar_dataframe(df_cenario)
        
        # Switch Lógico
        df_to_use = df_original_limpo if tipo_matriz == "Original" else df_condensado
        
        # Ocultar coluna de atribuições não encontradas (se existir)
        if "NÃO ENCONTRADAS ATRIBUIÇÕES" in df_to_use.columns:
            df_to_use = df_to_use.drop(columns=["NÃO ENCONTRADAS ATRIBUIÇÕES"])
        
        
        if st.session_state.get('language', 'PT-BR') == 'EN' and traduzir_cargos:
            # Traduz índice (cargos) do df_to_use
            df_to_use.index = [i18n.traduzir_cargo(c) for c in df_to_use.index]
            # Traduz colunas (atribuições) do df_to_use
            df_to_use.columns = [i18n.traduzir_atribuicao(c) for c in df_to_use.columns]
            
            if 'Carreira' in df_to_use.columns:
                df_to_use['Carreira'] = df_to_use['Carreira'].map(lambda c: i18n.traduzir_cargo(c))
            
            # Traduz filtro_cargos e cargos_destaque dinamicamente para os gráficos e tabelas
            filtro_cargos_ui = [i18n.traduzir_cargo(c) for c in filtro_cargos] if filtro_cargos else []
            cargos_destaque_ui = [i18n.traduzir_cargo(c) for c in cargos_destaque] if cargos_destaque else []
            cargos_disponiveis_ui = [i18n.traduzir_cargo(c) for c in cargos_disponiveis]
        else:
            filtro_cargos_ui = filtro_cargos
            cargos_destaque_ui = cargos_destaque
            cargos_disponiveis_ui = cargos_disponiveis
    
    # Siglas e Textos
    dic_siglas = data_processing.gerar_dicionario_siglas(df_to_use.columns)
    dic_reverso = {v: k for k, v in dic_siglas.items()}

    df_to_use_siglas = data_processing.aplicar_siglas_dataframe(df_to_use, dic_siglas)
    text_matrix = data_processing.obter_atribuicoes_comuns_textuais(df_to_use, dic_siglas, expandir_textos)
    adj_matrix = data_processing.gerar_matriz_adjacencia(df_to_use)
    
    df_para_gower = df_to_use.copy()
    if incluir_comuns:
        num_cargos_reais = len(df_para_gower)
        numeric_cols = df_para_gower.select_dtypes(include='number').columns
        pseudo_row = (df_para_gower[numeric_cols].sum(axis=0) == num_cargos_reais).astype(int)
        if 'Carreira' in df_para_gower.columns:
            pseudo_row['Carreira'] = "Policial Civil (todos os cargos)"
        pseudo_row.name = "Policial Civil (todos os cargos)"
        df_para_gower.loc[pseudo_row.name] = pseudo_row
        
    metric_options = {
        'gower': i18n.t("metric_gower", default="Distância de Gower (usado no artigo - ver Errata)"),
        'jaccard': i18n.t("metric_jaccard", default="Jaccard (Assimétrica)"),
        'sokalsneath': i18n.t("metric_sokal", default="Sokal & Sneath"),
        'dice': i18n.t("metric_dice", default="Sørensen-Dice / Gower & Legendre 2"),
        'overlap': i18n.t("metric_overlap", default="Overlap Coefficient (Szymkiewicz–Simpson)"),
        'cosine': i18n.t("metric_cosine", default="Cosine Similarity (Ochiai)")
    }
    # --- INJEÇÃO DO HEADER COMBINADO (Título + Status) ---
    lbl_cargos = f"{i18n.t('filter_all')}" if not filtro_cargos else f"{len(filtro_cargos)} {i18n.t('lbl_selected')}"
    lbl_genericas = i18n.t("lbl_on") if incluir_comuns else i18n.t("lbl_off")
    lbl_textos = i18n.t("lbl_on") if expandir_textos else i18n.t("lbl_off")
    
    lista_cargos_html = ""
    if filtro_cargos and len(filtro_cargos) < len(cargos_disponiveis):
        lista_cargos_html = f"<div style='text-align: right; color: #C0C0C0; font-size: 0.9rem; margin-top: 5px; margin-bottom: 5px;'><strong>{i18n.t('badge_filtered_careers')}</strong> {', '.join(filtro_cargos)}</div>"
    
    badge_destaque = ""
    if cargos_destaque:
        str_dest = ", ".join([c.replace(' de Polícia', '').replace(' Policial', '') for c in cargos_destaque])
        badge_destaque = f" <div class='status-badge' style='background: rgba(255, 152, 0, 0.2); border: 1px solid rgba(255, 152, 0, 0.5); color: #ffb74d;'>🎨 Destaques: <strong>{str_dest}</strong></div>"

    badge_vies_html = f"<div class='status-badge' style='background: rgba(220, 53, 69, 0.2); border: 1px solid rgba(220, 53, 69, 0.5); color: #ff6b6b;'>{i18n.t('warning_bias')}</div>" if is_sample_biased_global else ""
    header_html = f"""
<div style='display: flex; gap: 5px; flex-wrap: wrap; padding-bottom: 10px; margin-bottom: 10px; border-bottom: 1px solid rgba(255,255,255,0.1);'>
{badge_vies_html}
<div class='status-badge'>{i18n.t('badge_scenario')} <strong>{i18n.t(cenario_sel)}</strong></div>
<div class='status-badge'>{i18n.t('badge_matrix')} <strong>{i18n.t('lbl_original') if tipo_matriz == 'Original' else i18n.t('lbl_condensed')}</strong></div>
<div class='status-badge'>{i18n.t('badge_generic')} <strong>{lbl_genericas}</strong></div>
<div class='status-badge'>{i18n.t('badge_texts')} <strong>{lbl_textos}</strong></div>
<div class='status-badge'>{i18n.t('badge_roles')} <strong>{lbl_cargos}</strong></div>{badge_destaque}
</div>
{lista_cargos_html}
"""
    status_bar_placeholder.markdown(header_html, unsafe_allow_html=True)

    # --- INJEÇÃO DOS KPIs DENTRO DA GAVETA ---
    is_sample_biased = filtro_cargos and len(filtro_cargos) < len(cargos_disponiveis)

    reducao = len(df_original_limpo.columns) - len(df_condensado.columns)
    pct_reducao = (reducao / len(df_original_limpo.columns)) * 100 if len(df_original_limpo.columns) > 0 else 0
    
    html_kpis = f"""
<div style="display: flex; justify-content: space-between; flex-wrap: wrap; gap: 10px; margin-top: 10px;">
<div style="flex: 1; min-width: 140px; text-align: center; background: #1E1E1E; padding: 10px; border-radius: 8px; border: 1px solid #333;" title="{i18n.t('kpi_orig_help')}">
<div style="font-size: 0.65rem; color: #9E9E9E; font-weight: 600; text-transform: uppercase;">{i18n.t('kpi_orig_title')} <span style="cursor:help; color:#888; font-size:0.75rem;">ⓘ</span></div>
<div style="font-size: 1.1rem; line-height: 1.2;">{len(df_original_limpo.columns)}</div>
</div>
<div style="flex: 1; min-width: 140px; text-align: center; background: #1E1E1E; padding: 10px; border-radius: 8px; border: 1px solid #333;" title="{i18n.t('kpi_cond_help')}">
<div style="font-size: 0.65rem; color: #9E9E9E; font-weight: 600; text-transform: uppercase;">{i18n.t('kpi_cond_title')} <span style="cursor:help; color:#888; font-size:0.75rem;">ⓘ</span></div>
<div style="font-size: 1.1rem; line-height: 1.2;">{len(df_condensado.columns)}</div>
</div>
<div style="flex: 1; min-width: 140px; text-align: center; background: #1E1E1E; padding: 10px; border-radius: 8px; border: 1px solid #333;" title="{i18n.t('kpi_red_help')}">
<div style="font-size: 0.65rem; color: #9E9E9E; font-weight: 600; text-transform: uppercase;">{i18n.t('kpi_red_title')} <span style="cursor:help; color:#888; font-size:0.75rem;">ⓘ</span></div>
<div style="font-size: 1.1rem; color: #00C851; line-height: 1.2; font-weight: bold;">{reducao}</div>
</div>
<div style="flex: 1; min-width: 140px; text-align: center; background: #1E1E1E; padding: 10px; border-radius: 8px; border: 1px solid #333;" title="{i18n.t('kpi_pct_help')}">
<div style="font-size: 0.65rem; color: #9E9E9E; font-weight: 600; text-transform: uppercase;">{i18n.t('kpi_pct_title')} <span style="cursor:help; color:#888; font-size:0.75rem;">ⓘ</span></div>
<div style="font-size: 1.1rem; color: #00C851; line-height: 1.2; font-weight: bold;">{pct_reducao:.1f}%</div>
</div>
</div>
"""

    # 1.1. Matriz de Atribuições
    if current_section == 'sub_matrix':
        with st.expander(i18n.t('expander_math')):
            st.markdown(i18n.t('expander_math_text'))
            
        if st.session_state.get('language', 'PT-BR') == 'EN':
            with st.expander("📚 Brazilian Police Roles Glossary"):
                st.markdown("""
                **Roles Translation (Approximations):**
                - **Delegado de Polícia**: Police Chief / Police Delegate
                - **Investigador de Polícia**: Police Investigator / Detective
                - **Escrivão de Polícia**: Police Clerk / Desk Officer
                - **Agente Policial**: Police Agent / Operative
                - **Carcereiro Policial**: Police Jailer
                - **Agente de Telecomunicações Policial**: Police Telecommunications Agent / Dispatcher
                - **Papiloscopista Policial**: Fingerprint Examiner / Dactyloscopist
                - **Auxiliar de Papiloscopista Policial**: Fingerprint Examiner Assistant
                - **Perito Criminal**: Forensic Expert / Criminalist
                - **Médico Legista**: Medical Examiner / Forensic Pathologist
                - **Fotógrafo Técnico-Pericial**: Forensic Photographer
                - **Desenhista Técnico-Pericial**: Forensic Sketch Artist
                - **Atendente de Necrotério Policial**: Morgue Attendant
                - **Auxiliar de Necropsia**: Autopsy Assistant
                
                *(Note: 'Odontolegista' is not listed separately here because it's functionally merged within Medical Examiner and Forensic Expert duties in this dataset).*
                """)
            
            with st.expander("📖 Assignments Translation Table"):
                st.markdown("Below are the available translations for the assignments in the active dataset.")
                df_translations = pd.DataFrame(list(i18n.dic_traducao_atribuicoes.items()), columns=["Portuguese (PT-BR)", "English (US-EN)"])
                st.dataframe(df_translations, use_container_width=True, hide_index=True)
    
        st.markdown(html_kpis, unsafe_allow_html=True)
    
        if is_sample_biased:
            st.warning(explanations.get_short_bias_warning(language=st.session_state.get('language', 'PT-BR')), icon="🚨")
        st.markdown("<div id='toc-matrix'></div>", unsafe_allow_html=True)
        st.subheader(f"{i18n.t('sub_matrix')} ({i18n.t('lbl_original') if tipo_matriz == 'Original' else i18n.t('lbl_condensed')})", help=i18n.t('sub_matrix_help'))
        st.markdown(f"<p style='font-size: 0.85rem; color: #9E9E9E; margin-top: -15px; margin-bottom: 10px;'>{i18n.t('tip_hover')}</p>", unsafe_allow_html=True)
        lbl_matriz_translated = i18n.t('lbl_original') if tipo_matriz == 'Original' else i18n.t('lbl_condensed')
        fig_bin = visualizations.plot_binary_heatmap(df_to_use_siglas, f"{i18n.t('title_matrix_prefix')} {lbl_matriz_translated} - {i18n.t(cenario_sel)}", colorscale="Teal", dic_reverso=dic_reverso, cargos_destaque=cargos_destaque_ui)
        st.plotly_chart(fig_bin, use_container_width=True)
        if st.session_state.get('show_explanations', False):
            tone_key = st.session_state.get('explanation_tone', 'tecnico')
            st.info(explanations.get_explanation("matriz", tone_key, language=st.session_state.get('language', 'PT-BR')))
        if 'interaction_ui' in locals(): interaction_ui.render_like_button("1.1 Matriz de Atribuicoes", "1_1")

    
    # 1.2. Matriz de Adjacência
    elif current_section == 'sub_adj':
        if is_sample_biased:
            st.warning(explanations.get_short_bias_warning(language=st.session_state.get('language', 'PT-BR')), icon="🚨")
        st.markdown("<div id='toc-adj'></div>", unsafe_allow_html=True)
        st.subheader(i18n.t('sub_adj'), help=i18n.t('sub_adj_help'))
        
        # Prepara Top Pairs
        adj_matrix_copy = adj_matrix.copy()
        adj_matrix_copy.index.name = 'Cargo 1'
        adj_matrix_copy.columns.name = 'Cargo 2'
        pairs = adj_matrix_copy.stack().reset_index()
        pairs.columns = ['Cargo 1', 'Cargo 2', 'Compartilhamentos']
        pairs = pairs[pairs['Cargo 1'] != pairs['Cargo 2']]
        pairs['Pair'] = pairs.apply(lambda row: " - ".join(sorted([row['Cargo 1'], row['Cargo 2']])), axis=1)
        pairs = pairs.drop_duplicates(subset=['Pair'])
    
        
        # Prepara Connectivity KPIs
        import numpy as np
        # A diagonal principal contém a auto-interseção (total de atribuições do próprio cargo)
        # Para o grau de conectividade, subtraímos a diagonal da soma total da linha.
        degrees = adj_matrix.sum(axis=1) - pd.Series(np.diag(adj_matrix), index=adj_matrix.index)
        
        most_connected = degrees.idxmax()
        max_degree = int(degrees.max())
        least_connected = degrees.idxmin()
        min_degree = int(degrees.min())
        
        if st.session_state.get('language', 'PT-BR') == 'EN' and traduzir_cargos:
            most_connected = i18n.traduzir_cargo(most_connected)
            least_connected = i18n.traduzir_cargo(least_connected)
            
        # 1. KPIs Full Width
        st.markdown(f"<h4 style='margin-bottom: 15px; color:#ccc; font-size: 1.1rem;'>{i18n.t('adj_kpi_title')}</h4>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style="display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 25px;">
            <div style="flex: 1; min-width: 120px; background: #1E1E1E; padding: 10px; border-radius: 8px; border: 1px solid #333;">
                <div style="font-size: 0.65rem; color: #9E9E9E; text-transform: uppercase;">{i18n.t('adj_kpi_hub')}</div>
                <div style="font-size: 0.9rem; font-weight: bold; color: #4da6ff; margin-bottom: 3px;">{most_connected}</div>
                <div style="font-size: 0.75rem; color: #aaa;">{max_degree} {i18n.t('adj_kpi_connections')}</div>
            </div>
            <div style="flex: 1; min-width: 120px; background: #1E1E1E; padding: 10px; border-radius: 8px; border: 1px solid #333;">
                <div style="font-size: 0.65rem; color: #9E9E9E; text-transform: uppercase;">{i18n.t('adj_kpi_isolated')}</div>
                <div style="font-size: 0.9rem; font-weight: bold; color: #ff6b6b; margin-bottom: 3px;">{least_connected}</div>
                <div style="font-size: 0.75rem; color: #aaa;">{min_degree} {i18n.t('adj_kpi_connections')}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
            
        # 2. Columns for Heatmap and Table
        col_adj_1, col_adj_2 = st.columns([6, 4])
        
        with col_adj_1:
            fig_adj = visualizations.plot_adjacency_heatmap(adj_matrix, f"{i18n.t('title_adj_prefix')} - {i18n.t(cenario_sel)}", text_matrix=text_matrix, cargos_destaque=cargos_destaque_ui)
            st.plotly_chart(fig_adj, use_container_width=True)
            if st.session_state.get('show_explanations', False):
                tone_key = st.session_state.get('explanation_tone', 'tecnico')
                st.info(explanations.get_explanation("adjacencia", tone_key, language=st.session_state.get('language', 'PT-BR')))
            
        with col_adj_2:
            # Tabela Top Pares
            st.markdown(f"<p style='font-size: 0.9rem; margin-bottom: 5px; color:#ddd;'><strong>{i18n.t('adj_top_pairs')}</strong></p>", unsafe_allow_html=True)
            
            lbl_5 = "Top 5"
            lbl_10 = "Top 10"
            lbl_all = i18n.t("lbl_all", default="Todos")
            qtd_pares = st.selectbox("Quantidade:", [lbl_5, lbl_10, lbl_all], index=0, label_visibility="collapsed")
            
            limit_pairs = 5
            if qtd_pares == lbl_10:
                limit_pairs = 10
            elif qtd_pares == lbl_all:
                limit_pairs = len(pairs)
                
            top_pairs = pairs.sort_values(by='Compartilhamentos', ascending=False).head(limit_pairs)
            if st.session_state.get('language', 'PT-BR') == 'EN' and traduzir_cargos:
                top_pairs['Pair'] = top_pairs['Pair'].map(lambda x: " - ".join([i18n.traduzir_cargo(p) for p in x.split(" - ")]))
                
            df_top_pairs = top_pairs[['Pair', 'Compartilhamentos']].rename(columns={'Pair': i18n.t('adj_tbl_pair'), 'Compartilhamentos': i18n.t('adj_tbl_shared')})
            df_top_pairs.insert(0, '#', range(1, len(df_top_pairs) + 1))
            st.dataframe(df_top_pairs, use_container_width=True, hide_index=True)
            
        # 3. Gráfico Barras Full Width
        df_bar = degrees.reset_index()
        df_bar.columns = ['Cargo', 'Soma']
        if st.session_state.get('language', 'PT-BR') == 'EN' and traduzir_cargos:
            df_bar['Cargo'] = df_bar['Cargo'].map(lambda c: i18n.traduzir_cargo(c))
            
        import plotly.express as px
        fig_bar = px.bar(
            df_bar,
            x='Soma', 
            y='Cargo', 
            orientation='h',
            labels={'Soma': i18n.t('adj_tbl_shared'), 'Cargo': ''},
            title=f"<span style='font-size:0.95rem; color:#ccc'>{i18n.t('adj_bar_title')}</span>"
        )
        fig_bar.update_layout(
            plot_bgcolor='rgba(0,0,0,0)', 
            paper_bgcolor='rgba(0,0,0,0)', 
            font=dict(color='white'),
            margin=dict(l=0, r=0, t=40, b=0),
            height=300,
            yaxis={'categoryorder': 'total ascending'}
        )
        fig_bar.update_traces(marker_color='#4da6ff')
        st.plotly_chart(fig_bar, use_container_width=True)

        if 'interaction_ui' in locals(): interaction_ui.render_like_button("1.2 Matriz de Adjacencia", "1_2")

    # 1.3. Explorador Dinâmico
    elif current_section == 'sub_dyn':
        if is_sample_biased:
            st.warning(explanations.get_short_bias_warning(language=st.session_state.get('language', 'PT-BR')), icon="🚨")
        st.markdown("<div id='toc-dyn'></div>", unsafe_allow_html=True)
        st.subheader(i18n.t('sub_dyn'), help=i18n.t('sub_dyn_help'))
        
        df_explorer = df_original_limpo.set_index('Carreira') if 'Carreira' in df_original_limpo.columns else df_original_limpo.copy()
        if st.session_state.get('language', 'PT-BR') == 'EN' and traduzir_cargos:
            df_explorer.index = [i18n.traduzir_cargo(c) for c in df_explorer.index]
            df_explorer.columns = [i18n.traduzir_atribuicao(c) for c in df_explorer.columns]
            
        # Total de atribuições na base (para a porcentagem)
        total_atribuicoes_base = len(df_explorer.columns)
        
        aba1, aba2 = st.tabs([i18n.t("tab_roles"), i18n.t("tab_assignments")])
        
        with aba1:
            st.markdown(f"**{i18n.t('base_total')}** {total_atribuicoes_base} {i18n.t('base_desc')}")
            @st.cache_data(show_spinner=False)
            def carregar_tabela_conversao():
                try:
                    df_t = pd.read_excel('Tabela_Conversao_Cargos.xlsx')
                    if not df_t.empty and len(df_t.columns) > 1: return df_t
                except: pass
                
                for sep in [';', ',']:
                    for enc in ['utf-8', 'iso-8859-1', 'cp1252']:
                        try:
                            df_t = pd.read_csv('Tabela_Conversao_Cargos.CSV', sep=sep, encoding=enc)
                            if not df_t.empty and len(df_t.columns) > 1: return df_t
                        except: pass
                return None
    
            df_conv = carregar_tabela_conversao()
            
            def mapear_trio_base(old_sel_list, new_list, cenario_antigo, cenario_novo):
                if df_conv is None or df_conv.empty: return []
                
            cargos_default_aba1 = []
    
            if 'last_cenario_aba1' not in st.session_state:
                st.session_state.last_cenario_aba1 = cenario_sel
    
            # Hook de mudança de cenário (agora apenas limpa o filtro)
            mudou_cenario = st.session_state.last_cenario_aba1 != cenario_sel
            if mudou_cenario:
                st.session_state["filtro_cargos_aba1"] = []
                st.session_state.last_cenario_aba1 = cenario_sel
            filtro_cargos_explorador = st.multiselect(i18n.t("roles_label"), df_explorer.index.tolist(), default=cargos_default_aba1, key="filtro_cargos_aba1")
            if filtro_cargos_explorador:
                # Filtra e transpõe
                df_filtro = df_explorer.loc[filtro_cargos_explorador]
                colunas_ativas = df_filtro.columns[(df_filtro > 0).any()]
                df_resultado = df_filtro[colunas_ativas].T
                
                # Seletor de Visibilidade (Exclusivas vs Compartilhadas)
                op_todas = i18n.t("op_all")
                op_excl_selecao = i18n.t("op_excl")
                op_comp_fora = i18n.t("op_comp_out")
                op_comp_dentro = i18n.t("op_comp_in")
                
                tipo_exclusividade = st.radio(
                    i18n.t("filter_assignments"), 
                    [op_todas, op_excl_selecao, op_comp_fora, op_comp_dentro], 
                    horizontal=True
                )
                
                somas_globais = df_explorer[df_resultado.index].sum(axis=0)
                somas_selecao = df_resultado.sum(axis=1)
                
                if tipo_exclusividade == op_excl_selecao:
                    df_resultado = df_resultado[somas_globais == somas_selecao]
                elif tipo_exclusividade == op_comp_fora:
                    df_resultado = df_resultado[somas_globais > somas_selecao]
                elif tipo_exclusividade == op_comp_dentro:
                    df_resultado = df_resultado[somas_selecao > 1]
                    
                if len(filtro_cargos_explorador) > 1:
                    def status_compartilhamento(row):
                        if row.sum() == len(filtro_cargos_explorador):
                            return i18n.t("status_all")
                        elif row.sum() == 1:
                            return i18n.t("status_excl")
                        else:
                            return i18n.t("status_some")
                    df_resultado['Status'] = df_resultado.apply(status_compartilhamento, axis=1)
                    
                # Restaura Nomes
                df_resultado.index = [dic_reverso.get(col, col) for col in df_resultado.index]
                df_resultado.index.name = i18n.t("assignments_label").replace(":", "")
                
                # Mostra estatísticas de carga por cargo
                st.markdown(i18n.t("norm_weight"))
                stats = []
                for c in filtro_cargos_explorador:
                    qtd = df_filtro.loc[c].sum()
                    pct = (qtd / total_atribuicoes_base) * 100
                    stats.append({i18n.t("col_roles"): c, i18n.t("col_qtd"): int(qtd), i18n.t("col_rep"): f"{pct:.1f}%"})
                
                df_stats = pd.DataFrame(stats).set_index(i18n.t("col_roles"))
                
                def highlight_stats(row):
                    if cargos_destaque_ui and row.name in cargos_destaque_ui:
                        return ['background-color: rgba(255, 152, 0, 0.2); color: #ffb74d; font-weight: bold;'] * len(row)
                    return [''] * len(row)
                    
                st.dataframe(df_stats.style.apply(highlight_stats, axis=1), use_container_width=True)
                st.markdown(i18n.t("cross_table"))
                
                for c in filtro_cargos_explorador:
                    if c in df_resultado.columns:
                        df_resultado[c] = df_resultado[c].apply(lambda x: '✔️' if isinstance(x, (int, float)) and x > 0 else '❌' if isinstance(x, (int, float)) and x == 0 else x)
    
                def highlight_cruzamento(row):
                    styles = []
                    for col in df_resultado.columns:
                        if cargos_destaque_ui and col in cargos_destaque_ui:
                            if row[col] == '✔️':
                                styles.append('background-color: rgba(255, 152, 0, 0.25); color: #ffb74d; font-weight: bold;')
                            else:
                                styles.append('background-color: rgba(255, 152, 0, 0.05);')
                        else:
                            styles.append('')
                    return styles
    
                st.dataframe(df_resultado.style.apply(highlight_cruzamento, axis=1), use_container_width=True)
                
        with aba2:
            st.markdown(i18n.t("select_assignments_desc"))
            todas_atrib = df_explorer.columns.tolist()
            filtro_atrib = st.multiselect(i18n.t("assignments_label"), todas_atrib, key="filtro_atrib_aba2")
            if filtro_atrib:
                df_filtro_atrib = df_explorer[filtro_atrib].copy()
                df_filtro_atrib = df_filtro_atrib[(df_filtro_atrib > 0).any(axis=1)]
                df_filtro_atrib.columns = filtro_atrib
                df_filtro_atrib.index.name = i18n.t("roles_label").replace(":", "")
                
                for col in df_filtro_atrib.columns:
                    df_filtro_atrib[col] = df_filtro_atrib[col].apply(lambda x: '✔️' if isinstance(x, (int, float)) and x > 0 else '❌')
                    
                def highlight_aba2(row):
                    if cargos_destaque_ui and row.name in cargos_destaque_ui:
                        return ['background-color: rgba(255, 152, 0, 0.25); color: #ffb74d; font-weight: bold;' if v == '✔️' else 'background-color: rgba(255, 152, 0, 0.05);' for v in row]
                    return [''] * len(row)
    
                st.dataframe(df_filtro_atrib.style.apply(highlight_aba2, axis=1), use_container_width=True)
    
        if st.session_state.get('show_explanations', False):
            tone_key = st.session_state.get('explanation_tone', 'tecnico')
            st.info(explanations.get_explanation("explorador", tone_key, language=st.session_state.get('language', 'PT-BR')))
        if 'interaction_ui' in locals(): interaction_ui.render_like_button("1.3 Explorador Dinâmico", "1_3")


    # 1.4. Grafo de Similaridade
    elif current_section == 'sub_graph':
        if is_sample_biased:
            st.warning(explanations.get_short_bias_warning(language=st.session_state.get('language', 'PT-BR')), icon="🚨")
        st.markdown("<div id='toc-graph'></div>", unsafe_allow_html=True)
        st.subheader(i18n.t("sub_graph"), help=i18n.t("sub_graph_help"))
        threshold_adj = st.slider(i18n.t("threshold_adj"), min_value=1, max_value=15, value=1, step=1)
        nodes_data, edges_data, pos = data_processing.gerar_dados_grafo(adj_matrix, threshold=threshold_adj, text_matrix=text_matrix)
        fig_grafo = visualizations.plot_network_graph(nodes_data, edges_data, i18n.t("title_network").format(threshold=threshold_adj) + f" - {i18n.t(cenario_sel)}", cargos_destaque=cargos_destaque_ui)
        st.plotly_chart(fig_grafo, use_container_width=True)
        if st.session_state.get('show_explanations', False):
            tone_key = st.session_state.get('explanation_tone', 'tecnico')
            st.info(explanations.get_explanation("grafo", tone_key, language=st.session_state.get('language', 'PT-BR')))
        if 'interaction_ui' in locals(): interaction_ui.render_like_button("1.4 Grafo de Similaridade", "1_4")
    
    # 1.5. Mapa de Calor Gower
    elif current_section == 'sub_gower':
        if is_sample_biased:
            st.warning(explanations.get_short_bias_warning(language=st.session_state.get('language', 'PT-BR')), icon="🚨")
        st.markdown("<div id='toc-gower'></div>", unsafe_allow_html=True)
        st.subheader(i18n.t("sub_gower"), help=i18n.t("sub_gower_help"))
        
        selected_metric_key_15 = st.selectbox(
            i18n.t("select_metric", default="Selecione a Métrica de Similaridade"),
            list(metric_options.keys()),
            format_func=lambda x: metric_options[x],
            key="metric_selectbox_15"
        )
            
        df_gower_15 = data_processing.calcular_distancias(df_para_gower, metric=selected_metric_key_15)
        
        if st.session_state.get('language', 'PT-BR') == 'EN' and traduzir_cargos:
            df_gower_15.index = [i18n.dic_traducao_cargos.get(c, c) for c in df_gower_15.index]
            df_gower_15.columns = [i18n.dic_traducao_cargos.get(c, c) for c in df_gower_15.columns]
        
        fig_gower_heat = visualizations.plot_gower_heatmap(df_gower_15, f"{i18n.t('title_gower_prefix')} - {i18n.t(cenario_sel)}", cargos_destaque=cargos_destaque_ui)
        st.plotly_chart(fig_gower_heat, use_container_width=True)
        
        # Histograma de Distribuição (Sugestão Visual 1)
        auto_zoom_15 = st.checkbox(i18n.t("ruler_zoom_toggle", default="🔍 Habilitar Zoom Automático (Ajustar gráfico à dispersão)"), value=True, key="ruler_zoom_15")
        nome_metrica = metric_options[selected_metric_key_15]
        titulo_hist = f"📈 {i18n.t('hist_title', default='Distribuição das Distâncias')} ({nome_metrica})"
        fig_hist = visualizations.plot_distance_histogram(df_gower_15, titulo_hist, full_scale=not auto_zoom_15)
        st.plotly_chart(fig_hist, use_container_width=True)
        
        st.markdown("💡 **Dica:** Abra o painel abaixo para ver como cada métrica calcula as distâncias.")
        with st.expander("📖 ABRIR TABELA COMPARATIVA DE MÉTRICAS"):
            st.dataframe(explanations.get_metrics_comparison_df(), use_container_width=True)
            
        if st.session_state.get('show_explanations', False):
            tone_key = st.session_state.get('explanation_tone', 'tecnico')
            st.info(explanations.get_explanation("gower", tone_key, language=st.session_state.get('language', 'PT-BR')))
        if 'interaction_ui' in locals(): interaction_ui.render_like_button("1.5 Mapa de Calor Gower", "1_5")

    # 1.6. Régua Gower
    elif current_section == 'sub_ruler':
        if is_sample_biased:
            st.warning(explanations.get_short_bias_warning(language=st.session_state.get('language', 'PT-BR')), icon="🚨")
        st.markdown("<div id='toc-ruler'></div>", unsafe_allow_html=True)
        st.subheader(i18n.t("sub_ruler"), help=i18n.t("sub_ruler_help"))
    
        ref_cargo_opcoes = list(df_para_gower['Carreira']) if 'Carreira' in df_para_gower.columns else [str(x) for x in df_para_gower.index]
        
        col_ref_16, col_metric_16 = st.columns(2)
        with col_ref_16:
            ref_cargo = st.selectbox(
                i18n.t("select_ruler_role"), 
                ref_cargo_opcoes, 
                index=0,
                format_func=lambda x: f"{x} {i18n.t('used_in_paper')}" if x in ["Delegado de Polícia", "Police Chief"] else x,
                key="ruler_ref_selectbox"
            )
        with col_metric_16:
            selected_metric_key_16 = st.selectbox(
                i18n.t("select_metric", default="Selecione a Métrica de Similaridade"),
                list(metric_options.keys()),
                format_func=lambda x: metric_options[x],
                key="metric_selectbox_16"
            )
            
        df_gower_16 = data_processing.calcular_distancias(df_para_gower, metric=selected_metric_key_16)
        if st.session_state.get('language', 'PT-BR') == 'EN' and traduzir_cargos:
            df_gower_16.index = [i18n.dic_traducao_cargos.get(c, c) for c in df_gower_16.index]
            df_gower_16.columns = [i18n.dic_traducao_cargos.get(c, c) for c in df_gower_16.columns]
        
        # Checkbox para habilitar ou desabilitar o zoom automático no eixo X
        auto_zoom = st.checkbox(i18n.t("ruler_zoom_toggle", default="🔍 Habilitar Zoom Automático (Ajustar gráfico à dispersão)"), value=True, key="ruler_zoom_16")
        
        fig_gower_ruler = visualizations.plot_gower_ruler(df_gower_16, reference_career=ref_cargo, cargos_destaque=cargos_destaque, full_scale=not auto_zoom)
        st.plotly_chart(fig_gower_ruler, use_container_width=True)
        
        st.markdown("💡 **Dica:** Abra o painel abaixo para ver como cada métrica calcula as distâncias.")
        with st.expander("📖 ABRIR TABELA COMPARATIVA DE MÉTRICAS"):
            st.dataframe(explanations.get_metrics_comparison_df(), use_container_width=True)
            
        if st.session_state.get('show_explanations', False):
            tone_key = st.session_state.get('explanation_tone', 'tecnico')
            st.info(explanations.get_explanation("regua", tone_key, language=st.session_state.get('language', 'PT-BR')))
        if 'interaction_ui' in locals(): interaction_ui.render_like_button("1.6 Regua Gower", "1_6")
    
    # 1.7. Dendograma
    elif current_section == 'sub_dendro':
        if is_sample_biased:
            st.warning(explanations.get_short_bias_warning(language=st.session_state.get('language', 'PT-BR')), icon="🚨")
        st.markdown("<div id='toc-dendro'></div>", unsafe_allow_html=True)
        st.subheader(i18n.t("sub_dendro"), help=i18n.t("sub_dendro_help"))
    
        col_metric_17, col_linkage_17 = st.columns(2)
        with col_metric_17:
            selected_metric_key_17 = st.selectbox(
                i18n.t("select_metric", default="Selecione a Métrica de Similaridade"),
                list(metric_options.keys()),
                format_func=lambda x: metric_options[x],
                key="metric_selectbox_17"
            )
        with col_linkage_17:
            linkage_options_17 = {
                'single': i18n.t("linkage_single", default="Single Linkage (usado no artigo)"),
                'complete': i18n.t("linkage_complete", default="Complete Linkage"),
                'average': i18n.t("linkage_average", default="Average Linkage (UPGMA)")
            }
            selected_linkage_17 = st.selectbox(
                i18n.t("select_linkage", default="Selecione o Método de Agrupamento (Linkage)"),
                list(linkage_options_17.keys()),
                format_func=lambda x: linkage_options_17[x],
                key="linkage_selectbox_17"
            )
            
        df_gower_17 = data_processing.calcular_distancias(df_para_gower, metric=selected_metric_key_17)
        if st.session_state.get('language', 'PT-BR') == 'EN' and traduzir_cargos:
            df_gower_17.index = [i18n.dic_traducao_cargos.get(c, c) for c in df_gower_17.index]
            df_gower_17.columns = [i18n.dic_traducao_cargos.get(c, c) for c in df_gower_17.columns]
    
        st.markdown(i18n.t("dendro_method"))
        if len(df_gower_17.columns) > 1:
            fig_dendro = visualizations.plot_dendrogram(df_gower_17, f"{i18n.t('dendro_title')} - {i18n.t(cenario_sel)}", cargos_destaque=cargos_destaque_ui, linkage_method=selected_linkage_17)
            st.plotly_chart(fig_dendro, use_container_width=True)
            
            st.markdown("💡 **Dica:** Abra o painel abaixo para comparar as métricas e os métodos de agrupamento recomendados para o cenário atual.")
            with st.expander("📖 ABRIR COMPARAÇÕES E ÍNDICES COFENÉTICOS"):
                st.markdown("#### Métricas de Distância")
                st.dataframe(explanations.get_metrics_comparison_df(), use_container_width=True)
                
                st.markdown("#### Métodos de Agrupamento (Linkage)")
                st.markdown(i18n.t("coph_corr_help", default="Mede o quanto o dendrograma preserva as distâncias originais. Valores próximos a 1 indicam que a árvore representa fielmente as distâncias."))
                st.dataframe(explanations.get_linkages_comparison_df(), use_container_width=True)
                
                st.markdown("#### Índices Cofenéticos (Cenário Atual)")
                st.markdown("<span style='color:#00cc00; font-weight:bold;'>Verde (≥0.90)</span> | <span style='color:#ffcc00; font-weight:bold;'>Amarelo (≥0.75)</span> | <span style='color:#ff9900; font-weight:bold;'>Laranja (≥0.50)</span> | <span style='color:#ff3333; font-weight:bold;'>Vermelho (<0.50)</span>", unsafe_allow_html=True)
                df_coph = data_processing.get_cophenetic_comparison_table(df_para_gower)
                
                def color_coph(val):
                    if isinstance(val, str) and " (" in val:
                        try:
                            val = float(val.split(" ")[0])
                        except ValueError:
                            pass
                            
                    if isinstance(val, (int, float)):
                        if val >= 0.90:
                            f = (val - 0.90) / 0.10
                            f = max(0, min(1, f))
                            r = int(150 + f * (0 - 150))
                            g = int(255 + f * (200 - 255))
                            b = int(150 + f * (0 - 150))
                        elif val >= 0.75:
                            f = (val - 0.75) / 0.15
                            f = max(0, min(1, f))
                            r = int(255 + f * (150 - 255))
                            g = int(220 + f * (255 - 220))
                            b = int(0 + f * (150 - 0))
                        elif val >= 0.50:
                            f = (val - 0.50) / 0.25
                            f = max(0, min(1, f))
                            r = int(255 + f * (255 - 255))
                            g = int(150 + f * (220 - 150))
                            b = int(0 + f * (0 - 0))
                        else:
                            f = val / 0.50
                            f = max(0, min(1, f))
                            r = int(255 + f * (255 - 255))
                            g = int(50 + f * (150 - 50))
                            b = int(50 + f * (0 - 50))
                        return f'background-color: rgb({r},{g},{b}); color: black;'
                    return ''
                    
                st.dataframe(df_coph.style.map(color_coph), use_container_width=True)
        else:
            st.warning(i18n.t("dendro_warning"))
    
        if st.session_state.get('show_explanations', False):
            tone_key = st.session_state.get('explanation_tone', 'tecnico')
            st.info(explanations.get_explanation("dendograma", tone_key, language=st.session_state.get('language', 'PT-BR')))
        if 'interaction_ui' in locals(): interaction_ui.render_like_button("1.7 Dendograma", "1_7")


    # 1.8. UpSet Plot (Alternativa ao Venn)
    elif current_section == 'sub_upset':
        if is_sample_biased:
            st.warning(explanations.get_short_bias_warning(language=st.session_state.get('language', 'PT-BR')), icon="🚨")
        st.markdown("<div id='toc-upset'></div>", unsafe_allow_html=True)
        st.subheader(i18n.t("sub_upset"), help=i18n.t("sub_upset_help"))
        
        df_upset = df_original_limpo.set_index('Carreira') if 'Carreira' in df_original_limpo.columns else df_original_limpo.copy()
        if st.session_state.get('language', 'PT-BR') == 'EN' and traduzir_cargos:
            df_upset.index = [i18n.traduzir_cargo(c) for c in df_upset.index]
            df_upset.columns = [i18n.traduzir_atribuicao(c) for c in df_upset.columns]
        fig_upset = visualizations.plot_upset_bar_chart(
            df_upset, 
            f"{i18n.t('upset_title')} - {i18n.t(cenario_sel)}", 
            cargos_destaque=cargos_destaque_ui
        )
        st.plotly_chart(fig_upset, use_container_width=True)
        
        if st.session_state.get('show_explanations', False):
            tone_key = st.session_state.get('explanation_tone', 'tecnico')
            st.info(explanations.get_explanation("upset", tone_key, language=st.session_state.get('language', 'PT-BR')))
        if 'interaction_ui' in locals(): interaction_ui.render_like_button("1.8 UpSet Plot", "1_8")


elif modo_visao == i18n.t("mode_1"):
    st.error("Cenário indisponível.")

# Renderizar Botão Flutuante de Comentários (Geral para a Visão Atual)
try:
    interaction_ui.render_interactions(modo_visao)
except Exception as e:
    pass

# Padding para não esconder gráficos atrás do botão de rodapé
st.markdown("<div style='height: 150px;'></div>", unsafe_allow_html=True)

if persona_placeholder is not None:
    try:
        from database import get_db_session, AnalyticsSession
        import analytics
        db = get_db_session()
        session_id = analytics.get_session_id()
        analytics_session = db.query(AnalyticsSession).filter_by(session_id=session_id).first()
        inferred = analytics_session.inferred_persona if analytics_session else "Cidadão/Curioso"
        db.close()
    except Exception:
        inferred = "Erro ao carregar"
        
    persona_placeholder.info(f"**Sua Persona Atual:**\n\n{inferred}")

