import streamlit as st
import streamlit.components.v1 as components
import networkx as nx
import importlib
import explanations
importlib.reload(explanations)
import pandas as pd
import data_loader
import data_processing
import visualizations
import logger
import os
import explanations
import importlib
import i18n
importlib.reload(explanations)
importlib.reload(i18n)
importlib.reload(i18n)


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
            <span style="font-size: 1.2rem;">💬</span> __FOOTER_TITLE__
        </div>
        <div class="hud-content">
            <h4>__REF_TITLE__</h4>
            <span style="font-size: 0.75rem; color: #A0A0A0; display: block; margin: -5px 0 8px 0; font-style: italic;">__REF_DESC__</span>
            <a href="https://github.com/phsmaia/Estudo_Atribuicoes_PCSP_2024" target="_blank">__REPO__</a>
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

# --- CARREGAMENTO DE DADOS ---
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

    col_label, col_radio = st.columns([2, 8])
    with col_label:
        st.markdown(f"<h4 style='margin:0; margin-top:5px; font-size:1.1rem; color:#ccc;'>{i18n.t('view_modes')}</h4>", unsafe_allow_html=True)
    with col_radio:
        if 'modo_index' not in st.session_state:
            st.session_state.modo_index = 0
            
        opcoes_modos = [i18n.t("mode_1"), i18n.t("mode_2"), i18n.t("mode_3"), i18n.t("mode_4")]
        
        modo_visao = st.radio(
            i18n.t("nav_analytic"),
            opcoes_modos,
            index=st.session_state.modo_index,
            horizontal=True,
            label_visibility="collapsed"
        )
        
        st.session_state.modo_index = opcoes_modos.index(modo_visao)
        
    col_exp_1, col_exp_2 = st.columns([3, 7])
    with col_exp_1:
        st.toggle(i18n.t("explanation_mode"), key="show_explanations")
    with col_exp_2:
        if st.session_state.get('show_explanations', False):
            st.radio(i18n.t("reading_tone"), ["tecnico", "leigo"], format_func=lambda x: i18n.t("tone_academic") if x == "tecnico" else i18n.t("tone_layman"), horizontal=True, label_visibility="collapsed", key="explanation_tone")
        
    is_sample_biased_global = False
    
    # --- CONTROLES SUPERIORES (APENAS EXPLORADOR INDIVIDUAL) ---
    if modo_visao == i18n.t("mode_1"):
        with st.popover(i18n.t("config_analytic"), use_container_width=True):
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
                filtro_cargos = st.multiselect(
                    i18n.t("roles_analyze"), 
                    cargos_disponiveis,
                    default=default_cargos,
                    format_func=lambda x: i18n.traduzir_cargo(x) if st.session_state.get('language', 'PT-BR') == 'EN' else x,
                    key="filtro_cargos"
                )

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
        with st.popover(i18n.t("config_compare"), use_container_width=True):
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
            
        with st.popover(i18n.t("m4_config_title"), use_container_width=True):
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



if is_sample_biased_global:
    st.warning(explanations.get_bias_warning(language=st.session_state.get('language', 'PT-BR')), icon="⚠️")

if modo_visao == i18n.t("mode_2"):
    with st.spinner("🚓 Cruzando evidências de cenários... Por favor, aguarde." if st.session_state.get('language', 'PT-BR') == 'PT-BR' else "🚓 Cross-referencing scenario evidence... Please wait."):
        import comparative_view
        import importlib
        importlib.reload(comparative_view)
        comparative_view.render_comparativo_axb(opcoes_cenarios, mapa_cenarios, cenario_a, cenario_b, carreira_sel_comparativo, cargos_destaque_2)
    st.stop()
    
elif modo_visao == i18n.t("mode_3"):
    with st.spinner("🕵️‍♂️ Compilando a visão macro da corporação... Por favor, aguarde." if st.session_state.get('language', 'PT-BR') == 'PT-BR' else "🕵️‍♂️ Compiling macro corporate view... Please wait."):
        import timeline_view
        import importlib
        importlib.reload(timeline_view)
        timeline_view.render_timeline_mode(opcoes_cenarios, mapa_cenarios)
    st.stop()
    
elif modo_visao == i18n.t("mode_4"):
    with st.spinner("🔍 Rastreando rotas evolutivas longitudinais... Por favor, aguarde." if st.session_state.get('language', 'PT-BR') == 'PT-BR' else "🔍 Tracking longitudinal evolutionary routes... Please wait."):
        import longitudinal_view
        import importlib
        importlib.reload(longitudinal_view)
        longitudinal_view.render_longitudinal_mode(opcoes_cenarios, mapa_cenarios, filtro_cargos_long, cargos_destaque_long)
    st.stop()
    

