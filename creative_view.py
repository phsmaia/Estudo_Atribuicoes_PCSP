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
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
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
    },
    "🐺 Lobo-Guará Secreto": {
        "file": "mascote_lobo.png", "src": "mascot_wolf_1786318952220.png",
        "file_near": "mascote_lobo_near.png", "src_near": "mascot_wolf_near_v2_1786319184109.png",
        "file_won": "mascote_lobo_won.png", "src_won": "mascot_wolf_won_v5_1786409325010.png",
        "file_confused": "mascote_lobo_confused.png", "src_confused": "mascot_wolf_confused_v2_1786319193276.png",
        "emojis": ["🐺❓", "🐺💭", "🐺😎", "🐺🎉", "🐺😵"]
    }
}

def ensure_assets_copied():
    # Auto-copia os assets gerados pela IA para a pasta pública
    for mascot_data in MASCOTS.values():
        for f_key, s_key in [("file", "src"), ("file_near", "src_near"), ("file_won", "src_won"), ("file_confused", "src_confused")]:
            src_path = os.path.join(ARTIFACTS_DIR, mascot_data[s_key])
            dest_path = os.path.join(ASSETS_DIR, mascot_data[f_key])
            if os.path.exists(src_path):
                # Copy only if file doesn't exist or is older
                if not os.path.exists(dest_path) or os.path.getmtime(src_path) > os.path.getmtime(dest_path):
                    shutil.copy2(src_path, dest_path)

def render_creative_view(mapa_cenarios, cenario_sel, current_section):
    ensure_assets_copied()
    
    df_cenario = mapa_cenarios[cenario_sel]
    
    if current_section == "m5_sub_tree_title":
        st.markdown("<div id='toc-creative-mode'></div>", unsafe_allow_html=True)
        st.markdown("## " + i18n.t("m5_intro_title", default="🎨 5. Creative / Interactive Mode"))
        st.markdown(i18n.t("m5_intro_desc", default="Bem-vindo ao laboratório criativo! Aqui exploramos os dados de formas menos convencionais e mais divertidas."))
        render_taxonomic_tree(df_cenario)
    elif current_section == "m5_sub_akinator_title":
        render_akinator_game(df_cenario)

