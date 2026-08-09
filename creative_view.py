import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import networkx as nx
from math import log2
import i18n
import data_processing
import interaction_ui
import time
import os
import shutil
from PIL import Image

# Configuração de Assets (Mascotes)
PROJECT_DIR = r"c:\Users\maiap\OneDrive\Desktop\Desenvolvimento\Estudo_Atribuicoes_PCSP"
ASSETS_DIR = os.path.join(PROJECT_DIR, "assets")
if not os.path.exists(ASSETS_DIR):
    os.makedirs(ASSETS_DIR)

ARTIFACTS_DIR = r"C:\Users\maiap\.gemini\antigravity-ide\brain\ae9371df-6c3c-41ab-8af3-b66cfecd9248"
MASCOTS = {
    "🐶 Inspetor Cão": {
        "file": "mascote_cao.png", "src": "mascot_dog_detective_1786284825702.png",
        "file_near": "mascote_cao_near2.png", "src_near": "mascot_dog_near2_1786300511995.png",
        "file_won": "mascote_cao_won3.png", "src_won": "mascot_cao_won3_1786301099627.png",
        "file_confused": "mascote_cao_confused.png", "src_confused": "mascot_cao_confused_1786301128224.png",
        "emojis": ["🐶❓", "🐶💭", "🐶😎", "🐶🎉", "🐶😵"]
    },
    "🦫 Investigadora Capi": {
        "file": "mascote_capivara.png", "src": "mascot_capybara_detective_fixed_1786287273240.png",
        "file_near": "mascote_capivara_near5.png", "src_near": "mascot_capivara_near5_1786301394405.png",
        "file_won": "mascote_capivara_won2.png", "src_won": "mascot_capybara_won2_1786300501230.png",
        "file_confused": "mascote_capivara_confused.png", "src_confused": "mascot_capivara_confused_1786301119865.png",
        "emojis": ["🦫❓", "🦫💭", "🦫😎", "🦫🎉", "🦫😵"]
    },
    "🦉 Oráculo (Coruja)": {
        "file": "mascote_coruja.png", "src": "mascot_owl_1786281349179.png",
        "file_near": "mascote_coruja_near2.png", "src_near": "mascot_owl_near2_1786300532712.png",
        "file_won": "mascote_coruja_won2.png", "src_won": "mascot_owl_won2_1786300542801.png",
        "file_confused": "mascote_coruja_confused.png", "src_confused": "mascot_coruja_confused_1786301137184.png",
        "emojis": ["🦉❓", "🦉💭", "🦉😎", "🦉🎉", "🦉😵"]
    }
}

# Auto-copia os assets gerados pela IA para a pasta pública
for mascot_data in MASCOTS.values():
    for f_key, s_key in [("file", "src"), ("file_near", "src_near"), ("file_won", "src_won"), ("file_confused", "src_confused")]:
        src_path = os.path.join(ARTIFACTS_DIR, mascot_data[s_key])
        dest_path = os.path.join(ASSETS_DIR, mascot_data[f_key])
        if os.path.exists(src_path):
            shutil.copy2(src_path, dest_path)

def render_creative_view(mapa_cenarios, cenario_sel, current_section):
    st.markdown("<div id='toc-creative-mode'></div>", unsafe_allow_html=True)
    st.markdown("## " + i18n.t("m5_intro_title", default="🎨 5. Creative / Interactive Mode"))
    st.markdown(i18n.t("m5_intro_desc", default="Bem-vindo ao laboratório criativo! Aqui exploramos os dados de formas menos convencionais e mais divertidas."))
    
    df_cenario = mapa_cenarios[cenario_sel]
    
    if current_section == "m5_sub_tree_title":
        render_taxonomic_tree(df_cenario)
    elif current_section == "m5_sub_akinator_title":
        render_akinator_game(df_cenario)