# Registrar log invisível de visita
if 'visit_logged' not in st.session_state:
    logger.log_visit(cenario_sel)


if df_cenario is not None and not df_cenario.empty:
    with st.spinner("🚨 Processando evidências normativas e consolidando matriz... Por favor, aguarde." if st.session_state.get('language', 'PT-BR') == 'PT-BR' else "🚨 Processing normative evidence and consolidating matrix... Please wait."):
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
    st.subheader(f"{i18n.t('sub_matrix')} ({i18n.t('lbl_original') if tipo_matriz == 'Original' else i18n.t('lbl_condensed')})", help=i18n.t('sub_matrix_help'))
    st.markdown(f"<p style='font-size: 0.85rem; color: #9E9E9E; margin-top: -15px; margin-bottom: 10px;'>{i18n.t('tip_hover')}</p>", unsafe_allow_html=True)
    lbl_matriz_translated = i18n.t('lbl_original') if tipo_matriz == 'Original' else i18n.t('lbl_condensed')
    fig_bin = visualizations.plot_binary_heatmap(df_to_use_siglas, f"{i18n.t('title_matrix_prefix')} {lbl_matriz_translated} - {i18n.t(cenario_sel)}", colorscale="Teal", dic_reverso=dic_reverso, cargos_destaque=cargos_destaque_ui)
    st.plotly_chart(fig_bin, use_container_width=True)
    if st.session_state.get('show_explanations', False):
        raw_tone = st.session_state.get('explanation_tone', i18n.t("tone_academic"))
        tone_key = "tecnico" if raw_tone == i18n.t("tone_academic") else "leigo"
        st.info(explanations.get_explanation("matriz", tone_key, language=st.session_state.get('language', 'PT-BR')))
    
    # 1.2. Matriz de Adjacência
    if is_sample_biased:
        st.warning(explanations.get_short_bias_warning(language=st.session_state.get('language', 'PT-BR')), icon="🚨")
    st.subheader(i18n.t('sub_adj'), help=i18n.t('sub_adj_help'))
    adj_matrix = data_processing.gerar_matriz_adjacencia(df_to_use)
    fig_adj = visualizations.plot_adjacency_heatmap(adj_matrix, f"{i18n.t('title_adj_prefix')} - {i18n.t(cenario_sel)}", text_matrix=text_matrix, cargos_destaque=cargos_destaque_ui)
    st.plotly_chart(fig_adj, use_container_width=True)
    if st.session_state.get('show_explanations', False):
        raw_tone = st.session_state.get('explanation_tone', i18n.t("tone_academic"))
        tone_key = "tecnico" if raw_tone == i18n.t("tone_academic") else "leigo"
        st.info(explanations.get_explanation("adjacencia", tone_key, language=st.session_state.get('language', 'PT-BR')))

    st.markdown("---")

    # 1.3. Explorador Dinâmico
    if is_sample_biased:
        st.warning(explanations.get_short_bias_warning(language=st.session_state.get('language', 'PT-BR')), icon="🚨")
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
        raw_tone = st.session_state.get('explanation_tone', i18n.t("tone_academic"))
        tone_key = "tecnico" if raw_tone == i18n.t("tone_academic") else "leigo"
        st.info(explanations.get_explanation("explorador", tone_key, language=st.session_state.get('language', 'PT-BR')))

    st.markdown("---")

    # 1.4. Grafo de Similaridade
    if is_sample_biased:
        st.warning(explanations.get_short_bias_warning(language=st.session_state.get('language', 'PT-BR')), icon="🚨")
    st.subheader(i18n.t("sub_graph"), help=i18n.t("sub_graph_help"))
    threshold_adj = st.slider(i18n.t("threshold_adj"), min_value=1, max_value=15, value=1, step=1)
    nodes_data, edges_data, pos = data_processing.gerar_dados_grafo(adj_matrix, threshold=threshold_adj, text_matrix=text_matrix)
    fig_grafo = visualizations.plot_network_graph(nodes_data, edges_data, i18n.t("title_network").format(threshold=threshold_adj) + f" - {i18n.t(cenario_sel)}", cargos_destaque=cargos_destaque_ui)
    st.plotly_chart(fig_grafo, use_container_width=True)
    if st.session_state.get('show_explanations', False):
        raw_tone = st.session_state.get('explanation_tone', i18n.t("tone_academic"))
        tone_key = "tecnico" if raw_tone == i18n.t("tone_academic") else "leigo"
        st.info(explanations.get_explanation("grafo", tone_key, language=st.session_state.get('language', 'PT-BR')))

    st.markdown("---")

    # 1.5. Mapa de Calor Gower
    if is_sample_biased:
        st.warning(explanations.get_short_bias_warning(language=st.session_state.get('language', 'PT-BR')), icon="🚨")
    st.subheader(i18n.t("sub_gower"), help=i18n.t("sub_gower_help"))
    
    df_para_gower = df_to_use.copy()
    if incluir_comuns:
        num_cargos_reais = len(df_para_gower)
        numeric_cols = df_para_gower.select_dtypes(include='number').columns
        pseudo_row = (df_para_gower[numeric_cols].sum(axis=0) == num_cargos_reais).astype(int)
        if 'Carreira' in df_para_gower.columns:
            pseudo_row['Carreira'] = "Policial Civil (todos os cargos)"
        pseudo_row.name = "Policial Civil (todos os cargos)"
        df_para_gower.loc[pseudo_row.name] = pseudo_row
        
    df_gower = data_processing.calcular_distancias_gower(df_para_gower)
    
    if st.session_state.get('language', 'PT-BR') == 'EN' and traduzir_cargos:
        df_gower.index = [i18n.dic_traducao_cargos.get(c, c) for c in df_gower.index]
        df_gower.columns = [i18n.dic_traducao_cargos.get(c, c) for c in df_gower.columns]
    
    fig_gower_heat = visualizations.plot_gower_heatmap(df_gower, f"{i18n.t('title_gower_prefix')} - {i18n.t(cenario_sel)}", cargos_destaque=cargos_destaque_ui)
    st.plotly_chart(fig_gower_heat, use_container_width=True)
    if st.session_state.get('show_explanations', False):
        raw_tone = st.session_state.get('explanation_tone', i18n.t("tone_academic"))
        tone_key = "tecnico" if raw_tone == i18n.t("tone_academic") else "leigo"
        st.info(explanations.get_explanation("gower", tone_key, language=st.session_state.get('language', 'PT-BR')))

    st.markdown("---")
    
    # 1.6. Régua Gower
    if is_sample_biased:
        st.warning(explanations.get_short_bias_warning(language=st.session_state.get('language', 'PT-BR')), icon="🚨")
    st.subheader(i18n.t("sub_ruler"), help=i18n.t("sub_ruler_help"))

    ref_cargo_opcoes = list(df_gower.columns)
    ref_cargo = st.selectbox(
        i18n.t("select_ruler_role"), 
        ref_cargo_opcoes, 
        index=0,
        format_func=lambda x: f"{x} {i18n.t('used_in_paper')}" if x in ["Delegado de Polícia", "Police Chief"] else x
    )
    fig_gower_ruler = visualizations.plot_gower_ruler(df_gower, reference_career=ref_cargo, cargos_destaque=cargos_destaque)
    st.plotly_chart(fig_gower_ruler, use_container_width=True)
    if st.session_state.get('show_explanations', False):
        raw_tone = st.session_state.get('explanation_tone', i18n.t("tone_academic"))
        tone_key = "tecnico" if raw_tone == i18n.t("tone_academic") else "leigo"
        st.info(explanations.get_explanation("regua", tone_key, language=st.session_state.get('language', 'PT-BR')))

    st.markdown("---")

    # 1.7. Dendograma
    if is_sample_biased:
        st.warning(explanations.get_short_bias_warning(language=st.session_state.get('language', 'PT-BR')), icon="🚨")
    st.subheader(i18n.t("sub_dendro"), help=i18n.t("sub_dendro_help"))
    st.markdown(i18n.t("dendro_method"))
    if len(df_gower.columns) > 1:
        fig_dendro = visualizations.plot_dendrogram(df_gower, f"{i18n.t('dendro_title')} - {i18n.t(cenario_sel)}", cargos_destaque=cargos_destaque_ui)
        st.plotly_chart(fig_dendro, use_container_width=True)
    else:
        st.warning(i18n.t("dendro_warning"))

    if st.session_state.get('show_explanations', False):
        raw_tone = st.session_state.get('explanation_tone', i18n.t("tone_academic"))
        tone_key = "tecnico" if raw_tone == i18n.t("tone_academic") else "leigo"
        st.info(explanations.get_explanation("dendograma", tone_key, language=st.session_state.get('language', 'PT-BR')))

    st.markdown("---")

    # 1.8. UpSet Plot (Alternativa ao Venn)
    if is_sample_biased:
        st.warning(explanations.get_short_bias_warning(language=st.session_state.get('language', 'PT-BR')), icon="🚨")
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
        raw_tone = st.session_state.get('explanation_tone', i18n.t("tone_academic"))
        tone_key = "tecnico" if raw_tone == i18n.t("tone_academic") else "leigo"
        st.info(explanations.get_explanation("upset", tone_key, language=st.session_state.get('language', 'PT-BR')))

else:
    st.error("Cenário indisponível.")

# Padding para não esconder gráficos atrás do botão de rodapé
st.markdown("<div style='height: 150px;'></div>", unsafe_allow_html=True)


