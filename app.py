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
from datetime import datetime
import pytz


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

# --- SESSÃO DE SEGURANÇA: WATERMARK INVISÍVEL ---
import uuid

# Cria um ID único (Hash) para esta sessão (não muda ao recarregar filtros na mesma aba)
if "forensic_id" not in st.session_state:
    st.session_state.forensic_id = uuid.uuid4().hex[:6].upper()

# Captura o usuário passado pelo Nginx (se houver) e estampa na tela
try:
    remote_user = st.context.headers.get("X-Remote-User", "")
    if remote_user:
        # Pega a data e hora atual no fuso de Brasília
        fuso_br = pytz.timezone('America/Sao_Paulo')
        agora = datetime.now(fuso_br).strftime('%d/%m/%Y %H:%M')
        
        # A marca d'água agora inclui o Hash da sessão
        marca_texto = f"{remote_user} ({agora}) [{st.session_state.forensic_id}]"
        
        watermark_html = f"""
        <style>
        .leak-tracer {{
            position: fixed;
            top: -50%; left: -50%; width: 200vw; height: 200vh;
            pointer-events: none;
            z-index: 9999999;
            /* Cor branca com blend difference garante contraste sutil em fundos claros e escuros */
            color: #FFF;
            opacity: 0.02;
            mix-blend-mode: difference;
            font-size: 24px;
            font-family: monospace;
            font-weight: bold;
            display: flex;
            flex-wrap: wrap;
            overflow: hidden;
            transform: rotate(-30deg);
            align-content: center;
            justify-content: center;
        }}
        .leak-tracer span {{
            padding: 30px 50px;
        }}
        </style>
        <div class="leak-tracer">
        """
        # Repete o nome do usuário para preencher a tela (diagonal tracking)
        spans = "".join([f"<span>{marca_texto}</span>" for _ in range(400)])
        watermark_html += spans + "</div>"
        st.markdown(watermark_html, unsafe_allow_html=True)
except Exception as e:
    pass
# ------------------------------------------------

# Sincroniza o modo de tema com a URL (para sobreviver a reloads)
if "light_mode" not in st.session_state:
    st.session_state.light_mode = st.query_params.get("theme") == "light"

# --- Detecção Mobile (Auto) ---
is_mobile_qs = st.query_params.get("is_mobile", None)
if is_mobile_qs is None:
    is_mobile_default = False
    if "mobile_auto_checked" not in st.session_state:
        st.session_state.mobile_auto_checked = True
        components.html("""
        <script>
        const isMobile = window.innerWidth <= 768;
        const urlParams = new URLSearchParams(window.parent.location.search);
        if (!urlParams.has('is_mobile')) {
            urlParams.set('is_mobile', isMobile);
            window.parent.location.search = '?' + urlParams.toString();
        }
        </script>
        """, height=0, width=0)
else:
    is_mobile_default = (is_mobile_qs.lower() == "true")

if "is_mobile" not in st.session_state:
    st.session_state.is_mobile = is_mobile_default

# --- MONKEY PATCH PARA SUPORTE A LIGHT MODE EM PLOTLY ---
_original_plotly_chart = st.plotly_chart
def _custom_plotly_chart(figure_or_data, **kwargs):
    if st.session_state.get("light_mode"):
        if hasattr(figure_or_data, "update_layout"):
            figure_or_data.update_layout(
                template="plotly_white",
                paper_bgcolor="#F4F6F9",
                plot_bgcolor="#F4F6F9",
                font=dict(color="#1E2329")
            )
            figure_or_data.update_xaxes(color="#1E2329", gridcolor="#E1E5EA", tickfont=dict(color="#1E2329"))
            figure_or_data.update_yaxes(color="#1E2329", gridcolor="#E1E5EA", tickfont=dict(color="#1E2329"))
        kwargs["theme"] = None
    return _original_plotly_chart(figure_or_data, **kwargs)
st.plotly_chart = _custom_plotly_chart