def render_taxonomic_tree(df_cenario):
    st.subheader(i18n.t("m5_tree_title", default="🌳 Árvore Taxonômica das Carreiras"))
    st.markdown(i18n.t("m5_tree_desc", default="Aqui visualizamos as carreiras da PCSP como se fossem espécies biológicas. Cargos na base da árvore compartilham as atribuições mais fundamentais e universais da polícia, sendo considerados mais 'basais' (primitivos). Conforme a árvore se ramifica, encontramos as funções mais especializadas e exclusivas, que formam os ramos mais 'derivados' e complexos."))
    
    if df_cenario is None or df_cenario.empty:
        st.error("Sem dados para o cenário selecionado.")
        return
        
    # Processa os dados
    df_clean = df_cenario.copy()
    if 'Carreira' in df_clean.columns:
        df_clean = df_clean.set_index('Carreira')
    
    # Binariza a matriz
    df_bin = (df_clean > 0).astype(int)
    
    # Calcula a frequência de cada atribuição (quão "basal" ela é)
    freq_atrib = df_bin.sum(axis=0)
    
    # Calcula um "score de basalidade" para cada cargo
    # Cargos com muitas atribuições basais e poucas derivadas ficam na base.
    cargo_scores = {}
    for cargo in df_bin.index:
        atribs = df_bin.columns[df_bin.loc[cargo] > 0]
        if len(atribs) == 0:
            cargo_scores[cargo] = 0
            continue
        # Média da frequência das atribuições do cargo
        score = sum(freq_atrib[a] for a in atribs) / len(atribs)
        cargo_scores[cargo] = score
        
    sorted_cargos = sorted(cargo_scores.keys(), key=lambda x: cargo_scores[x], reverse=True)
    
    tipo_arvore = st.radio(i18n.t("m5_tree_format", default="Formato da Árvore:"), [i18n.t("m5_tree_format_v", default="Cladograma Angular (V-shape)"), i18n.t("m5_tree_format_c", default="Dendrograma Clássico")], horizontal=True)
    
    if tipo_arvore == i18n.t("m5_tree_format_v", default="Cladograma Angular (V-shape)"):
        fig = _plot_vertical_cladogram(sorted_cargos, cargo_scores, df_bin, freq_atrib)
    else:
        fig = _plot_classical_dendrogram(sorted_cargos, cargo_scores, df_bin)
        
    st.plotly_chart(fig, use_container_width=True)
    
    if st.session_state.get('show_explanations', False):
        import explanations
        tone_key = st.session_state.get('explanation_tone', 'tecnico')
        st.info(explanations.get_explanation("taxonomic_tree", tone_key, language=st.session_state.get('language', 'PT-BR')))
        
    if 'interaction_ui' in globals(): interaction_ui.render_like_button("5.1 Arvore Taxonomica", "5_1")

def _plot_vertical_cladogram(sorted_cargos, cargo_scores, df_bin, freq_atrib):
    # Cria uma árvore ramificada em V (diagonal)
    import networkx as nx
    G = nx.DiGraph()
    
    # Adicionando um nó raiz implícito em (0.5, 0)
    root = "Origem"
    G.add_node(root, pos=(0.5, 0))
    
    max_score = max(cargo_scores.values()) if cargo_scores else 1
    min_score = min(cargo_scores.values()) if cargo_scores else 0
    
    nodes_x = np.linspace(0.1, 0.9, len(sorted_cargos))
    
    # Criamos a espinha dorsal principal conectando nós em zigue-zague
    last_node = root
    last_x, last_y = 0.5, 0
    
    for i, cargo in enumerate(sorted_cargos):
        if max_score > min_score:
            y = 1 - ((cargo_scores[cargo] - min_score) / (max_score - min_score))
        else:
            y = 1
        y = y * 0.8 + 0.2
        
        # Branch node point
        branch_y = (last_y + y) / 2
        branch_x = (last_x + nodes_x[i]) / 2
        branch_name = f"b_{i}"
        
        G.add_node(branch_name, pos=(branch_x, branch_y))
        G.add_node(cargo, pos=(nodes_x[i], y))
        
        G.add_edge(last_node, branch_name)
        G.add_edge(branch_name, cargo)
        
        last_node = branch_name
        last_x, last_y = branch_x, branch_y

    pos = nx.get_node_attributes(G, 'pos')
    
    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        # Linhas diretas (diagonal)
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
        
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=edge_x, y=edge_y, line=dict(width=2, color='#555'), mode='lines', hoverinfo='none'))
    
    node_x = []
    node_y = []
    text = []
    colors = []
    labels = []
    
    import plotly.express as px
    palette = px.colors.qualitative.Pastel
    
    for i, node in enumerate(G.nodes()):
        if node.startswith("b_") or node == root:
            continue # hide branch nodes
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        
        score = cargo_scores.get(node, 0)
        node_trad = i18n.traduzir_cargo(node)
        text.append(f"<b>{node_trad}</b><br>Score Basal: {score:.2f}")
        
        # Color based on score groups (arbitrary grouping for coloring)
        if score > 0.8 * max_score:
            colors.append(palette[2])
            labels.append("Muito Basal")
        elif score > 0.5 * max_score:
            colors.append(palette[1])
            labels.append("Intermediário")
        else:
            colors.append(palette[0])
            labels.append("Especializado (Derivado)")
            
    # Draw Legend groups
    for group, color in zip(["Muito Basal", "Intermediário", "Especializado (Derivado)"], [palette[2], palette[1], palette[0]]):
        fig.add_trace(go.Scatter(
            x=[None], y=[None], mode='markers',
            marker=dict(size=12, color=color),
            name=group
        ))
            
    fig.add_trace(go.Scatter(
        x=node_x, y=node_y, mode='markers+text',
        text=[i18n.traduzir_cargo(n).split(' ')[0] for n in G.nodes() if not n.startswith("b_") and n != root],
        textposition="top center",
        hovertext=text,
        hoverinfo="text",
        marker=dict(size=12, color=colors, line=dict(width=1, color='#333')),
        showlegend=False
    ))
    
    fig.update_layout(
        title="Cladograma Evolutivo das Carreiras (Ângulo V)",
        showlegend=True,
        legend_title="Grau Taxonômico",
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False), # Removed autorange="reversed"
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=650
    )
    return fig