def render_taxonomic_tree(df_cenario):
    st.markdown("<div id='toc-tree'></div>", unsafe_allow_html=True)
    col_sub, col_tut = st.columns([85, 15], vertical_alignment="center")
    with col_sub:
        st.subheader(i18n.t("m5_tree_title", default="🌳 Árvore Taxonômica das Carreiras"), help=i18n.t("m5_tree_desc"))
    with col_tut:
        with st.popover(i18n.t("tutorial_popover", default="Tutorial")):
            st.info(i18n.t("m5_tree_desc"))
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
    
    # Calcula a frequência de cada atribuição para uso de plotagem
    freq_atrib = df_bin.sum(axis=0)

    # --- LÓGICA CLADÍSTICA (Biopython) ---
    from Bio.Phylo.TreeConstruction import DistanceMatrix, DistanceTreeConstructor
    from Bio import Phylo
    from scipy.spatial.distance import pdist, squareform
    import networkx as nx

    # Remove a pseudo-carreira injetada globalmente pela opção de Atribuições Comuns no app.py (se houver)
    df_tree = df_bin.copy()
    pseudo_row_name = "Policial Civil (todos os cargos)"
    if pseudo_row_name in df_tree.index:
        df_tree = df_tree.drop(index=pseudo_row_name)
        
    # Matriz de distância Jaccard (apropriada para presenças e ausências filogenéticas)
    dist_array = pdist(df_tree, metric='jaccard')
    dist_sq = squareform(dist_array)
    
    # Formatar para o Biopython DistanceMatrix (lista de listas triangular inferior)
    names = df_tree.index.tolist()
    matrix = []
    for i in range(len(names)):
        matrix.append(dist_sq[i, :i+1].tolist())
        
    dm = DistanceMatrix(names, matrix)
    
    # Adicionar o seletor de algoritmo se não estiver no mobile
    is_mobile = st.session_state.get("is_mobile", False)
    # Toggles removidos: O conceito de cladograma exige que a evolução (Autapomorfias) 
    # seja sempre destrinchada e as atribuições sempre mostradas nos hovers/expansores.
    mostrar_atribuicoes = True
    separar_evolucao = True
    opcoes_estilos = [
        "🌿 Tradicional (Científico)",
        i18n.t("m5_clade_fish", default="🐟 Espinha de Peixe (Angular)"),
        i18n.t("m5_clade_circular", default="🌀 Circular (Radial)")
    ]
    estilo_cladograma = st.radio(i18n.t("m5_clade_style", default="Estilo Visual:"), opcoes_estilos, horizontal=True)
    
    opcoes_algoritmo = ["UPGMA (Cladograma Alinhado)", "Neighbor-Joining (Árvore Evolutiva Biológica)"]
    algoritmo_selecionado = st.radio("Algoritmo de Agrupamento:", opcoes_algoritmo, horizontal=True)
    
    # Gerar a árvore com UPGMA ou NJ
    constructor = DistanceTreeConstructor()
    if algoritmo_selecionado == "Neighbor-Joining (Árvore Evolutiva Biológica)":
        tree = constructor.nj(dm)
    else:
        tree = constructor.upgma(dm)
    
    # Calcular a profundidade filogenética
    depths = tree.depths()
    terminals = tree.get_terminals()
    max_d = max(depths.values()) if depths else 1
    
    # Calcular profundidade topológica (para organizar a árvore perfeitamente sem nós "quebrados")
    topo_depths = {clade: len(tree.get_path(clade)) for clade in tree.find_clades()}
    max_topo = max(topo_depths.values()) if topo_depths else 1
    
    cargo_scores = {}
    leaf_y_pos = {}
    
    # Ordenar terminais pela travessia nativa da árvore biológica (impede cruzamento de galhos)
    terminals_sorted = tree.get_terminals()
    
    for i, leaf in enumerate(terminals_sorted):
        cargo = leaf.name
        # O Score de basalidade agora é obtido pela menor quantidade de divisões (nós) desde a raiz
        cargo_scores[cargo] = ((max_topo - topo_depths[leaf]) / max(1, max_topo)) * 10.0
        leaf_y_pos[leaf] = float(i) / max(1, len(terminals_sorted) - 1)
        
    sorted_cargos = sorted(cargo_scores.keys(), key=lambda x: cargo_scores[x], reverse=True)
    
    # Construir Grafo Direcionado nativo para o Plotly a partir do Biopython
    G = nx.DiGraph()
    root_name = i18n.t("m5_common_ancestor", default="Policial Civil")
    
    def calc_pos(clade):
        if clade in leaf_y_pos:
            y = leaf_y_pos[clade]
        else:
            children_y = [calc_pos(c) for c in clade.clades]
            y = sum(children_y) / len(children_y) if children_y else 0
            
        # Usa a profundidade topológica para X
        # O raiz do UPGMA ficará em x=0. As folhas ficarão em x=1.
        x_depth = topo_depths[clade] / max_topo
        
        name = clade.name if clade.name else f"b_{id(clade)}"
        
        # X passa a ser a distância cumulativa (depth topológico ou real) e Y o espalhamento (leaf_y_pos)
        # Invertemos para cladograma horizontal (Raiz na esquerda, folhas na direita)
        G.add_node(name, pos=(x_depth, y), is_terminal=clade.is_terminal(), original_name=clade.name, score=cargo_scores.get(clade.name, 0) if clade.is_terminal() else 0)
        
        for child in clade.clades:
            child_name = child.name if child.name else f"b_{id(child)}"
            # O tamanho do galho para repulsão/desenho (no NJ é real, no UPGMA é flat)
            branch_len = child.branch_length if child.branch_length is not None else 1.0
            G.add_edge(name, child_name, length=branch_len)
            
        return y
        
    # Criar raiz basal a partir da própria árvore gerada (sem nós artificiais injetados)
    calc_pos(tree.root)
    
    # Ordenar os cargos explicitamente por basalidade (opcional para listagem mobile)
    sorted_cargos = sorted(cargo_scores.keys(), key=lambda x: cargo_scores[x], reverse=True)
    
    # Distanciamento Y inteligente: Repulsão para evitar sobreposição de nós próximos
    # Pegamos todas as posições atuais
    nodes = list(G.nodes())
    y_vals = [G.nodes[n]['pos'][1] for n in nodes]
    # Nós precisamos separar quem está muito perto.
    min_dist = 0.05
    for _ in range(10): # 10 iterações de relaxamento
        for i in range(len(nodes)):
            for j in range(i+1, len(nodes)):
                n1, n2 = nodes[i], nodes[j]
                x1, y1 = G.nodes[n1]['pos']
                x2, y2 = G.nodes[n2]['pos']
                # Se eles estão no mesmo X (ou próximos) e Y muito perto, empurrar Y
                if abs(x1 - x2) < 0.2 and abs(y1 - y2) < min_dist:
                    push = (min_dist - abs(y1 - y2)) / 2.0
                    if y1 > y2:
                        G.nodes[n1]['pos'] = (x1, y1 + push)
                        G.nodes[n2]['pos'] = (x2, y2 - push)
                    else:
                        G.nodes[n1]['pos'] = (x1, y1 - push)
                        G.nodes[n2]['pos'] = (x2, y2 + push)

    # Identificar se há textos muito longos para esticar a tela
    max_label_len = max([len(n) for n in sorted_cargos]) if sorted_cargos else 20
    
    fig = _plot_vertical_cladogram(G, root_name, sorted_cargos, cargo_scores, df_bin, freq_atrib, mostrar_atribuicoes, separar_evolucao, estilo_cladograma, max_topo, max_label_len)
        
    st.plotly_chart(fig, use_container_width=True)
    
    if is_mobile:
        st.markdown("### " + i18n.t("m5_basal_table_title", default="Tabela de Basalidade"))
        import pandas as pd
        df_basal = pd.DataFrame([
            {i18n.t("m5_basal_rank", default="Rank"): i + 1, "Carreira": i18n.traduzir_cargo(cargo), i18n.t("m5_basal_score", default="Score Basal"): round(cargo_scores[cargo], 2)}
            for i, cargo in enumerate(sorted_cargos)
        ])
        st.dataframe(df_basal, use_container_width=True, hide_index=True)
    else:
        with st.expander("📊 " + i18n.t("m5_basal_table_title", default="Tabela de Basalidade")):
            import pandas as pd
            df_basal = pd.DataFrame([
                {i18n.t("m5_basal_rank", default="Rank"): i + 1, "Carreira": i18n.traduzir_cargo(cargo), i18n.t("m5_basal_score", default="Score Basal"): round(cargo_scores[cargo], 2)}
                for i, cargo in enumerate(sorted_cargos)
            ])
            st.dataframe(df_basal, use_container_width=True, hide_index=True)
    
    # Em mobile, o hover é ruim. Exibimos na tela via lista.
    if is_mobile and mostrar_atribuicoes:
        st.markdown(f"#### {i18n.t('m5_attr_list', default='Atribuições:')}")
        
        root_name = i18n.t("m5_common_ancestor", default="Policial Civil")
        comuns = df_bin.columns[df_bin.sum(axis=0) == len(df_bin)].tolist()
        if len(comuns) > 0:
            with st.expander(f"🧬 {root_name}"):
                st.markdown("**Atribuições Comuns a todos os cargos:**" if separar_evolucao else f"**{i18n.t('m5_attr_list')}**")
                for a in comuns:
                    st.markdown(f"- {i18n.traduzir_atribuicao(a)}")
                    
        # Rastrear o que já foi herdado para exibir no mobile também
        branch_attrs = {}
        if separar_evolucao:
            for i in range(len(sorted_cargos)):
                cargos_sub = sorted_cargos[i:]
                if len(cargos_sub) > 0:
                    sub_df = df_bin.loc[cargos_sub]
                    b_attr = set(sub_df.columns[sub_df.sum(axis=0) == len(cargos_sub)])
                else:
                    b_attr = set()
                branch_attrs[f"b_{i}"] = b_attr
                
                # Renderizar Divisão se houver novas atribuições
                idx = i
                total_here = branch_attrs[f"b_{i}"]
                total_parent = set(comuns) if idx == 0 else branch_attrs[f"b_{idx-1}"]
                new_attrs = total_here - total_parent
                if len(new_attrs) > 0:
                    title_div = f"{i18n.t('m5_branch_node', default='Divisão Evolutiva')} {idx+1}"
                    with st.expander(f"🌿 {title_div}"):
                        st.markdown(f"### {title_div}")
                        st.markdown(f"**{i18n.t('m5_attr_syn_long', default='Sinapomorfias (Novas atribuições na divisão):')}**")
                        for a in new_attrs:
                            st.markdown(f"- {i18n.traduzir_atribuicao(a)}")

        for i, cargo in enumerate(sorted_cargos):
            if separar_evolucao:
                total_inherited = branch_attrs.get(f"b_{i}", set())
                all_cargo_attrs = set(df_bin.columns[df_bin.loc[cargo] > 0])
                atribs = list(all_cargo_attrs - total_inherited)
            else:
                atribs = df_bin.columns[df_bin.loc[cargo] > 0]
                
            if len(atribs) > 0:
                cargo_trad = i18n.traduzir_cargo(cargo)
                with st.expander(f"💼 {cargo_trad}"):
                    st.markdown(f"### {cargo_trad}")
                    st.markdown(f"**{i18n.t('m5_attr_aut_long', default='Autapomorfias (Exclusivas):')}**" if separar_evolucao else f"**{i18n.t('m5_attr_list')}**")
                    for a in atribs:
                        st.markdown(f"- {i18n.traduzir_atribuicao(a)}")
    
    if st.session_state.get('show_explanations', False):
        import explanations
        tone_key = st.session_state.get('explanation_tone', 'tecnico')
        st.info(explanations.get_explanation("taxonomic_tree", tone_key, language=st.session_state.get('language', 'PT-BR')))
        
    if 'interaction_ui' in globals(): interaction_ui.render_like_button("5.1 Arvore Taxonomica", "5_1")