if st.session_state.get("light_mode"):
    st.markdown("""
        <style>
        /* Fundo principal suave (não branco puro) */
        [data-testid="stAppViewContainer"] { background-color: #F4F6F9 !important; color: #1E2329 !important; }
        [data-testid="stSidebar"] { background-color: #E8ECEF !important; color: #1E2329 !important; }
        [data-testid="stHeader"] { background-color: transparent !important; }
        
        /* Preservar as luzes azul e vermelha no fundo invertendo o modo de mesclagem */
        .stApp::before, .stApp::after { mix-blend-mode: multiply !important; opacity: 0.25 !important; }
        
        /* Força textos para escuro, preservando spans para cores inline */
        .stMarkdown, .stText, p, h1, h2, h3, h4, h5, h6, label { color: #1E2329 !important; }
        
        /* Menus (Selectboxes, Dropdowns) */
        div[data-baseweb="select"] > div { background-color: #FFFFFF !important; border-color: #CED4DA !important; }
        div[data-baseweb="select"] span { color: #1E2329 !important; }
        /* Inputs, Textareas e Menus Suspensos (Dropdowns) */
        .stTextArea textarea, .stTextInput input, [data-baseweb="textarea"] textarea, [data-baseweb="input"] input, [data-baseweb="textarea"], [data-baseweb="input"] {
            background-color: #F0F2F6 !important;
            color: #1E2329 !important;
            border-color: #CED4DA !important;
            -webkit-text-fill-color: #1E2329 !important;
        }
        
        ul[role="listbox"], [data-baseweb="menu"], div[role="listbox"] {
            background-color: #FFFFFF !important;
            border: 1px solid #CED4DA !important;
        }
        
        li[role="option"] { 
            background-color: #FFFFFF !important;
            color: #1E2329 !important; 
        }
        li[role="option"]:hover, li[role="option"][aria-selected="true"] { 
            background-color: #F0F2F6 !important; 
            color: #0072B2 !important;
        }
        
        /* Abas (Tabs) */
        button[data-baseweb="tab"] p { color: #5C6C7B !important; font-weight: 600 !important; }
        button[data-baseweb="tab"][aria-selected="true"] p { color: #0072B2 !important; font-weight: 800 !important; }
        
        /* Multiselect Tags (Carreiras) */
        span[data-baseweb="tag"] {
            background-color: #E8ECEF !important;
            color: #1E2329 !important;
            border: 1px solid #CED4DA !important;
        }
        span[data-baseweb="tag"] span { color: #1E2329 !important; }
        span[data-baseweb="tag"] svg { fill: #1E2329 !important; }
        
        /* Tooltips e Balões de Ajuda */
        [data-baseweb="tooltip"] > div, div[data-testid="stTooltipContent"], [data-baseweb="popover"] > div {
            background-color: #FFFFFF !important;
            color: #1E2329 !important;
            border: 1px solid #CED4DA !important;
        }
        [data-testid="stTooltipHoverTarget"] {
            color: #1E2329 !important;
        }
        [data-testid="stTooltipHoverTarget"] svg {
            stroke: #1E2329 !important;
            color: #1E2329 !important;
            opacity: 1 !important;
        }
        /* Botões */
        button[kind="secondary"] { background-color: #FFFFFF !important; color: #1E2329 !important; border-color: #CED4DA !important; }
        
        /* Ajustar containers escuros (Header fixo e Caixas) */
        div[data-testid="stLayoutWrapper"]:has(div#sticky-header-anchor) { background-color: rgba(244, 246, 249, 0.95) !important; border-bottom: 1px solid rgba(0, 0, 0, 0.1) !important; }
        .transparency-box { background-color: #FFFFFF !important; }
        /* Forçar variáveis nativas do Streamlit para Light Mode em todos os elementos flutuantes */
        :root, .stApp, [data-baseweb], div[role="dialog"] {
            --background-color: #FFFFFF !important;
            --secondary-background-color: #F0F2F6 !important;
            --text-color: #1E2329 !important;
            --primary-color: #0072B2 !important;
        }
        
        .status-badge { background-color: #FFFFFF !important; border: 1px solid #CED4DA !important; color: #1E2329 !important; }
        .status-badge strong { color: #0072B2 !important; }
        
        /* Tabela Light (HTML customizada) */
        .light-table-container { overflow-x: auto; white-space: nowrap; -webkit-overflow-scrolling: touch; }
        .light-table-container table { width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 0.9rem; font-family: sans-serif; background-color: #FFFFFF !important; }
        .light-table-container th { background-color: #F0F2F6 !important; color: #1E2329 !important; padding: 10px; text-align: left; border: 1px solid #CED4DA !important; }
        .light-table-container td { padding: 10px; border: 1px solid #CED4DA !important; color: #1E2329; }
        /* Efeitos visuais suaves nas tabelas claras */
        .light-table-container tr:hover td { filter: brightness(0.92); }
        
        /* Expander (Modos de Visão e Explicações) e Configurações Analíticas */
        [data-testid="stExpander"], .stExpander, div[data-testid="stExpander"] { background-color: #FFFFFF !important; border-color: #CED4DA !important; }
        [data-testid="stExpander"] summary, .stExpander summary { color: #1E2329 !important; background-color: #FFFFFF !important; }
        [data-testid="stExpander"] summary:hover, .stExpander summary:hover { background-color: #F0F2F6 !important; }
        [data-testid="stExpander"] summary p, [data-testid="stExpander"] summary span, .stExpander summary p, .stExpander summary span { color: #1E2329 !important; font-weight: 700 !important; }
        [data-testid="stExpanderDetails"], .stExpanderDetails, div[data-testid="stExpanderDetails"] { background-color: #FFFFFF !important; color: #1E2329 !important; }
        [data-testid="stExpanderDetails"] p, [data-testid="stExpanderDetails"] h4, .stExpanderDetails p, .stExpanderDetails h4 { color: #1E2329 !important; }
        
        /* Toasts (Mensagens flutuantes) */
        [data-testid="stToast"] { background-color: #FFFFFF !important; border-color: #CED4DA !important; }
        [data-testid="stToast"] > div, [data-testid="stToast"] p { color: #1E2329 !important; }
        
        /* Popovers (Modos de Visão / Configurações) */
        [data-testid="stPopoverBody"], div[data-testid="stPopoverBody"], .stPopoverBody, div[data-baseweb="popover"] > div, div[data-baseweb="popover"] { background-color: #FFFFFF !important; border-color: #CED4DA !important; color: #1E2329 !important; }
        [data-testid="stPopoverBody"] p, [data-testid="stPopoverBody"] h4, [data-testid="stPopoverBody"] label, div[data-baseweb="popover"] p, div[data-baseweb="popover"] label { color: #1E2329 !important; }
        
        /* Caixas de Alerta (st.info) */
        [data-testid="stAlert"] { background-color: #E8F4F8 !important; border: 1px solid #B6D4E3 !important; color: #1E2329 !important; }
        [data-testid="stAlert"] p { color: #1E2329 !important; }
        
        /* Custom Metric Boxes */
        .custom-metric-box { background: #FFFFFF !important; border-color: #CED4DA !important; color: #1E2329 !important; }
        .custom-metric-box * { color: #1E2329 !important; }
        
        /* Tooltips e labels */
        [data-testid="stWidgetLabel"] { color: #1E2329 !important; }
        
        /* Modals e Dialogs */
        [data-testid="stDialog"] > div, [data-testid="stModal"] > div, div[role="dialog"] > div, div[data-baseweb="modal"] > div { background-color: #FFFFFF !important; border: 1px solid #CED4DA !important; }
        [data-testid="stDialog"] *, [data-testid="stModal"] *, div[role="dialog"] *, div[data-baseweb="modal"] * { color: #1E2329 !important; }
        
        /* Inputs, Selects, Menus suspensos (Dropdowns) */
        [data-baseweb="select"] > div, [data-baseweb="menu"], ul[role="listbox"], ul[role="listbox"] li { background-color: #FFFFFF !important; color: #1E2329 !important; }
        [data-baseweb="select"] *, [data-baseweb="menu"] *, ul[role="listbox"] * { color: #1E2329 !important; }
        [data-testid="stSelectbox"] label, [data-testid="stMultiSelect"] label, [data-testid="stRadio"] label { color: #1E2329 !important; }
        
        /* Tabs active state */
        [data-baseweb="tab"][aria-selected="true"] { background-color: transparent !important; }
        </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <style>
        .custom-metric-box { background: #1E1E1E !important; border: 1px solid #333 !important; padding: 15px; border-radius: 10px; }
        </style>
    """, unsafe_allow_html=True)

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
footer_bg = "rgba(255, 255, 255, 0.95)" if st.session_state.get("light_mode") else "rgba(14, 17, 23, 0.90)"
footer_border = "rgba(0, 0, 0, 0.15)" if st.session_state.get("light_mode") else "rgba(255, 255, 255, 0.15)"
footer_text = "#1E2329" if st.session_state.get("light_mode") else "#E0E0E0"
footer_subtext = "#5C6C7B" if st.session_state.get("light_mode") else "#A0A0A0"
footer_link = "#0072B2" if st.session_state.get("light_mode") else "#4da6ff"

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
            background: __BG_COLOR__;
            backdrop-filter: blur(15px);
            border: 1px solid __BORDER_COLOR__;
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
            color: __TEXT_COLOR__;
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
            color: __LINK_COLOR__;
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
            background: rgba(128,128,128,0.1);
        }
        .hud-content h4 {
            margin: 0 0 10px 0;
            color: __TEXT_COLOR__;
            font-size: 1rem;
            border-bottom: 1px solid #333;
            padding-bottom: 5px;
            text-align: center;
        }
        @media (max-width: 768px) {
            #hud-floating-footer {
                width: 44px;
                height: 44px;
                border-radius: 22px;
                bottom: 10px;
                right: 10px;
                padding: 0;
                justify-content: center;
                border: none;
            }
            .hud-icon {
                font-size: 1.3rem;
            }
            .hud-icon span {
                display: none;
            }
            #hud-floating-footer:hover {
                width: 240px;
                height: max-content;
                border-radius: 12px;
                padding: 12px;
                bottom: 10px;
                right: 10px;
                border: 1px solid __BORDER_COLOR__;
            }
            .hud-content a {
                padding: 12px;
                font-size: 1rem;
            }
        }
        </style>
        
        <div class="hud-icon">
            <span style="font-size: 1.2rem;">📚</span> __FOOTER_TITLE__
        </div>
        <div class="hud-content">
            <h4>__REF_TITLE__</h4>
            <span style="font-size: 0.75rem; color: __SUBTEXT_COLOR__; display: block; margin: -5px 0 8px 0; font-style: italic;">__REF_DESC__</span>
            <a href="https://github.com/phsmaia/Estudo_Atribuicoes_PCSP" target="_blank">__REPO__</a>
            <a href="https://periodicos.pf.gov.br/index.php/RBCP/pt_BR/article/view/4693" target="_blank">__ARTICLE__</a>
            <a href="https://zenodo.org/records/14284483" target="_blank">__DATA__</a>
            <h4 style="margin-top: 15px;">__CONTACT_TITLE__</h4>
            <span style="font-size: 0.75rem; color: __SUBTEXT_COLOR__; display: block; margin: -5px 0 8px 0; font-style: italic;">__CONTACT_DESC__</span>
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