def _plot_classical_dendrogram(sorted_cargos, cargo_scores, df_bin):
    import plotly.figure_factory as ff
    from scipy.spatial.distance import pdist
    
    dist_matrix = pdist(df_bin.values, metric='jaccard')
    labels_trad = [i18n.traduzir_cargo(c) for c in df_bin.index.tolist()]
    fig = ff.create_dendrogram(df_bin.values, orientation='left', labels=labels_trad)
    fig.update_layout(height=700, title="Dendrograma de Similaridade (Clássico)", xaxis_title="Distância de Ligação")
    return fig

# --- LÓGICA DO AKINATOR ---

def get_entropy(df):
    n = len(df)
    if n <= 1:
        return 0
    return log2(n)

def best_attribute_to_ask(df_remaining):
    # Qual atribuição divide o df atual o mais próximo possível de 50/50?
    if len(df_remaining) <= 1:
        return None
        
    best_attr = None
    min_diff = float('inf')
    
    total = len(df_remaining)
    for col in df_remaining.columns:
        counts = df_remaining[col].value_counts()
        has_attr = counts.get(1, 0)
        
        # Evita perguntas que não dividem nada
        if has_attr == 0 or has_attr == total:
            continue
            
        diff = abs(has_attr - (total / 2))
        if diff < min_diff:
            min_diff = diff
            best_attr = col
            
    return best_attr

def reset_game():
    st.session_state.akinator_state = "playing"
    st.session_state.akinator_remaining = None
    st.session_state.akinator_questions = []