def _plot_vertical_cladogram(G, root_name, sorted_cargos, cargo_scores, df_bin, freq_atrib, mostrar_atribuicoes, separar_evolucao, estilo_cladograma, max_topo, max_label_len=20):
    import networkx as nx
    import plotly.graph_objects as go
    import plotly.express as px
    import plotly.colors as pcolors
    import numpy as np
    
    is_elegant = estilo_cladograma == "🌿 Tradicional (Científico)"
    is_circular = estilo_cladograma == i18n.t("m5_clade_circular", default="🌀 Circular (Radial)")
    
    pos = nx.get_node_attributes(G, 'pos')
    max_score = max(cargo_scores.values()) if cargo_scores and max(cargo_scores.values()) > 0 else 10
    
    def get_leaves(graph, n):
        leaves = []
        for desc in nx.descendants(graph, n) | {n}:
            if graph.nodes[desc].get('is_terminal'):
                leaves.append(graph.nodes[desc].get('original_name', desc))
        return leaves
        
    def get_shared_traits(leaves):
        if not leaves: return set()
        shared = set(df_bin.columns)
        for leaf in leaves:
            if leaf in df_bin.index:
                shared &= set(df_bin.columns[df_bin.loc[leaf] > 0])
        return shared
    
    if is_circular:
        new_pos = {}
        # Mapeia as folhas no círculo
        terminals = [n for n, attr in G.nodes(data=True) if attr.get('is_terminal', False)]
        n_cargos = len(terminals)
        angles = np.linspace(0, 2 * np.pi * (n_cargos - 1) / max(1, n_cargos), n_cargos)
        terminal_angles = {n: angles[i] for i, n in enumerate(terminals)}
        
        def get_angle(node):
            if node in terminal_angles:
                return terminal_angles[node]
            children = list(G.successors(node))
            if not children: return 0
            child_angles = [get_angle(c) for c in children]
            return np.mean(child_angles)
            
        for node in G.nodes():
            # r=0 deve ser a raiz, que está em x=0 na topologia.
            r = pos[node][0]
            theta = get_angle(node) + np.pi / 2
            new_pos[node] = (r * np.cos(theta), r * np.sin(theta))
            
        pos = new_pos

    fig = go.Figure()
    
    # Adicionar as arestas (galhos) com espessuras baseadas em sinapomorfias
    for edge in G.edges():
        u, v = edge
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        
        leaves_u = get_leaves(G, u)
        leaves_v = get_leaves(G, v)
        
        shared_u = get_shared_traits(leaves_u)
        shared_v = get_shared_traits(leaves_v)
        
        new_traits = len(shared_v - shared_u)
        
        # Espessura base é 1.5, aumenta 0.5 por cada nova atribuição inovada (máx 6)
        thickness = min(1.5 + (new_traits * 0.5), 6)
        edge_color = '#666' if new_traits == 0 else '#4d4d4d'
        
        if is_elegant and not is_circular:
            # Traçado ortogonal tipo dendrograma
            branch_x = [x0, x1, x1]
            branch_y = [y0, y0, y1]
        else:
            branch_x = [x0, x1]
            branch_y = [y0, y1]
            
        fig.add_trace(go.Scatter(x=branch_x, y=branch_y, line=dict(width=thickness, color=edge_color), mode='lines', hoverinfo='none', showlegend=False))
    
    # Dummy traces para criar a Legenda Lateral (Caixa explicativa)
    palette = px.colors.qualitative.Pastel
    fig.add_trace(go.Scatter(x=[None], y=[None], mode='markers', marker=dict(size=8, color=palette[4], line=dict(width=1.5, color='#333')), name=i18n.t("m5_leg_node", default="Divisão (Ramos mais grossos = Muitas Inovações)")))
    fig.add_trace(go.Scatter(x=[None], y=[None], mode='markers', marker=dict(size=14, color='rgba(215, 48, 39, 1)', line=dict(width=1.5, color='#333')), name=i18n.t("m5_leg_leaf1", default="Carreira Atual (Especializada/Derivada)")))
    fig.add_trace(go.Scatter(x=[None], y=[None], mode='markers', marker=dict(size=14, color='rgba(69, 117, 180, 1)', line=dict(width=1.5, color='#333')), name=i18n.t("m5_leg_leaf2", default="Carreira Atual (Generalista/Basal)")))
    
    node_x = []
    node_y = []
    text = []
    colors = []
    labels = []
    sizes = []
    
    comuns = set(df_bin.columns[df_bin.sum(axis=0) == len(df_bin)])
    
    for node, attr in G.nodes(data=True):
        is_term = attr.get('is_terminal', False)
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        
        if not is_term:
            # Todos os nós não-terminais (inclusive a raiz do clustering) são tratados como Divisão Evolutiva
            children = list(G.successors(node))
            hover_text = f"<b>{i18n.t('m5_branch_node', default='Divisão Evolutiva')}</b>"
            
            if len(children) == 2:
                leaves1 = get_leaves(G, children[0])
                leaves2 = get_leaves(G, children[1])
                
                shared1 = get_shared_traits(leaves1)
                shared2 = get_shared_traits(leaves2)
                
                syn1 = shared1 - shared2
                syn2 = shared2 - shared1
                
                def format_syns(syns, clade_leaves):
                    if not syns: return ""
                    syns_list = list(syns)
                    display = syns_list[:5]
                    res = "<br>".join([f"- {i18n.traduzir_atribuicao(a)}" for a in display])
                    if len(syns_list) > 5:
                        res += f"<br><i>(+{len(syns_list)-5} outras)</i>"
                        
                    rep_name = i18n.traduzir_cargo(clade_leaves[0])
                    if len(clade_leaves) > 1:
                        rep_name += f" e +{len(clade_leaves)-1}"
                        
                    return f"<br><br><b>Ramo '{rep_name}' inovou com:</b><br>{res}"
                    
                hover_text += format_syns(syn1, leaves1)
                hover_text += format_syns(syn2, leaves2)
                
            text.append(hover_text)
            colors.append(palette[4])
            labels.append("")
            sizes.append(8)
        else:
            cargo = attr.get('original_name', node)
            score = attr.get('score', 0)
            cargo_trad = i18n.traduzir_cargo(cargo)
            if separar_evolucao:
                atribs = list(set(df_bin.columns[df_bin.loc[cargo] > 0]) - comuns)
            else:
                atribs = df_bin.columns[df_bin.loc[cargo] > 0]
            hover_text = f"<b>{cargo_trad}</b><br>"
            if len(atribs) > 0:
                hover_text += f"<i>{i18n.t('m5_attr_aut_long', default='Autapomorfias:')}</i><br>"
                hover_text += "<br>".join([f"- {i18n.traduzir_atribuicao(a)}" for a in list(atribs)[:5]])
            text.append(hover_text)
            score = attr.get('score', 0)
            norm = score / 10.0
            colors.append(pcolors.sample_colorscale("RdYlBu", norm)[0])
            sizes.append(12 + ((1 - norm) * 6))
            labels.append(cargo_trad)
            
    fig.add_trace(go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        hoverinfo='text',
        hovertext=text,
        marker=dict(size=sizes, color=colors, line=dict(width=1.5, color='#333')),
        showlegend=False,
        cliponaxis=False
    ))
    
    # Usar annotations em vez de 'text' no Scatter para forçar a renderização bulletproof
    annotations = []
    if not is_circular:
        for x, y, label in zip(node_x, node_y, labels):
            if label:
                annotations.append(dict(
                    x=x, y=y,
                    text=f"<b>{label}</b>",
                    showarrow=False,
                    xanchor='left',
                    yanchor='middle',
                    xshift=12, # Afasta 12px do ponto
                    font=dict(size=12, color='white')
                ))
    else:
        for x, y, label in zip(node_x, node_y, labels):
            if label:
                # No circular, os labels apontam para fora a partir do centro
                angle = np.arctan2(y, x)
                annotations.append(dict(
                    x=x, y=y,
                    text=f"<b>{label}</b>",
                    showarrow=False,
                    xanchor='left' if np.cos(angle) >= 0 else 'right',
                    yanchor='middle',
                    xshift=12 * np.sign(np.cos(angle)),
                    font=dict(size=11, color='white')
                ))

    
    if not is_circular:
        # Calcular o limite máximo de X para NJ ou UPGMA
        max_x = max([pos[n][0] for n in G.nodes()]) if G.nodes() else 1.0
        
        fig.update_layout(
            xaxis=dict(range=[-0.1, max_x + 0.1], showgrid=False, zeroline=False, visible=False),
            yaxis=dict(range=[-0.1, 1.1], showgrid=False, zeroline=False, visible=False),
            margin=dict(l=40, r=min(500, max(200, max_label_len * 8)), t=60, b=40),
            legend=dict(
                title=dict(text="<b>Legenda</b>", font=dict(color="white")),
                font=dict(color="white"),
                orientation="v",
                yanchor="top", y=1,
                xanchor="left", x=1.05,
                bgcolor="rgba(0,0,0,0.5)",
                bordercolor="gray",
                borderwidth=1
            )
        )
        
    layout_update = dict(
        title="Cladograma Filogenético Especializado (Biopython UPGMA)",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        hovermode='closest',
        margin=dict(l=40, r=40, t=60, b=40),
        height=max(700, max_topo * 65),
        annotations=annotations
    )
    
    if is_circular:
        layout_update['xaxis'] = dict(showgrid=False, zeroline=False, showticklabels=False)
        layout_update['yaxis'] = dict(showgrid=False, zeroline=False, showticklabels=False, scaleanchor='x', scaleratio=1)
        layout_update['height'] = max(800, max_topo * 70)
        layout_update['legend'] = dict(
            title=dict(text="<b>Legenda</b>", font=dict(color="white")),
            font=dict(color="white"),
            orientation="v",
            yanchor="top", y=1,
            xanchor="left", x=1.05,
            bgcolor="rgba(0,0,0,0.5)",
            bordercolor="gray",
            borderwidth=1
        )
        
    fig.update_layout(**layout_update)
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
    st.session_state.akinator_multi_sel = []
    
    if st.session_state.get("mascote_sel_key") == "mascot_aleatorio" or "mascote_sel_key" not in st.session_state:
        import random
        choices = ["🐶 Inspetor Cão", "🦫 Investigadora Capi", "🦉 Oráculo (Coruja)", "🐺 Lobo-Guará Secreto"]
        weights = [30, 30, 30, 10]
        st.session_state.akinator_internal_mascot = random.choices(choices, weights=weights)[0]