footer_html = footer_html.replace('__BG_COLOR__', footer_bg).replace('__BORDER_COLOR__', footer_border).replace('__TEXT_COLOR__', footer_text).replace('__LINK_COLOR__', footer_link).replace('__SUBTEXT_COLOR__', footer_subtext)

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

                // Adiciona o CSS de sirene intermitente, adaptando-o para Light/Dark Mode
                const urlParams = new URLSearchParams(window.parent.location.search);
                const isLight = urlParams.get('theme') === 'light';
                const styleId = isLight ? 'hud-strobe-css-light' : 'hud-strobe-css-dark';
                
                // Limpa estilos opostos ou antigos
                const oldLight = window.parent.document.getElementById('hud-strobe-css-light');
                if (oldLight) oldLight.remove();
                const oldDark = window.parent.document.getElementById('hud-strobe-css-dark');
                if (oldDark) oldDark.remove();
                const oldOld = window.parent.document.getElementById('hud-strobe-css');
                if (oldOld) oldOld.remove();

                if (!window.parent.document.getElementById(styleId)) {{
                    const style = window.parent.document.createElement('style');
                    style.id = styleId;
                    
                    const bgRedOn = isLight ? 'rgba(255, 70, 90, 0.85)' : 'rgba(255, 0, 50, 0.95)';
                    const bgRedOff = isLight ? 'rgba(255, 255, 255, 0.95)' : 'rgba(0, 0, 0, 0.8)';
                    const bgBlueOn = isLight ? 'rgba(70, 150, 255, 0.85)' : 'rgba(0, 100, 255, 0.95)';
                    const shadowRed = isLight ? 'rgba(255, 70, 90, 0.4)' : 'rgba(255, 0, 50, 0.9)';
                    const shadowBlue = isLight ? 'rgba(70, 150, 255, 0.4)' : 'rgba(0, 100, 255, 0.9)';
                    const txtColor = isLight ? '#1E2329' : 'white';
                    const txtColorOn = 'white';
                    const borderOff = isLight ? '1px solid #CED4DA' : '1px solid rgba(255,255,255,0.2)';
                    
                    style.innerHTML = "" + 
                        "@keyframes hud_strobe_" + (isLight?"light":"dark") + " {{ " +
                            "0%, 10% {{ box-shadow: 0 0 15px " + shadowRed + "; background: " + bgRedOn + "; color: " + txtColorOn + "; border: transparent; }} " +
                            "11%, 15% {{ box-shadow: none; background: " + bgRedOff + "; color: " + txtColor + "; border: " + borderOff + "; }} " +
                            "16%, 25% {{ box-shadow: 0 0 15px " + shadowRed + "; background: " + bgRedOn + "; color: " + txtColorOn + "; border: transparent; }} " +
                            "26%, 49% {{ box-shadow: none; background: " + bgRedOff + "; color: " + txtColor + "; border: " + borderOff + "; }} " +
                            "50%, 60% {{ box-shadow: 0 0 15px " + shadowBlue + "; background: " + bgBlueOn + "; color: " + txtColorOn + "; border: transparent; }} " +
                            "61%, 65% {{ box-shadow: none; background: " + bgRedOff + "; color: " + txtColor + "; border: " + borderOff + "; }} " +
                            "66%, 75% {{ box-shadow: 0 0 15px " + shadowBlue + "; background: " + bgBlueOn + "; color: " + txtColorOn + "; border: transparent; }} " +
                            "76%, 100% {{ box-shadow: none; background: " + bgRedOff + "; color: " + txtColor + "; border: " + borderOff + "; }} " +
                        "}} " +
                        ".custom-inline-loader {{ " +
                            "position: fixed; top: 25px; left: 50%; transform: translateX(-50%); z-index: 9999999; " +
                            "padding: 8px 20px; border-radius: 30px; font-size: 1rem; font-weight: bold; " +
                            "animation: hud_strobe_" + (isLight?"light":"dark") + " 1.2s infinite; " +
                            "box-shadow: 0 4px 15px rgba(0,0,0,0.1); display: flex; align-items: center; gap: 10px; " +
                            "pointer-events: none; transition: all 0.2s ease;" +
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
sticky_bg = "rgba(244, 246, 249, 0.95)" if st.session_state.get("light_mode") else "rgba(14, 17, 23, 0.95)"
sticky_border = "rgba(0, 0, 0, 0.15)" if st.session_state.get("light_mode") else "rgba(255, 255, 255, 0.15)"

st.markdown(f"""
<style>
/* Animação Premium: Fade & Focus (Sem alteração geométrica) */
@keyframes smoothCascadeFocus {{
    0% {{ opacity: 0; filter: blur(5px); }}
    100% {{ opacity: 1; filter: blur(0); }}
}}

div[data-testid="stVerticalBlock"] > div {{
    opacity: 0; 
    animation: smoothCascadeFocus 0.7s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}}

/* Fundo Elegante e Trava contra barras de rolagem artificiais */
.stApp {{
    background: {'none' if st.session_state.get("light_mode") else 'radial-gradient(circle at 50% 0%, #121c2b 0%, #0e1117 60%)'} !important;
}}
</style>
""", unsafe_allow_html=True)

ambient_blend = "normal" if st.session_state.get("light_mode") else "screen"
ambient_red_base = "rgba(255, 0, 0, 1.0)" if st.session_state.get("light_mode") else "rgba(255, 0, 0, 0.25)"
ambient_red_fade = "rgba(255, 0, 0, 0.0)" if st.session_state.get("light_mode") else "rgba(255, 0, 0, 0.15)"
ambient_blue_base = "rgba(0, 80, 255, 1.0)" if st.session_state.get("light_mode") else "rgba(0, 80, 255, 0.25)"
ambient_blue_fade = "rgba(0, 80, 255, 0.0)" if st.session_state.get("light_mode") else "rgba(0, 80, 255, 0.15)"

st.markdown(f"""
<style>
/* --- Ambient Police Lights (Subtle & Cinematic) --- */
.stApp::before {{
    content: "";
    position: fixed;
    top: 0; left: 0; width: 100vw; height: 100vh;
    pointer-events: none;
    z-index: 9999;
    mix-blend-mode: {ambient_blend};
    background: radial-gradient(circle at 15% 20%, {ambient_red_base}, transparent 60%),
                radial-gradient(circle at 85% 80%, {ambient_red_fade}, transparent 60%);
    animation: ambientRed 8s infinite alternate ease-in-out;
}}

.stApp::after {{
    content: "";
    position: fixed;
    top: 0; left: 0; width: 100vw; height: 100vh;
    pointer-events: none;
    z-index: 9999;
    mix-blend-mode: {ambient_blend};
    background: radial-gradient(circle at 85% 20%, {ambient_blue_base}, transparent 60%),
                radial-gradient(circle at 15% 80%, {ambient_blue_fade}, transparent 60%);
    animation: ambientBlue 10s infinite alternate ease-in-out;
}}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
    @keyframes ambientRed {
        0% { opacity: 0.3; transform: scale(1); }
        100% { opacity: 0.7; transform: scale(1.1); }
    }
    
    @keyframes ambientBlue {
        0% { opacity: 0.7; transform: scale(1.1); }
        100% { opacity: 0.3; transform: scale(1); }
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown(f"""
<style>
/* Atrasos escalonados */
div[data-testid="stVerticalBlock"] > div:nth-child(1) {{ animation-delay: 0.05s; }}
div[data-testid="stVerticalBlock"] > div:nth-child(2) {{ animation-delay: 0.15s; }}
div[data-testid="stVerticalBlock"] > div:nth-child(3) {{ animation-delay: 0.25s; }}
div[data-testid="stVerticalBlock"] > div:nth-child(4) {{ animation-delay: 0.35s; }}
div[data-testid="stVerticalBlock"] > div:nth-child(5) {{ animation-delay: 0.45s; }}

/* Sticky Container Header */
div[data-testid="stLayoutWrapper"]:has(div#sticky-header-anchor):has(div[data-testid="stRadio"]) {{
    position: sticky;
    top: 0;
    z-index: 999;
    background-color: {sticky_bg};
    padding: 15px 20px 10px 20px;
    border-radius: 12px;
    border-bottom: 1px solid {sticky_border};
    box-shadow: 0 8px 32px rgba(0,0,0,0.4);
    margin-bottom: 25px;
    backdrop-filter: blur(10px);
}}

@media (max-width: 768px) {{
    div[data-testid="stLayoutWrapper"]:has(div#sticky-header-anchor) div[data-testid="stHorizontalBlock"] {{
        flex-wrap: nowrap !important;
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
        padding-bottom: 8px;
    }}
    div[data-testid="stLayoutWrapper"]:has(div#sticky-header-anchor) div[data-testid="column"] {{
        min-width: fit-content !important;
        flex: 0 0 auto !important;
        padding-right: 1rem;
    }}
}}

@media (min-width: 769px) {{
    /* Hide plotly text labels on desktop to preserve hover-only clean look */
    .js-plotly-plot .textpoint {{
        display: none !important;
    }}
}}