def render_akinator_game(df_cenario):
    with st.expander(i18n.t("akinator_cheat_title", default="📖 Cola do Oráculo: Consulte as atribuições para saber o que responder"), expanded=False):
        st.markdown(i18n.t("akinator_cheat_desc", default="Se você não conhece os cargos a fundo, escolha um cargo abaixo para ver a lista exata de atribuições ativas dele. Você pode usar isso como 'cola' para responder às perguntas do oráculo sem errar!"))
        
        df_cola = df_cenario.copy()
        if 'Carreira' in df_cola.columns:
            df_cola = df_cola.set_index('Carreira')
            
        cargos_cola = sorted(df_cola.index.tolist())
        cargo_cola_sel = st.selectbox(i18n.t("akinator_cheat_select", default="Selecione um cargo para inspecionar:"), cargos_cola, format_func=i18n.traduzir_cargo, key="cola_cargo_sel")
        
        if cargo_cola_sel:
            row = df_cola.loc[cargo_cola_sel]
            atribs = row[row > 0].index.tolist()
            st.success(i18n.t("akinator_cheat_success", default="O cargo **{cargo}** possui **{count}** atribuições ativas neste cenário:").format(cargo=i18n.traduzir_cargo(cargo_cola_sel), count=len(atribs)))
            for a in atribs:
                st.markdown(f"- {i18n.traduzir_atribuicao(a)}")

    st.subheader(i18n.t("akinator_title", default="🔮 O Oráculo da PCSP (Adivinhador de Cargos)"))
    st.markdown(i18n.t("akinator_desc", default="Pense em um cargo da Polícia Civil. Eu vou tentar adivinhar qual é através das atribuições dele!"))
    
    if 'akinator_state' not in st.session_state:
        reset_game()
        
    col_config1, col_config2 = st.columns(2)
    with col_config1:
        tipo_jogo = st.radio(i18n.t("akinator_how_to_play", default="Como quer jogar?"), [i18n.t("akinator_mode_q", default="Perguntas (Modo Divertido)"), i18n.t("akinator_mode_m", default="Seleção Rápida (Multiselect)")], horizontal=True, on_change=reset_game)
    with col_config2:
        # Mascote options should remain original keys but format in UI
        mascote_sel = st.radio(i18n.t("akinator_choose_mascot", default="Escolha seu Mascote:"), list(MASCOTS.keys()), format_func=lambda x: i18n.t_lang(x, st.session_state.get('language', 'PT-BR')), horizontal=True)
    
    df_clean = df_cenario.copy()
    if 'Carreira' in df_clean.columns:
        df_clean = df_clean.set_index('Carreira')
    df_bin = (df_clean > 0).astype(int)
    
    if st.session_state.akinator_remaining is None:
        st.session_state.akinator_remaining = df_bin.copy()
    
    # Exibe a imagem do Mascote no canto
    mascot_img_path = os.path.join(ASSETS_DIR, MASCOTS[mascote_sel]["file"])
    
    st.markdown("---")
    
    if tipo_jogo == i18n.t("akinator_mode_m", default="Seleção Rápida (Multiselect)"):
        col_img, col_ui = st.columns([1, 4])
        with col_img:
            if os.path.exists(mascot_img_path):
                st.image(Image.open(mascot_img_path), use_container_width=True)
        with col_ui:
            todas_atrib = df_bin.columns.tolist()
            selecionadas = st.multiselect(i18n.t("akinator_select_attr", default="Selecione as atribuições que seu cargo faz:"), todas_atrib, format_func=i18n.traduzir_atribuicao)
            if selecionadas:
                df_match = df_bin.copy()
                for s in selecionadas:
                    df_match = df_match[df_match[s] == 1]
                    
                cargos_restantes = df_match.index.tolist()
                if len(cargos_restantes) == 0:
                    st.error(i18n.t("akinator_no_match", default="Nenhum cargo faz essa combinação exata!"))
                elif len(cargos_restantes) == 1:
                    st.success(i18n.t("akinator_is", default="🎉 É o **{cargo}**!").format(cargo=i18n.traduzir_cargo(cargos_restantes[0])))
                else:
                    cargos_trad = [i18n.traduzir_cargo(c) for c in cargos_restantes]
                    st.warning(i18n.t("akinator_could_be", default="🤔 Pode ser: {cargos}").format(cargos=', '.join(cargos_trad)))
    else:
        # Modo Perguntas Interativas
        df_rem = st.session_state.akinator_remaining
        
        n_restantes = len(df_rem)
        n_total = len(df_bin)
        pct_restante = n_restantes / n_total if n_total > 0 else 1
        
        # Emojis baseados no mascote escolhido [confuso, pensativo, confiante, ganhou, derrotado]
        emojis_mascote = MASCOTS[mascote_sel]["emojis"]
        mascote_emoji = emojis_mascote[0] # Confuso
        mascot_file_key = "file"
        
        if n_restantes == 0:
            mascote_emoji = emojis_mascote[4] # Derrotado / Confuso Doido
            mascot_file_key = "file_confused"
        elif n_restantes == 1:
            mascote_emoji = emojis_mascote[3] # Ganhou
            mascot_file_key = "file_won"
        elif pct_restante < 0.3:
            mascote_emoji = emojis_mascote[2] # Confiante
            mascot_file_key = "file_near"
        elif pct_restante < 0.7:
            mascote_emoji = emojis_mascote[1] # Pensativo
            mascot_file_key = "file"
            
        mascot_img_path_dynamic = os.path.join(ASSETS_DIR, MASCOTS[mascote_sel][mascot_file_key])
            
        col_img, col_ui = st.columns([1, 4])
        with col_img:
            if os.path.exists(mascot_img_path_dynamic):
                st.image(Image.open(mascot_img_path_dynamic), use_container_width=True)
                
        with col_ui:
            mascote_sel_trad = i18n.t_lang(mascote_sel, st.session_state.get('language', 'PT-BR'))
            nome_personagem = mascote_sel_trad.split(' ', 1)[1] if ' ' in mascote_sel_trad else mascote_sel_trad
            if n_restantes == 0:
                st.markdown(f"### {mascote_emoji} **{nome_personagem} " + i18n.t("akinator_lost", default="está em pane...") + "**")
            elif n_restantes == 1:
                st.markdown(f"### {mascote_emoji} **{nome_personagem} " + i18n.t("akinator_won", default="desvendou o mistério!") + "**")
            elif pct_restante < 0.3:
                st.markdown(f"### {mascote_emoji} **{nome_personagem} " + i18n.t("akinator_near", default="está quase lá...") + "**")
            else:
                st.markdown(f"### {mascote_emoji} **{nome_personagem} " + i18n.t("akinator_thinking", default="está pensando...") + "**")
            st.caption(i18n.t("akinator_remaining", default="Cargos possíveis restantes: {n}").format(n=n_restantes))
            
            with st.expander(i18n.t("akinator_show_possibilities", default="🕵️ Ver status dos cargos (Eliminados vs Possíveis)"), expanded=False):
                todas_carreiras = set(df_bin.index)
                carreiras_restantes = set(df_rem.index)
                carreiras_eliminadas = todas_carreiras - carreiras_restantes
                
                col_possivel, col_eliminado = st.columns(2)
                with col_possivel:
                    st.markdown(f"**{i18n.t('akinator_possible', default='Ainda Possíveis')}:**")
                    for c in sorted(carreiras_restantes):
                        st.markdown(f"- ✅ {i18n.traduzir_cargo(c)}")
                with col_eliminado:
                    st.markdown(f"**{i18n.t('akinator_eliminated', default='Eliminados')}:**")
                    for c in sorted(carreiras_eliminadas):
                        st.markdown(f"- ❌ ~{i18n.traduzir_cargo(c)}~")
                        
                st.markdown("---")
                qtd_perguntas = len(st.session_state.akinator_questions)
                st.markdown(f"**{i18n.t('akinator_questions_count', default='Perguntas Realizadas')}: {qtd_perguntas}**")
                if qtd_perguntas > 0:
                    for q in st.session_state.akinator_questions:
                        st.markdown(f"- {i18n.traduzir_atribuicao(q)}")
            
            if n_restantes == 0:
                st.error(i18n.t("akinator_lost_desc", default="Fui derrotado! Você pensou em uma combinação que não existe (ou que a lei esqueceu)."))
                if st.button(i18n.t("akinator_play_again", default="Jogar Novamente")):
                    reset_game()
                    st.rerun()
            elif n_restantes == 1:
                st.success(i18n.t("akinator_won_desc", default="Eu sei! Você pensou em: **{cargo}**!").format(cargo=i18n.traduzir_cargo(df_rem.index[0])))
                if st.button(i18n.t("akinator_play_again", default="Jogar Novamente")):
                    reset_game()
                    st.rerun()
            else:
                best_q = best_attribute_to_ask(df_rem)
                if best_q is None:
                    cargos_trad = [i18n.traduzir_cargo(c) for c in df_rem.index]
                    st.warning(i18n.t("akinator_tie", default="Não consigo desempatar! Pode ser qualquer um destes:") + f" {', '.join(cargos_trad)}")
                    if st.button(i18n.t("akinator_play_again", default="Jogar Novamente")):
                        reset_game()
                        st.rerun()
                else:
                    st.markdown(f"#### " + i18n.t("akinator_your_role", default="Seu cargo faz isso: **'{attr}'**?").format(attr=i18n.traduzir_atribuicao(best_q)))
                    
                    col_s, col_n, col_p = st.columns([1,1,1])
                    with col_s:
                        if st.button("✅ " + i18n.t("akinator_btn_yes", default="Sim"), use_container_width=True):
                            st.session_state.akinator_questions.append(best_q)
                            st.session_state.akinator_remaining = df_rem[df_rem[best_q] == 1].drop(columns=[best_q])
                            st.rerun()
                    with col_n:
                        if st.button("❌ " + i18n.t("akinator_btn_no", default="Não"), use_container_width=True):
                            st.session_state.akinator_questions.append(best_q)
                            st.session_state.akinator_remaining = df_rem[df_rem[best_q] == 0].drop(columns=[best_q])
                            st.rerun()
                    with col_p:
                        if st.button("⏭️ " + i18n.t("akinator_btn_skip", default="Não Sei / Pular"), use_container_width=True):
                            st.session_state.akinator_questions.append(best_q)
                            st.session_state.akinator_remaining = df_rem.drop(columns=[best_q])
                            st.rerun()

    if st.session_state.get('show_explanations', False):
        import explanations
        tone_key = st.session_state.get('explanation_tone', 'tecnico')
        st.info(explanations.get_explanation("akinator", tone_key, language=st.session_state.get('language', 'PT-BR')))

    if 'interaction_ui' in globals(): interaction_ui.render_like_button("5.2 Adivinhador de Cargos", "5_2")