def render_akinator_game(df_cenario):
    col_img, col_ui = st.columns([1, 4])
    
    with col_ui:
        st.markdown("<div id='toc-creative-mode'></div>", unsafe_allow_html=True)
        st.markdown("## " + i18n.t("m5_intro_title", default="🎨 5. Creative / Interactive Mode"))
        st.markdown(i18n.t("m5_intro_desc", default="Bem-vindo ao laboratório criativo! Aqui exploramos os dados de formas menos convencionais e mais divertidas."))
        
        st.markdown("<div id='toc-akinator'></div>", unsafe_allow_html=True)
        col_sub, col_tut = st.columns([85, 15], vertical_alignment="center")
        with col_sub:
            st.subheader(i18n.t("akinator_title", default="🔮 O Oráculo da PCSP (Adivinhador de Cargos)"), help=i18n.t("akinator_desc"))
        with col_tut:
            with st.popover(i18n.t("tutorial_popover", default="Tutorial")):
                st.info(i18n.t("akinator_desc", default="Pense em um cargo da Polícia Civil. Eu vou tentar adivinhar qual é através das atribuições dele!"))
        st.markdown(i18n.t("akinator_desc", default="Pense em um cargo da Polícia Civil. Eu vou tentar adivinhar qual é através das atribuições dele!"))
        
        st.markdown("""
<style>
    [data-testid="stImage"] img {
        max-height: 25vh !important;
        object-fit: contain !important;
        margin: 0 auto !important;
        display: block !important;
    }
}
/* Mascot CSS moved to JS injection */
</style>
        """, unsafe_allow_html=True)
        
        if 'akinator_state' not in st.session_state:
            st.session_state.mascote_sel_key = "mascot_aleatorio"
            reset_game()
            
        with st.expander(i18n.t("akinator_config_title", default="⚙️ Configurações (Como jogar e Dificuldade)"), expanded=False):
            col_config1, col_config2 = st.columns(2)
            with col_config1:
                tipo_jogo = st.radio(i18n.t("akinator_how_to_play", default="Como quer jogar?"), [i18n.t("akinator_mode_q", default="Perguntas (Modo Divertido)"), i18n.t("akinator_mode_m", default="Seleção Rápida (Multiselect)")], horizontal=True, on_change=reset_game)
                dificuldade = st.radio(
                    i18n.t("akinator_difficulty", default="Dificuldade (Nível de Detalhe):"), 
                    ["akinator_diff_easy", "akinator_diff_hard"], 
                    format_func=lambda x: i18n.t(x, default="🟢 Fácil (Atribuições Aglutinadas)" if "easy" in x else "🔴 Difícil (Matriz Completa/Granular)"),
                    horizontal=True, 
                    on_change=reset_game
                )
            with col_config2:
                visible_mascots = ["🐶 Inspetor Cão", "🦫 Investigadora Capi", "🦉 Oráculo (Coruja)"]
                radio_options = ["mascot_aleatorio"] + visible_mascots
                
                def format_mascot_option(x):
                    if x == "mascot_aleatorio":
                        return i18n.t_lang("mascot_aleatorio", st.session_state.get('language', 'PT-BR'))
                    key_map = {
                        "🐶 Inspetor Cão": "mascot_cao",
                        "🦫 Investigadora Capi": "mascot_capivara",
                        "🦉 Oráculo (Coruja)": "mascot_coruja"
                    }
                    return i18n.t_lang(key_map.get(x, x), st.session_state.get('language', 'PT-BR'))
                    
                mascote_sel = st.radio(
                    i18n.t("akinator_choose_mascot", default="Escolha seu Mascote:"), 
                    radio_options, 
                    format_func=format_mascot_option, 
                    horizontal=True, 
                    key="mascote_sel_key"
                )
                
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

    if mascote_sel == "mascot_aleatorio":
        mascote_real = st.session_state.get("akinator_internal_mascot", "🐶 Inspetor Cão")
    else:
        mascote_real = mascote_sel
    
    if dificuldade == "akinator_diff_easy":
        try:
            df_clean = data_processing.condensar_atribuicoes(df_cenario, similarity_threshold=0.7)
        except Exception:
            df_clean = df_cenario.copy()
    else:
        df_clean = df_cenario.copy()
        
    if 'Carreira' in df_clean.columns:
        df_clean = df_clean.set_index('Carreira')
    df_bin = (df_clean > 0).astype(int)
    
    if st.session_state.akinator_remaining is None:
        st.session_state.akinator_remaining = df_bin.copy()
    
    if tipo_jogo == i18n.t("akinator_mode_m", default="Seleção Rápida (Multiselect)"):
        todas_atrib = df_bin.columns.tolist()
        
        # Função para limpar sujeira do Streamlit multiselect (quando ele retorna a label formatada antiga)
        def get_original_attr(val):
            if val in todas_atrib:
                return val
            for attr in todas_atrib:
                trad = i18n.traduzir_atribuicao(attr)
                if trad in val:
                    return attr
            return val
            
        if "akinator_multi_sel" not in st.session_state:
            st.session_state.akinator_multi_sel = []
            
        # Limpa o state caso o Streamlit tenha salvo a label formatada com emojis
        selecionadas_atuais = [get_original_attr(s) for s in st.session_state.akinator_multi_sel]
        st.session_state.akinator_multi_sel = selecionadas_atuais
        
        cargos_restantes = df_bin.index.tolist()
        if selecionadas_atuais:
            df_match = df_bin.copy()
            for s in selecionadas_atuais:
                df_match = df_match[df_match[s] == 1]
            cargos_restantes = df_match.index.tolist()
            
        def format_attr_colored(attr):
            trad = i18n.traduzir_atribuicao(attr)
            if attr in selecionadas_atuais:
                return f"✅ {trad}"
                
            if len(cargos_restantes) == 0:
                return f"🔴 {trad} (Incompatível)"
                
            cargos_with_attr = [c for c in cargos_restantes if df_bin.loc[c, attr] == 1]
            n = len(cargos_with_attr)
            
            if n == 0:
                return f"🔴 {trad} (Incompatível)"
            elif n == 1:
                return f"🟢 {trad} (Define: {i18n.traduzir_cargo(cargos_with_attr[0]).split(' ')[0]})"
            else:
                return f"🟡 {trad} (Grupo: {n} cargos)"
                
        # Define a imagem dinâmica do mascote baseada no resultado atual
        mascot_file_key = "file"
        if selecionadas_atuais:
            if len(cargos_restantes) == 0:
                mascot_file_key = "file_confused"
            elif len(cargos_restantes) == 1:
                mascot_file_key = "file_won"
            elif len(cargos_restantes) <= 3:
                mascot_file_key = "file_near"
                
        mascot_img_path_dynamic = os.path.join(ASSETS_DIR, MASCOTS[mascote_real].get(mascot_file_key, MASCOTS[mascote_real]["file"]))
        
        with col_img:
            if os.path.exists(mascot_img_path_dynamic):
                import base64
                with open(mascot_img_path_dynamic, "rb") as image_file:
                    encoded_string = base64.b64encode(image_file.read()).decode()
                import streamlit.components.v1 as components
                st.markdown("<style>#mascot-floating-fixed { display: block !important; }</style>", unsafe_allow_html=True)
                components.html(f"""
                <script>
                    const parentWin = window.parent;
                    const doc = parentWin.document;
                    
                    let floating = doc.getElementById('mascot-floating-fixed');
                    if (!floating) {{
                        floating = doc.createElement('div');
                        floating.id = 'mascot-floating-fixed';
                        floating.style.position = 'fixed';
                        floating.style.bottom = '80px';
                        floating.style.left = 'max(1.5rem, 2vw)';
                        floating.style.width = '16vw';
                        floating.style.minWidth = '150px';
                        floating.style.maxWidth = '250px';
                        floating.style.zIndex = '50';
                        floating.style.pointerEvents = 'none';
                        doc.body.appendChild(floating);
                    }}
                    floating.innerHTML = '<img src="data:image/png;base64,{encoded_string}" style="width: 100%; border-radius: 8px;">';
                </script>
                """, height=0)

                
        with col_ui:
            # Renderiza o select
            selecionadas = st.multiselect(
                i18n.t("akinator_select_attr", default="Selecione as atribuições que seu cargo faz:"), 
                todas_atrib, 
                format_func=format_attr_colored,
                key="akinator_multi_sel"
            )
            
            if selecionadas:
                if len(cargos_restantes) == 0:
                    st.error(i18n.t("akinator_no_match", default="Nenhum cargo faz essa combinação exata!"))
                    if st.button(i18n.t("akinator_play_again", default="Jogar Novamente"), key="play_again_multi_loss"):
                        reset_game()
                        st.rerun()
                elif len(cargos_restantes) == 1:
                    st.success(i18n.t("akinator_is", default="🎉 É o **{cargo}**!").format(cargo=i18n.traduzir_cargo(cargos_restantes[0])))
                    if st.button(i18n.t("akinator_play_again", default="Jogar Novamente"), key="play_again_multi_win"):
                        reset_game()
                        st.rerun()
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
        emojis_mascote = MASCOTS[mascote_real]["emojis"]
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
            
        mascot_img_path_dynamic = os.path.join(ASSETS_DIR, MASCOTS[mascote_real][mascot_file_key])
            
        with col_img:
            if os.path.exists(mascot_img_path_dynamic):
                import base64
                with open(mascot_img_path_dynamic, "rb") as image_file:
                    encoded_string = base64.b64encode(image_file.read()).decode()
                import streamlit.components.v1 as components
                st.markdown("<style>#mascot-floating-fixed { display: block !important; }</style>", unsafe_allow_html=True)
                components.html(f"""
                <script>
                    const parentWin = window.parent;
                    const doc = parentWin.document;
                    
                    let floating = doc.getElementById('mascot-floating-fixed');
                    if (!floating) {{
                        floating = doc.createElement('div');
                        floating.id = 'mascot-floating-fixed';
                        floating.style.position = 'fixed';
                        floating.style.bottom = '80px';
                        floating.style.left = 'max(1.5rem, 2vw)';
                        floating.style.width = '16vw';
                        floating.style.minWidth = '150px';
                        floating.style.maxWidth = '250px';
                        floating.style.zIndex = '50';
                        floating.style.pointerEvents = 'none';
                        doc.body.appendChild(floating);
                    }}
                    floating.innerHTML = '<img src="data:image/png;base64,{encoded_string}" style="width: 100%; border-radius: 8px;">';
                </script>
                """, height=0)
                

                
        with col_ui:
            if mascote_real == "🐺 Lobo-Guará Secreto":
                nome_personagem = i18n.t_lang("mascot_lobo", st.session_state.get('language', 'PT-BR'))
            else:
                key_map = {
                    "🐶 Inspetor Cão": "mascot_cao",
                    "🦫 Investigadora Capi": "mascot_capivara",
                    "🦉 Oráculo (Coruja)": "mascot_coruja"
                }
                mascote_sel_trad = i18n.t_lang(key_map.get(mascote_real, mascote_real), st.session_state.get('language', 'PT-BR'))
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
                    # Question UI
                    st.markdown(f"#### " + i18n.t("akinator_your_role", default="Seu cargo possui a atribuição **'{attr}'**?").format(attr=i18n.traduzir_atribuicao(best_q)))
                    
                    with st.expander("💡 " + i18n.t("akinator_hint", default="Ver Dica do Oráculo (Quem faz isso?)")):
                        faz = [c for c in df_rem.index if df_rem.loc[c, best_q] == 1]
                        nao_faz = [c for c in df_rem.index if df_rem.loc[c, best_q] == 0]
                        st.markdown(f"**🟢 Realizam:** {', '.join([i18n.traduzir_cargo(c) for c in faz])}")
                        st.markdown(f"**🔴 NÃO Realizam:** {', '.join([i18n.traduzir_cargo(c) for c in nao_faz])}")
                    
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