/* Remover espaço em branco superior do Streamlit */
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
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
        
        // Verifica URL Params para manter Light Mode durante Splash Screen
        const urlParams = new URLSearchParams(window.parent.location.search);
        const isLight = urlParams.get('theme') === 'light';
        const bgColor = isLight ? '#E9ECEF' : '#0b0f19';
        const textColor = isLight ? '#1E2329' : 'white';
        const lightsOpacity = isLight ? '0.15' : '1.0';
        const lightsBlend = isLight ? 'multiply' : 'screen';
        const btnBg = isLight ? 'rgba(255, 255, 255, 0.8)' : 'rgba(14, 17, 23, 0.5)';
        const btnBorder = isLight ? 'rgba(0, 114, 178, 0.3)' : 'rgba(77, 166, 255, 0.3)';
        const btnBorderHover = isLight ? 'rgba(0, 114, 178, 0.6)' : 'rgba(77, 166, 255, 0.4)';
        const strokeColor = isLight ? '#0072B2' : '#4da6ff';
        const progressBg = isLight ? 'rgba(0,0,0,0.1)' : 'rgba(255,255,255,0.1)';
        const scanColor = isLight ? '#008060' : '#00ffcc';
        const scanShadow = isLight ? 'rgba(0, 128, 96, 0.5)' : 'rgba(0, 255, 204, 0.6)';
        const splashTitleColor = isLight ? '#1E2329' : '#E0E0E0';

        splash.innerHTML = `
            <style>
            #custom-splash-screen {{
                position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
                background: ${{bgColor}};
                z-index: 9999999; display: flex; flex-direction: column;
                align-items: center; justify-content: center; color: ${{textColor}};
                font-family: sans-serif; overflow: hidden;
            }}
            .police-lights {{
                position: absolute; top: 0; left: 0; width: 100%; height: 100%;
                background: transparent;
                animation: strobe 1.2s infinite;
                pointer-events: none;
                mix-blend-mode: ${{lightsBlend}};
            }}
            @keyframes strobe {{
                0%, 10% {{ background: radial-gradient(circle at 15% 50%, rgba(255, 0, 50, 0.25) 0%, transparent 40%), radial-gradient(circle at 85% 50%, rgba(0, 100, 255, 0) 0%, transparent 40%); opacity: ${{lightsOpacity}}; transform: scale(1.05); }}
                11%, 15% {{ background: transparent; opacity: 0.1; transform: scale(1); }}
                16%, 25% {{ background: radial-gradient(circle at 15% 50%, rgba(255, 0, 50, 0.25) 0%, transparent 40%), radial-gradient(circle at 85% 50%, rgba(0, 100, 255, 0) 0%, transparent 40%); opacity: ${{lightsOpacity}}; transform: scale(1.05); }}
                
                26%, 49% {{ background: transparent; opacity: 0.1; transform: scale(1); }}
                
                50%, 60% {{ background: radial-gradient(circle at 15% 50%, rgba(255, 0, 50, 0) 0%, transparent 40%), radial-gradient(circle at 85% 50%, rgba(0, 100, 255, 0.25) 0%, transparent 40%); opacity: ${{lightsOpacity}}; transform: scale(1.05); }}
                61%, 65% {{ background: transparent; opacity: 0.1; transform: scale(1); }}
                66%, 75% {{ background: radial-gradient(circle at 15% 50%, rgba(255, 0, 50, 0) 0%, transparent 40%), radial-gradient(circle at 85% 50%, rgba(0, 100, 255, 0.25) 0%, transparent 40%); opacity: ${{lightsOpacity}}; transform: scale(1.05); }}
                
                76%, 100% {{ background: transparent; opacity: 0.1; transform: scale(1); }}
            }}
            .fingerprint-btn {{
                width: 90px; height: 90px; border-radius: 50%;
                border: 2px solid ${{btnBorder}};
                display: flex; align-items: center; justify-content: center;
                margin-bottom: 25px; cursor: pointer; position: relative;
                background: ${{btnBg}}; backdrop-filter: blur(5px);
                transition: all 0.3s ease;
            }}
            .fingerprint-btn svg {{
                width: 45px; height: 45px; stroke: ${{strokeColor}}; fill: none; transition: all 0.3s ease;
            }}
            .fingerprint-btn:hover {{
                border-color: ${{strokeColor}}; box-shadow: 0 0 20px ${{btnBorderHover}};
            }}
            .fingerprint-btn.scanning {{
                border-color: ${{scanColor}}; box-shadow: 0 0 30px ${{scanShadow}};
            }}
            .fingerprint-btn.scanning svg {{ stroke: ${{scanColor}}; }}
            .scan-line {{
                position: absolute; top: 10%; left: 15%; width: 70%; height: 3px;
                background: ${{scanColor}}; box-shadow: 0 0 12px ${{scanShadow}};
                animation: scanAnim 1.5s infinite ease-in-out;
                display: none; border-radius: 2px;
            }}
            .fingerprint-btn.scanning .scan-line {{ display: block; }}
            @keyframes scanAnim {{ 0% {{ top: 15%; }} 50% {{ top: 85%; }} 100% {{ top: 15%; }} }}
            
            .progress-bar-container {{
                width: 300px; height: 6px; background: ${{progressBg}};
                border-radius: 3px; margin: 25px 0; overflow: hidden; position: relative;
            }}
            .progress-bar-fill {{
                position: absolute; top: 0; left: 0; height: 100%; background: ${{strokeColor}};
                width: 30%; animation: loadIndeterminate 1.5s infinite ease-in-out;
                border-radius: 3px;
                transition: background 0.3s ease, box-shadow 0.3s ease;
            }}
            .progress-bar-fill.scanning {{
                background: ${{scanColor}};
                box-shadow: 0 0 10px ${{scanShadow}};
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
            
            <h2 style="margin-bottom: 10px; color: ${{splashTitleColor}}; text-align: center; text-transform: uppercase; letter-spacing: 2px;">{title_str}</h2>
            <div class="progress-bar-container"><div class="progress-bar-fill"></div></div>
            <div id="splash-msg" style="color: ${{strokeColor}}; font-weight: bold; font-size: 1.1rem; height: 30px;">Carregando...</div>
        `;
        window.parent.document.body.appendChild(splash);
        
        // Interatividade divertida do botão e Easter Eggs
        const badge = window.parent.document.getElementById('interactive-badge');
        const msgEl = window.parent.document.getElementById('splash-msg');
        const pbFill = window.parent.document.querySelector('.progress-bar-fill');
        
        if (badge) {{
            let easterEggTimer;
            let eggTriggered = false;
            
            function triggerEasterEgg() {{
                eggTriggered = true;
                const eggs = [
                    () => {{
                        // 1. Acesso Confidencial
                        splash.style.background = isLight ? '#fff0f0' : '#2b0000';
                        const lights = window.parent.document.querySelector('.police-lights');
                        if(lights) lights.style.animation = 'strobe 0.5s infinite';
                        badge.style.borderColor = '#ffd700';
                        badge.querySelector('svg').style.stroke = '#ffd700';
                        if(pbFill) pbFill.style.background = '#ffd700';
                        msgEl.style.color = '#ffd700';
                        msgEl.innerText = "🚨 Acesso Nível 5 Confirmado! 🚨";
                    }},
                    () => {{
                        // 2. Modo CSI
                        splash.style.background = '#0a001a';
                        const titleEl = splash.querySelector('h2');
                        if(titleEl) titleEl.style.color = '#e0b3ff';
                        const lights = window.parent.document.querySelector('.police-lights');
                        if(lights) lights.style.display = 'none';
                        badge.style.borderColor = '#b84dff';
                        badge.style.boxShadow = '0 0 40px #b84dff';
                        badge.querySelector('svg').style.stroke = '#b84dff';
                        if(pbFill) pbFill.style.background = '#b84dff';
                        msgEl.style.color = '#b84dff';
                        msgEl.innerText = "🔦 Modo CSI de análise profunda ativado! 🕵️‍♂️";
                    }},
                    () => {{
                        // 3. Investigador Honorário
                        msgEl.style.color = '#ff9900';
                        msgEl.innerText = "🎖️ Código 10-4! Você foi promovido a Investigador Honorário!";
                        // Chuva de distintivos
                        for(let i=0; i<30; i++) {{
                            const conf = window.parent.document.createElement('div');
                            conf.innerText = Math.random() > 0.5 ? '🚔' : '🎖️';
                            conf.style.position = 'absolute';
                            conf.style.left = Math.random() * 100 + 'vw';
                            conf.style.top = '-50px';
                            conf.style.fontSize = (Math.random() * 20 + 15) + 'px';
                            conf.style.transition = 'top ' + (Math.random() * 2 + 1.5) + 's cubic-bezier(0.25, 0.46, 0.45, 0.94)';
                            conf.style.zIndex = '999999';
                            splash.appendChild(conf);
                            setTimeout(() => {{ conf.style.top = '120vh'; }}, 50);
                        }}
                    }}
                ];
                const randomEgg = eggs[Math.floor(Math.random() * eggs.length)];
                randomEgg();
            }}

            function startScanner(e) {{
                if(e && e.type === 'touchstart') e.preventDefault();
                eggTriggered = false;
                badge.classList.add('scanning');
                if(pbFill) pbFill.classList.add('scanning');
                msgEl.innerText = "🕵️‍♂️ Analisando biometria...";
                msgEl.style.color = scanColor;
                
                // Inicia o timer do Easter Egg
                easterEggTimer = setTimeout(triggerEasterEgg, 5000);
            }}

            badge.addEventListener('mousedown', startScanner);
            badge.addEventListener('touchstart', startScanner, {{passive: false}});
            
            function resetScanner(e) {{
                if(e && e.type === 'touchend') e.preventDefault();
                clearTimeout(easterEggTimer);
                if(eggTriggered) return; // Se o easter egg rodou, mantém na tela
                
                badge.classList.remove('scanning');
                if(pbFill) pbFill.classList.remove('scanning');
                msgEl.style.color = strokeColor;
            }}
            
            badge.addEventListener('mouseup', resetScanner);
            badge.addEventListener('mouseleave', resetScanner);
            badge.addEventListener('touchend', resetScanner);
            badge.addEventListener('touchcancel', resetScanner);
        }}
        
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
    
    .custom-metric-box { background: #1E1E1E; border: 1px solid #333; }
    </style>
""", unsafe_allow_html=True)

# Container Exclusivo para o Header Sticky
with st.container():
    st.markdown("<div id='sticky-header-anchor'></div>", unsafe_allow_html=True)
    
    # Dar mais espaço para o bloco de botões para que os componentes do Streamlit não encolham demais (causando quebra de linha ou sumiço de botões)
    col_title, col_btn = st.columns([80, 20], vertical_alignment="center")
    with col_title:
        st.markdown(f"<h3 style='margin: 0; padding: 0; font-size: 1.4rem; color: #E0E0E0; white-space: nowrap;'>{i18n.t('title')}</h3>", unsafe_allow_html=True)
    
    def _muda_idioma():
        val = st.session_state.lang_radio
        st.session_state.language = 'PT-BR' if 'PT-BR' in val else 'EN'
        analytics.log_event("change_language", {"language": st.session_state.language})
        
    def _change_font():
        st.session_state.base_font_size = st.session_state.font_input

    def _sync_theme():
        st.session_state.light_mode = st.session_state.light_mode_toggle
        if st.session_state.light_mode:
            st.query_params["theme"] = "light"
        else:
            if "theme" in st.query_params:
                del st.query_params["theme"]
                
    def _sync_mobile():
        st.session_state.is_mobile = st.session_state.mobile_mode_toggle
        st.query_params["is_mobile"] = str(st.session_state.mobile_mode_toggle).lower()

    with col_btn:
        if "base_font_size" not in st.session_state:
            st.session_state.base_font_size = 16
        st.markdown(f"<style>html {{ font-size: {st.session_state.base_font_size}px !important; }}</style>", unsafe_allow_html=True)
        
        # Popover minimalista para configurações
        with st.popover("⚙️ Configs", use_container_width=False):
            st.radio(
                "🌐 Idioma / Language", 
                options=["PT-BR", "EN"], 
                index=0 if st.session_state.get('language', 'PT-BR') == 'PT-BR' else 1,
                key="lang_radio",
                on_change=_muda_idioma,
                horizontal=True
            )
            
            st.number_input(
                "🔎 Fonte / Font Size", 
                min_value=10, 
                max_value=24, 
                value=st.session_state.base_font_size, 
                key="font_input", 
                on_change=_change_font
            )
            
            is_light = st.session_state.get("light_mode", False)
            toggle_label = "☀️ Modo Claro" if is_light else "🌙 Modo Escuro"
            st.toggle(toggle_label, value=is_light, key="light_mode_toggle", on_change=_sync_theme)
            
            st.toggle("📱 Modo Mobile", value=st.session_state.get("is_mobile", False), key="mobile_mode_toggle", on_change=_sync_mobile)
            
        mobile_str = "📱 Mobile" if st.session_state.is_mobile else "🖥️ Desktop"
        lang_str = st.session_state.get("language", "PT-BR")
        font_str = f"A {st.session_state.base_font_size}px"
        theme_str = "☀️ Light" if st.session_state.get("light_mode", False) else "🌙 Dark"
        st.markdown(f"<div style='font-size: 0.75rem; color: #888; text-align: right; margin-top: 4px;'>{mobile_str} | {lang_str} | {font_str} | {theme_str}</div>", unsafe_allow_html=True)

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
    
    # Criamos o expander para reduzir o espaço da interface
    menu_label = "🛠️ Menu Principal (Configurações e Navegação)" if st.session_state.get('language', 'PT-BR') == 'PT-BR' else "🛠️ Main Menu (Settings and Navigation)"
    menu_expander = st.expander(menu_label, expanded=False)
        
    with menu_expander:
        if current_mode_for_layout == "mode_3":
            col_menu_global = st.container()
            col_menu_especifico = st.container()
        else:
            col_menu_global, col_menu_especifico = st.columns(2)
            
        with col_menu_global.popover(i18n.t('modes_and_explanations'), use_container_width=True):
            # Usar <div> em vez de <h4> remove a âncora padrão e o espaçamento gigante do Streamlit
            st.markdown(f"<div style='margin-bottom:-15px; margin-top: -10px; font-size:1.1rem; font-weight:bold;'>{i18n.t('view_modes')}</div>", unsafe_allow_html=True)
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
                
            # Divisor mais compacto que o st.divider()
            st.markdown("<hr style='margin: 0px 0 15px 0; border: none; border-top: 1px solid rgba(150,150,150,0.3);'>", unsafe_allow_html=True)
            
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
            is_mobile = st.session_state.get("is_mobile", False)
            traduzir_cargos = st.session_state.get('language', 'PT-BR') == 'EN'
            
            if is_mobile:
                # Layout de coluna única empilhado para mobile
                cenario_sel = st.selectbox(i18n.t("select_scenario"), opcoes_cenarios, format_func=lambda x: i18n.t(x), key="cenario_sel")
                df_cenario = mapa_cenarios.get(cenario_sel)
                cargos_disponiveis = df_cenario['Carreira'].tolist() if df_cenario is not None and 'Carreira' in df_cenario.columns else (df_cenario.index.tolist() if df_cenario is not None else [])
                
                st.markdown("<div style='margin-top: 10px; margin-bottom: 5px;'></div>", unsafe_allow_html=True)
                incluir_comuns = st.checkbox(i18n.t("include_generic"), value=False)
                
                opcoes_matriz = ["condensed", "original"]
                tipo_matriz_raw = st.selectbox(
                    i18n.t("matrix_format"), 
                    opcoes_matriz, 
                    format_func=lambda x: i18n.t(x),
                    disabled=incluir_comuns,
                    key="tipo_matriz_raw"
                )
                tipo_matriz = "Original" if "original" in tipo_matriz_raw or incluir_comuns else "Condensada"
                
                # Valores padrão (opções ocultas no mobile)
                grupo_sel = "filter_all"
                default_cargos = cargos_disponiveis
                filtro_cargos = default_cargos
                cargos_destaque = []
                expandir_textos = False
                
            else:
                # Layout de 2 colunas para desktop (melhor distribuição)
                col1, col2 = st.columns([1, 1.2])
                
                with col1:
                    cenario_sel = st.selectbox(i18n.t("select_scenario"), opcoes_cenarios, format_func=lambda x: i18n.t(x), key="cenario_sel")
                    df_cenario = mapa_cenarios.get(cenario_sel)
                    cargos_disponiveis = df_cenario['Carreira'].tolist() if df_cenario is not None and 'Carreira' in df_cenario.columns else (df_cenario.index.tolist() if df_cenario is not None else [])
                    
                    cientifica_keywords = ["Perito", "Médico", "Fotógrafo", "Desenhista", "Necropsia", "Necrópsia", "Atendente"]
                    cargos_cientifica = [c for c in cargos_disponiveis if any(k in c for k in cientifica_keywords)]
                    cargos_pc = [c for c in cargos_disponiveis if c not in cargos_cientifica]
                    
                    st.markdown("<div style='margin-top: 5px; margin-bottom: 5px;'></div>", unsafe_allow_html=True)
                    incluir_comuns = st.checkbox(i18n.t("include_generic"), value=False)
                    
                    opcoes_matriz = ["condensed", "original"]
                    tipo_matriz_raw = st.selectbox(
                        i18n.t("matrix_format"), 
                        opcoes_matriz, 
                        format_func=lambda x: i18n.t(x),
                        disabled=incluir_comuns,
                        key="tipo_matriz_raw"
                    )
                    tipo_matriz = "Original" if "original" in tipo_matriz_raw or incluir_comuns else "Condensada"
                    
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
                        
                    expandir_textos = st.checkbox(i18n.t("expand_texts"), value=True)
                    
                with col2:
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
                        format_func=lambda x: i18n.traduzir_cargo(x) if traduzir_cargos else x,
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
                        format_func=lambda x: i18n.traduzir_cargo(x) if traduzir_cargos else x,
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
            tracker_text_color = "#333" if st.session_state.get('light_mode') else "#E0E0E0"
            tracker_bg = "rgba(0, 114, 178, 0.1)" if st.session_state.get('light_mode') else "rgba(0, 114, 178, 0.2)"
            rastreio_html = f"<div title='{i18n.t('tracking_title')}' style='cursor: help; background: {tracker_bg}; border: 1px solid #0072B2; padding: 6px 15px; border-radius: 8px; font-size: 0.85rem; color: {tracker_text_color}; width: 100%; margin-top: 5px;'>{i18n.t('tracking_main')} <strong style='color: #4da6ff;'>{c_sel_trans}</strong> ({i18n.t(cenario_a)}) ➔ <strong style='color: #4da6ff;'>{c_foco_trans}</strong> ({i18n.t(cenario_b)}) <span style='float:right'>ℹ️</span></div>"
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
        
    current_section = menu_expander.radio(
        "📍 Navegação Rápida:" if st.session_state.get('language', 'PT-BR') == 'PT-BR' else "📍 Quick Navigation:", 
        options=nav_options, 
        format_func=lambda x: i18n.t(x),
        key=f"nav_section_radio_{modo_visao_key}",
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
    text_matrix_full = data_processing.obter_atribuicoes_comuns_textuais(df_to_use, dic_siglas, expandir_textos=True)
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
        c_badge_cargos = "#1E2329" if st.session_state.get("light_mode") else "#C0C0C0"
        lista_cargos_html = f"<div style='text-align: right; color: {c_badge_cargos}; font-size: 0.9rem; margin-top: 5px; margin-bottom: 5px;'><strong>{i18n.t('badge_filtered_careers')}</strong> {', '.join(filtro_cargos)}</div>"
    
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
<div class="custom-metric-box" style="flex: 1; min-width: 140px; text-align: center; padding: 10px; border-radius: 8px;" title="{i18n.t('kpi_orig_help')}">
<div style="font-size: 0.65rem; color: #9E9E9E; font-weight: 600; text-transform: uppercase;">{i18n.t('kpi_orig_title')} <span style="cursor:help; color:#888; font-size:0.75rem;">ⓘ</span></div>
<div style="font-size: 1.1rem; line-height: 1.2;">{len(df_original_limpo.columns)}</div>
</div>
<div class="custom-metric-box" style="flex: 1; min-width: 140px; text-align: center; padding: 10px; border-radius: 8px;" title="{i18n.t('kpi_cond_help')}">
<div style="font-size: 0.65rem; color: #9E9E9E; font-weight: 600; text-transform: uppercase;">{i18n.t('kpi_cond_title')} <span style="cursor:help; color:#888; font-size:0.75rem;">ⓘ</span></div>
<div style="font-size: 1.1rem; line-height: 1.2;">{len(df_condensado.columns)}</div>
</div>
<div class="custom-metric-box" style="flex: 1; min-width: 140px; text-align: center; padding: 10px; border-radius: 8px;" title="{i18n.t('kpi_red_help')}">
<div style="font-size: 0.65rem; color: #9E9E9E; font-weight: 600; text-transform: uppercase;">{i18n.t('kpi_red_title')} <span style="cursor:help; color:#888; font-size:0.75rem;">ⓘ</span></div>
<div style="font-size: 1.1rem; color: #00C851; line-height: 1.2; font-weight: bold;">{reducao}</div>
</div>
<div class="custom-metric-box" style="flex: 1; min-width: 140px; text-align: center; padding: 10px; border-radius: 8px;" title="{i18n.t('kpi_pct_help')}">
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
        if st.session_state.get('language', 'PT-BR') == 'PT-BR':
            st.markdown(f"<p style='font-size: 0.85rem; color: #9E9E9E; margin-top: -15px; margin-bottom: 10px;'>{i18n.t('tip_hover')}</p>", unsafe_allow_html=True)
        lbl_matriz_translated = i18n.t('lbl_original') if tipo_matriz == 'Original' else i18n.t('lbl_condensed')
        c_scale = [[0, "#B0B5BA"], [1, "#0055A4"]] if st.session_state.get('light_mode') else "Teal"
        
        is_mobile = st.session_state.get("is_mobile", False)
        if is_mobile:
            st.info("📱 **Modo Simplificado (Mobile)**. Acesse em um Computador para visualizar o mapa de calor completo.", icon="ℹ️")
            
            # Corrige a extração dos nomes (podem estar na coluna 'Carreira' ou no index)
            opcoes_cargos_mobile = df_to_use_siglas['Carreira'].tolist() if 'Carreira' in df_to_use_siglas.columns else df_to_use_siglas.index.tolist()
            
            cargos_mobile_default = ["Perito Criminal", "Papiloscopista Policial", "Investigador de Polícia (+ Apoio)", "Investigador de Polícia"]
            cargos_mobile_default = [c for c in cargos_mobile_default if c in opcoes_cargos_mobile]
            if not cargos_mobile_default and len(opcoes_cargos_mobile) > 0:
                cargos_mobile_default = [opcoes_cargos_mobile[0]]
                
            cargos_mobile = st.multiselect(
                "🔍 Selecione carreiras para ver o total de atribuições:" if st.session_state.get('language', 'PT-BR') == 'PT-BR' else "🔍 Select careers to view the total of assignments:", 
                opcoes_cargos_mobile, 
                default=cargos_mobile_default,
                key="mobile_matrix_select"
            )
            
            if not cargos_mobile:
                st.warning("Selecione pelo menos uma carreira." if st.session_state.get('language', 'PT-BR') == 'PT-BR' else "Select at least one career.")
            else:
                if 'Carreira' in df_to_use_siglas.columns:
                    df_mobile = df_to_use_siglas[df_to_use_siglas['Carreira'].isin(cargos_mobile)]
                else:
                    df_mobile = df_to_use_siglas.loc[cargos_mobile]
                    
                fig_bin = visualizations.plot_mobile_binary_bars(df_mobile, cargos_destaque_ui, dic_reverso)
                st.plotly_chart(fig_bin, use_container_width=True)
                
                # Tabela listando as atribuições
                st.markdown("---")
                st.markdown("#### 📋 " + ("Lista de Atribuições" if st.session_state.get('language', 'PT-BR') == 'PT-BR' else "Assignments List"))
                
                df_temp = df_mobile.copy()
                if 'Carreira' in df_temp.columns:
                    df_temp = df_temp.set_index('Carreira')
                df_temp = df_temp.apply(pd.to_numeric, errors='coerce').fillna(0)
                df_long = df_temp.reset_index()
                df_long.rename(columns={df_long.columns[0]: 'Cargo'}, inplace=True)
                df_long = df_long.melt(id_vars='Cargo', var_name='Atribuição', value_name='Possui')
                df_long = df_long[df_long['Possui'] > 0][['Cargo', 'Atribuição']]
                if dic_reverso:
                    df_long['Atribuição'] = df_long['Atribuição'].map(lambda x: dic_reverso.get(x, x))
                
                # Renderizar como HTML para herdar o CSS global (Light/Dark mode)
                html_table = df_long.to_html(index=False, border=0, classes=["table", "table-striped"])
                # Adiciona um container com scroll e estilo básico
                st.markdown(f"""
                <div style="max-height: 400px; overflow-y: auto; font-size: 0.85rem;">
                    {html_table}
                </div>
                <style>
                    .table {{ width: 100%; border-collapse: collapse; }}
                    .table th, .table td {{ padding: 8px; text-align: left; border-bottom: 1px solid rgba(128,128,128,0.2); }}
                    .table th {{ font-weight: bold; }}
                </style>
                """, unsafe_allow_html=True)
                
                # Explicação Mobile
                if st.session_state.get('language', 'PT-BR') == 'PT-BR':
                    st.caption("⚠️ **Diferença entre Original e Condensada:** A versão Condensada aglutina a quantidade de atribuições dos cargos (agrupando redundâncias/sobreposições), enquanto a Original lista todas separadamente. As atribuições genéricas não necessariamente estão inclusas nas aglutinadas ou totais.")
                else:
                    st.caption("⚠️ **Original vs Condensed:** The Condensed version agglutinates the quantity of assignments of the roles (grouping redundancies/overlaps), while the Original lists them all separately. Generic assignments are not necessarily included in the agglutinated or total counts.")
        else:
            fig_bin = visualizations.plot_binary_heatmap(df_to_use_siglas, f"{i18n.t('title_matrix_prefix')} {lbl_matriz_translated} - {i18n.t(cenario_sel)}", colorscale=c_scale, dic_reverso=dic_reverso, cargos_destaque=cargos_destaque_ui)
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
        c_adj_kpi_title = "#1E2329" if st.session_state.get("light_mode") else "#ccc"
        st.markdown(f"<h4 style='margin-bottom: 15px; color:{c_adj_kpi_title}; font-size: 1.1rem;'>{i18n.t('adj_kpi_title')}</h4>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style="display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 25px;">
            <div class="custom-metric-box" style="flex: 1; min-width: 120px; padding: 10px; border-radius: 8px;">
                <div style="font-size: 0.65rem; color: #9E9E9E; text-transform: uppercase;">{i18n.t('adj_kpi_hub')}</div>
                <div style="font-size: 0.9rem; font-weight: bold; color: #4da6ff; margin-bottom: 3px;">{most_connected}</div>
                <div style="font-size: 0.75rem; color: #aaa;">{max_degree} {i18n.t('adj_kpi_connections')}</div>
            </div>
            <div class="custom-metric-box" style="flex: 1; min-width: 120px; padding: 10px; border-radius: 8px;">
                <div style="font-size: 0.65rem; color: #9E9E9E; text-transform: uppercase;">{i18n.t('adj_kpi_isolated')}</div>
                <div style="font-size: 0.9rem; font-weight: bold; color: #ff6b6b; margin-bottom: 3px;">{least_connected}</div>
                <div style="font-size: 0.75rem; color: #aaa;">{min_degree} {i18n.t('adj_kpi_connections')}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
            
        # 2. Render Heatmap (Somente Desktop) e Tabela
        is_mobile = st.session_state.get("is_mobile", False)
        
        if not is_mobile:
            col_adj_1, col_adj_2 = st.columns([6, 4])
            
            with col_adj_1:
                c_scale_adj = [[0.0, "#B0B5BA"], [0.001, "#deebf7"], [1.0, "#08519c"]] if st.session_state.get("light_mode") else "YlGnBu"
                fig_adj = visualizations.plot_adjacency_heatmap(adj_matrix, f"{i18n.t('title_adj_prefix')} - {i18n.t(cenario_sel)}", text_matrix=text_matrix, cargos_destaque=cargos_destaque_ui, colorscale=c_scale_adj)
                st.plotly_chart(fig_adj, use_container_width=True)
                if st.session_state.get('show_explanations', False):
                    tone_key = st.session_state.get('explanation_tone', 'tecnico')
                    st.info(explanations.get_explanation("adjacencia", tone_key, language=st.session_state.get('language', 'PT-BR')))
                    
            with col_adj_2:
                c_adj_top_pairs = "#1E2329" if st.session_state.get("light_mode") else "#ddd"
                st.markdown(f"<p style='font-size: 0.9rem; margin-bottom: 5px; color:{c_adj_top_pairs};'><strong>{i18n.t('adj_top_pairs')}</strong></p>", unsafe_allow_html=True)
                
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
                
                if st.session_state.get('light_mode'):
                    html_table = df_top_pairs.to_html(index=False, classes="light-table", border=0)
                    st.markdown(f'<div style="overflow-x: auto;">{html_table}</div>', unsafe_allow_html=True)
                else:
                    st.dataframe(df_top_pairs, use_container_width=True, hide_index=True)
        else:
            # Layout Mobile (Apenas Tabela)
            st.info("📱 **Modo Simplificado (Mobile)**. Acesse em um Computador para visualizar o mapa de calor completo.", icon="ℹ️")
            c_adj_top_pairs = "#1E2329" if st.session_state.get("light_mode") else "#ddd"
            st.markdown(f"<p style='font-size: 0.9rem; margin-bottom: 5px; margin-top: 15px; color:{c_adj_top_pairs};'><strong>{i18n.t('adj_top_pairs')}</strong></p>", unsafe_allow_html=True)
            
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
            
            if st.session_state.get('light_mode'):
                html_table = df_top_pairs.to_html(index=False, classes="table table-striped", border=0)
                st.markdown(f"""
                <div style="overflow-x: auto; font-size: 0.85rem;">
                    {html_table}
                </div>
                <style>
                    .table {{ width: 100%; border-collapse: collapse; }}
                    .table th, .table td {{ padding: 8px; text-align: left; border-bottom: 1px solid rgba(128,128,128,0.2); }}
                    .table th {{ font-weight: bold; }}
                </style>
                """, unsafe_allow_html=True)
            else:
                st.dataframe(df_top_pairs, use_container_width=True, hide_index=True)
                
            if st.session_state.get('show_explanations', False):
                tone_key = st.session_state.get('explanation_tone', 'tecnico')
                st.info(explanations.get_explanation("adjacencia", tone_key, language=st.session_state.get('language', 'PT-BR')))
            
        # 3. Gráfico Barras Full Width
        df_bar = degrees.reset_index()
        df_bar.columns = ['Cargo', 'Soma']
        if st.session_state.get('language', 'PT-BR') == 'EN' and traduzir_cargos:
            df_bar['Cargo'] = df_bar['Cargo'].map(lambda c: i18n.traduzir_cargo(c))
            
        import plotly.express as px
        font_color = "#1E2329" if st.session_state.get("light_mode") else "white"
        title_color = "#1E2329" if st.session_state.get("light_mode") else "#ccc"
        fig_bar = px.bar(
            df_bar,
            x='Soma', 
            y='Cargo', 
            orientation='h',
            labels={'Soma': i18n.t('adj_tbl_shared'), 'Cargo': ''},
            title=f"<span style='font-size:0.95rem; color:{title_color}'>{i18n.t('adj_bar_title')}</span>"
        )
        fig_bar.update_layout(
            plot_bgcolor='rgba(0,0,0,0)', 
            paper_bgcolor='rgba(0,0,0,0)', 
            font=dict(color=font_color),
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
                
                import plotly.express as px
                node_colors = px.colors.qualitative.Bold
                
                def get_c_hex(cargo_name):
                    import data_processing
                    return data_processing.get_cargo_color_hex(cargo_name, filtro_cargos_explorador)

                def hex_to_rgba(hex_str, alpha):
                    if not hex_str: return hex_str
                    # Se já for RGB ou RGBA do Plotly
                    if hex_str.startswith('rgb'):
                        import re
                        match = re.search(r'rgba?\((\d+),\s*(\d+),\s*(\d+)', hex_str)
                        if match:
                            return f"rgba({match.group(1)}, {match.group(2)}, {match.group(3)}, {alpha})"
                        return hex_str
                    
                    hex_str_clean = hex_str.lstrip('#')
                    if len(hex_str_clean) == 6:
                        r, g, b = tuple(int(hex_str_clean[i:i+2], 16) for i in (0, 2, 4))
                        return f"rgba({r}, {g}, {b}, {alpha})"
                    return hex_str

                def highlight_stats(row):
                    c_hex = get_c_hex(row.name)
                    if c_hex:
                        bg_color = hex_to_rgba(c_hex, 0.2)
                        return [f'background-color: {bg_color}; color: {c_hex}; font-weight: bold;'] * len(row)
                    return [''] * len(row)
                    
                import data_processing
                if st.session_state.get("light_mode"):
                    html_stats = data_processing.df_to_inline_html(df_stats, highlight_stats)
                    st.markdown(f'<div class="light-table-container">{html_stats}</div>', unsafe_allow_html=True)
                else:
                    styled_stats = df_stats.style.apply(highlight_stats, axis=1)
                    st.dataframe(styled_stats, use_container_width=True)
                st.markdown(i18n.t("cross_table"))
                
                for c in filtro_cargos_explorador:
                    if c in df_resultado.columns:
                        df_resultado[c] = df_resultado[c].apply(lambda x: '✔️' if isinstance(x, (int, float)) and x > 0 else '❌' if isinstance(x, (int, float)) and x == 0 else x)
    
                def highlight_cruzamento(row):
                    styles = []
                    for col in df_resultado.columns:
                        c_hex = get_c_hex(col)
                        if c_hex:
                            if row[col] == '✔️':
                                bg_color = hex_to_rgba(c_hex, 0.25)
                                styles.append(f'background-color: {bg_color}; color: {c_hex}; font-weight: bold;')
                            else:
                                bg_color_light = hex_to_rgba(c_hex, 0.06)
                                styles.append(f'background-color: {bg_color_light};')
                        else:
                            styles.append('')
                    return styles
    
                if st.session_state.get("light_mode"):
                    html_resultado = data_processing.df_to_inline_html(df_resultado, highlight_cruzamento)
                    st.markdown(f'<div class="light-table-container">{html_resultado}</div>', unsafe_allow_html=True)
                else:
                    styled_resultado = df_resultado.style.apply(highlight_cruzamento, axis=1)
                    st.dataframe(styled_resultado, use_container_width=True)
                
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
    
                styled_aba2 = df_filtro_atrib.style.apply(highlight_aba2, axis=1)
                if st.session_state.get("light_mode"):
                    st.markdown(f'<div class="light-table-container">{styled_aba2.to_html()}</div>', unsafe_allow_html=True)
                else:
                    st.dataframe(styled_aba2, use_container_width=True)
    
        if st.session_state.get('show_explanations', False):
            tone_key = st.session_state.get('explanation_tone', 'tecnico')
            st.info(explanations.get_explanation("explorador", tone_key, language=st.session_state.get('language', 'PT-BR')))
        if 'interaction_ui' in locals(): interaction_ui.render_like_button("1.3 Explorador Dinâmico", "1_3")


    # 1.4. Grafo de Similaridade
    elif current_section == 'sub_graph':
        if is_sample_biased:
            st.warning(explanations.get_short_bias_warning(language=st.session_state.get('language', 'PT-BR')), icon="🚨")
        is_mobile = st.session_state.get("is_mobile", False)
        if is_mobile:
            st.info("📱 **Modo Simplificado (Mobile)**. O limite inicial (threshold) do grafo foi ajustado dinamicamente para evitar nodos isolados e limpar a visualização.", icon="ℹ️")
            
        st.markdown("<div id='toc-graph'></div>", unsafe_allow_html=True)
        st.subheader(i18n.t("sub_graph"), help=i18n.t("sub_graph_help"))
        
        # Calculate optimal threshold dynamically for mobile:
        # Maximize threshold while keeping at least one connection for every node.
        import numpy as np
        adj_array = adj_matrix.to_numpy(dtype=float, copy=True)
        np.fill_diagonal(adj_array, 0)
        max_edges_per_node = adj_array.max(axis=1)
        optimal_mobile_thresh = int(max_edges_per_node.min())
        if optimal_mobile_thresh < 1:
            optimal_mobile_thresh = 1
            
        default_thresh = optimal_mobile_thresh if is_mobile else 1
        
        threshold_adj = st.slider(i18n.t("threshold_adj"), min_value=1, max_value=15, value=default_thresh, step=1)
        nodes_data, edges_data, pos = data_processing.gerar_dados_grafo(adj_matrix, threshold=threshold_adj, text_matrix=text_matrix)
        fig_grafo = visualizations.plot_network_graph(nodes_data, edges_data, i18n.t("title_network").format(threshold=threshold_adj) + f" - {i18n.t(cenario_sel)}", cargos_destaque=cargos_destaque_ui)
        st.plotly_chart(fig_grafo, use_container_width=True)
        if st.session_state.get('show_explanations', False):
            tone_key = st.session_state.get('explanation_tone', 'tecnico')
            st.info(explanations.get_explanation("grafo", tone_key, language=st.session_state.get('language', 'PT-BR')))
        if 'interaction_ui' in locals(): interaction_ui.render_like_button("1.4 Grafo de Similaridade", "1_4")
        
        with st.expander(i18n.t("graph_edges_table", default="Ver Lista de Conexões em Comum")):
            show_all_edges = st.radio(
                i18n.t("graph_edges_toggle", default="Filtro de Conexões:"),
                [i18n.t("graph_edges_active", default="Mostrar apenas conexões ativas no gráfico"), 
                 i18n.t("graph_edges_all", default="Mostrar todas as conexões")],
                index=0,
                key="graph_edges_radio"
            ) == i18n.t("graph_edges_all", default="Mostrar todas as conexões")
            
            edges_list = []
            cargos = list(adj_matrix.columns)
            for i in range(len(cargos)):
                for j in range(i + 1, len(cargos)):
                    weight = adj_matrix.iloc[i, j]
                    if weight > 0:
                        is_active = weight >= threshold_adj
                        if not show_all_edges and not is_active:
                            continue
                        c1 = cargos[i]
                        c2 = cargos[j]
                        attrs = text_matrix_full.iloc[i, j] if text_matrix_full is not None else ""
                        attrs_list = ", ".join([a.strip() for a in str(attrs).split("<br>") if a.strip()])
                        edges_list.append({
                            "Cargo 1": i18n.traduzir_cargo(c1) if st.session_state.get('language', 'PT-BR') == 'EN' else c1,
                            "Cargo 2": i18n.traduzir_cargo(c2) if st.session_state.get('language', 'PT-BR') == 'EN' else c2,
                            "Conexões em Comum": weight,
                            "Atribuições": attrs_list,
                            "Ativa": is_active
                        })
                        
            if edges_list:
                df_edges = pd.DataFrame(edges_list).sort_values(by="Conexões em Comum", ascending=False)
                
                def highlight_inactive_edge(row_display, row_edges):
                    if not row_edges["Ativa"]:
                        # If light mode, use a slightly darker grey to be visible
                        bg_c = "rgba(0,0,0,0.03)" if st.session_state.get('light_mode') else "rgba(255,255,255,0.05)"
                        color_c = "#a0a0a0" if st.session_state.get('light_mode') else "#666666"
                        return [f'color: {color_c}; background-color: {bg_c};'] * len(row_display)
                    return [''] * len(row_display)
                
                df_display = df_edges.drop(columns=["Ativa"])
                styled_edges = df_display.style.apply(lambda row: highlight_inactive_edge(row, df_edges.loc[row.name]), axis=1)
                
                if st.session_state.get('light_mode'):
                    # Custom light HTML table
                    html_table = df_display.to_html(index=False, classes="table table-striped", border=0)
                    st.markdown(f'<div class="light-table-container">{html_table}</div>', unsafe_allow_html=True)
                else:
                    st.dataframe(styled_edges, use_container_width=True, hide_index=True)
            else:
                st.write(i18n.t("graph_edges_empty", default="Nenhuma conexão encontrada com o filtro atual."))
    
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
            
        df_gower_15 = data_processing.calcular_distancias(df_para_gower, metric=selected_metric_key_15).fillna(1.0)
        
        if st.session_state.get('language', 'PT-BR') == 'EN' and traduzir_cargos:
            df_gower_15.index = [i18n.dic_traducao_cargos.get(c, c) for c in df_gower_15.index]
            df_gower_15.columns = [i18n.dic_traducao_cargos.get(c, c) for c in df_gower_15.columns]
        
        is_mobile = st.session_state.get("is_mobile", False)
        
        if not is_mobile:
            gower_bg = "#CED4DA" if st.session_state.get("light_mode") else "rgba(0,0,0,0)"
            fig_gower_heat = visualizations.plot_gower_heatmap(df_gower_15, f"{i18n.t('title_gower_prefix')} - {i18n.t(cenario_sel)}", cargos_destaque=cargos_destaque_ui, plot_bgcolor=gower_bg)
            st.plotly_chart(fig_gower_heat, use_container_width=True)
        else:
            # Layout Mobile (Apenas Tabela com menores distâncias)
            st.info("📱 **Modo Simplificado (Mobile)**. Acesse em um Computador para visualizar o mapa de calor completo.", icon="ℹ️")
            c_gower_top = "#1E2329" if st.session_state.get("light_mode") else "#ddd"
            st.markdown(f"<p style='font-size: 0.9rem; margin-bottom: 5px; margin-top: 15px; color:{c_gower_top};'><strong>{i18n.t('gower_top_pairs', default='Maiores Similaridades (Menores Distâncias)')}</strong></p>", unsafe_allow_html=True)
            
            df_g = df_gower_15.copy()
            df_g.index.name = 'Cargo 1'
            df_g.columns.name = 'Cargo 2'
            pairs_g = df_g.stack().reset_index()
            pairs_g.columns = ['Cargo 1', 'Cargo 2', 'Distância']
            pairs_g = pairs_g[pairs_g['Cargo 1'] != pairs_g['Cargo 2']]
            pairs_g['Pair'] = pairs_g.apply(lambda row: " - ".join(sorted([row['Cargo 1'], row['Cargo 2']])), axis=1)
            pairs_g = pairs_g.drop_duplicates(subset=['Pair'])
            
            lbl_5 = "Top 5"
            lbl_10 = "Top 10"
            lbl_all = i18n.t("lbl_all", default="Todos")
            qtd_pares_g = st.selectbox("Quantidade:", [lbl_5, lbl_10, lbl_all], index=0, label_visibility="collapsed", key="gower_qtd")
            
            limit_pairs_g = 5
            if qtd_pares_g == lbl_10:
                limit_pairs_g = 10
            elif qtd_pares_g == lbl_all:
                limit_pairs_g = len(pairs_g)
                
            top_pairs_g = pairs_g.sort_values(by='Distância', ascending=True).head(limit_pairs_g)
            top_pairs_g['Distância'] = top_pairs_g['Distância'].map(lambda x: f"{x:.3f}")
            
            df_top_g = top_pairs_g[['Pair', 'Distância']].rename(columns={'Pair': i18n.t('adj_tbl_pair'), 'Distância': 'Distância'})
            df_top_g.insert(0, '#', range(1, len(df_top_g) + 1))
            
            if st.session_state.get('light_mode'):
                html_table_g = df_top_g.to_html(index=False, classes="table table-striped", border=0)
                st.markdown(f"""
                <div style="overflow-x: auto; font-size: 0.85rem;">
                    {html_table_g}
                </div>
                <style>
                    .table {{ width: 100%; border-collapse: collapse; }}
                    .table th, .table td {{ padding: 8px; text-align: left; border-bottom: 1px solid rgba(128,128,128,0.2); }}
                    .table th {{ font-weight: bold; }}
                </style>
                """, unsafe_allow_html=True)
            else:
                st.dataframe(df_top_g, use_container_width=True, hide_index=True)
        
        # Histograma de Distribuição (Sugestão Visual 1)
        auto_zoom_15 = st.checkbox(i18n.t("ruler_zoom_toggle", default="🔍 Habilitar Zoom Automático (Ajustar gráfico à dispersão)"), value=True, key="ruler_zoom_15")
        nome_metrica = metric_options[selected_metric_key_15]
        titulo_hist = f"📈 {i18n.t('hist_title', default='Distribuição das Distâncias')} ({nome_metrica})"
        fig_hist = visualizations.plot_distance_histogram(df_gower_15, titulo_hist, full_scale=not auto_zoom_15)
        st.plotly_chart(fig_hist, use_container_width=True)
        
        st.markdown("💡 **Dica:** Abra o painel abaixo para ver como cada métrica calcula as distâncias.")
        with st.expander("📖 ABRIR TABELA COMPARATIVA DE MÉTRICAS"):
            df_comp = explanations.get_metrics_comparison_df()
            if st.session_state.get("light_mode"):
                st.markdown(f'<div class="light-table-container">{df_comp.to_html(index=False, escape=False)}</div>', unsafe_allow_html=True)
            else:
                st.dataframe(df_comp, use_container_width=True)
            
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
        
        is_mobile = st.session_state.get("is_mobile", False)
        if is_mobile:
            st.info("📱 **Modo Simplificado (Mobile)**. A régua foi rotacionada para a vertical garantindo o scroll (role para baixo para ver a assimetria).", icon="ℹ️")
    
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
            df_comp_16 = explanations.get_metrics_comparison_df()
            if st.session_state.get("light_mode"):
                st.markdown(f'<div class="light-table-container">{df_comp_16.to_html(index=False, escape=False)}</div>', unsafe_allow_html=True)
            else:
                st.dataframe(df_comp_16, use_container_width=True)
            
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
        
        is_mobile = st.session_state.get("is_mobile", False)
        if is_mobile:
            st.info("📱 **Modo Simplificado (Mobile)**. A árvore hierárquica foi disposta lateralmente para evitar encavalamento de textos.", icon="ℹ️")
    
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
                df_comp_17 = explanations.get_metrics_comparison_df()
                if st.session_state.get("light_mode"):
                    st.markdown(f'<div class="light-table-container">{df_comp_17.to_html(index=False, escape=False)}</div>', unsafe_allow_html=True)
                else:
                    st.dataframe(df_comp_17, use_container_width=True)
                
                st.markdown("#### Métodos de Agrupamento (Linkage)")
                st.markdown(i18n.t("coph_corr_help", default="Mede o quanto o dendrograma preserva as distâncias originais. Valores próximos a 1 indicam que a árvore representa fielmente as distâncias."))
                df_comp_link = explanations.get_linkages_comparison_df()
                if st.session_state.get("light_mode"):
                    st.markdown(f'<div class="light-table-container">{df_comp_link.to_html(index=False, escape=False)}</div>', unsafe_allow_html=True)
                else:
                    st.dataframe(df_comp_link, use_container_width=True)
                
                st.markdown("#### Índices Cofenéticos (Cenário Atual)")
                st.markdown("<span style='color:#00cc00; font-weight:bold;'>Verde (≥0.90)</span> | <span style='color:#ffcc00; font-weight:bold;'>Amarelo (≥0.75)</span> | <span style='color:#ff9900; font-weight:bold;'>Laranja (≥0.50)</span> | <span style='color:#ff3333; font-weight:bold;'>Vermelho (<0.50)</span>", unsafe_allow_html=True)
                df_coph = data_processing.get_cophenetic_comparison_table(df_para_gower)
                
                def color_coph(val):
                    if isinstance(val, str):
                        if " (" in val:
                            val = val.split(" ")[0]
                        try:
                            val = float(val)
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
                        return f'background-color: #{r:02x}{g:02x}{b:02x}; color: black;'
                    return ''
                    
                if not df_coph.empty and "Métrica" in df_coph.columns:
                    df_coph = df_coph.set_index("Métrica")
                    
                if st.session_state.get("light_mode"):
                    html = data_processing.df_to_inline_html(df_coph, col_style_func=color_coph)
                    st.markdown(html, unsafe_allow_html=True)
                else:
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
        
        is_mobile = st.session_state.get("is_mobile", False)
        if is_mobile:
            st.info("📱 **Modo Simplificado (Mobile)**. O gráfico foi reduzido ao Top 10 para não esmagar as barras na tela. Acesse em um Computador para visualizar o Top 30 completo.", icon="ℹ️")
        
        df_upset = df_original_limpo.set_index('Carreira') if 'Carreira' in df_original_limpo.columns else df_original_limpo.copy()
        if st.session_state.get('language', 'PT-BR') == 'EN' and traduzir_cargos:
            df_upset.index = [i18n.traduzir_cargo(c) for c in df_upset.index]
            df_upset.columns = [i18n.traduzir_atribuicao(c) for c in df_upset.columns]
        fig_upset = visualizations.plot_upset_bar_chart(
            df_upset, 
            f"{i18n.t('upset_title')} - {i18n.t(cenario_sel)}", 
            cargos_destaque=cargos_destaque_ui,
            limit_top_n=10 if is_mobile else 30
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

