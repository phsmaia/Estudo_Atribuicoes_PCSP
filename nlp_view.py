import streamlit as st
import pandas as pd
import numpy as np
import re
import os
import json
import i18n
import explanations
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt

try:
    from wordcloud import WordCloud
    HAS_WORDCLOUD = True
except ImportError:
    HAS_WORDCLOUD = False

try:
    import networkx as nx
    HAS_NETWORKX = True
except ImportError:
    HAS_NETWORKX = False

try:
    import interaction_ui
except ImportError:
    interaction_ui = None

@st.cache_data
def load_nlp_data():
    """Carrega os dados processados pelo nlp_processor.py"""
    sim_tfidf = None
    sim_spacy = None
    word_weights = None
    topic_models = None
    
    try:
        if os.path.exists("nlp_sim_matrix_tfidf.csv"):
            sim_tfidf = pd.read_csv("nlp_sim_matrix_tfidf.csv", index_col=0)
        
        if os.path.exists("nlp_sim_matrix_spacy.csv"):
            sim_spacy = pd.read_csv("nlp_sim_matrix_spacy.csv", index_col=0)
            
        if os.path.exists("nlp_tfidf_word_clouds.json"):
            with open("nlp_tfidf_word_clouds.json", 'r', encoding='utf-8') as f:
                word_weights = json.load(f)
                
        if os.path.exists("nlp_topics.json"):
            with open("nlp_topics.json", 'r', encoding='utf-8') as f:
                topic_models = json.load(f)
                
    except Exception as e:
        st.error(f"Erro ao carregar dados de PLN: {e}")
        
    return sim_tfidf, sim_spacy, word_weights, topic_models

def parse_raw_texts(filepath):
    """
    Lê o arquivo Markdown e extrai os textos brutos das atribuições.
    Retorna um DataFrame com Documento, Cargo, Ano e Texto Bruto Completo.
    """
    data = []
    if not os.path.exists(filepath):
        return pd.DataFrame()
        
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    pattern = re.compile(r'-\s*(.+?)\s*=\s*"(.*?)"', re.DOTALL)
    matches = pattern.findall(content)
    
    for match in matches:
        raw_name = match[0].strip()
        text = match[1].strip().replace('\n', ' ')
        raw_name_clean = raw_name.replace('_', ' ')
        
        documento = "Desconhecido"
        cargo = "Desconhecido"
        ano = "Desconhecido"
        
        year_match = re.search(r'(\d{4}(?:/\d{4})?)$', raw_name_clean)
        if year_match:
            ano = year_match.group(1)
            raw_name_clean = raw_name_clean[:year_match.start()].strip()
            
        doc_match = re.match(r'^(Edital|Decreto|Portaria(?:\s+DGP)?|Consolidação)(.*)', raw_name_clean, re.IGNORECASE)
        if doc_match:
            documento = doc_match.group(1).strip()
            cargo_raw = doc_match.group(2).strip()
            if cargo_raw.startswith("de "):
                cargo_raw = cargo_raw[3:]
            if cargo_raw.startswith("-"):
                cargo_raw = cargo_raw[1:].strip()
            cargo = cargo_raw if cargo_raw else documento
        else:
            cargo = raw_name_clean
            
        if "Portaria" in documento:
            cargo = "Atribuições Comuns"
            
        data.append({
            "Documento": documento,
            "Cargo": cargo,
            "Ano": ano,
            "Texto Bruto Completo": text
        })
        
    return pd.DataFrame(data)

def render_nlp_view(current_section=None):
    st.markdown(f"<h2 style='text-align: center; color: var(--primary-color);'>{i18n.t('mode_8')}</h2>", unsafe_allow_html=True)
    st.divider()

    # Tenta carregar dados pré-processados para as seções 8.2+
    sim_tfidf, sim_spacy, word_weights, topic_models = load_nlp_data()
    tem_dados = sim_tfidf is not None and sim_spacy is not None and word_weights is not None
    
    if tem_dados:
        with st.expander("🔬 Criar Cargo Virtual (Fusão de Documentos)", expanded=False):
            st.markdown("Selecione de 2 a 4 documentos para criar um 'Cargo Virtual'. Ele aparecerá nas visualizações abaixo como uma combinação matemática (média) dos cargos originais.")
            todos_docs = list(sim_tfidf.columns)
            
            col_fusao1, col_fusao2 = st.columns([3, 1])
            with col_fusao1:
                selecionados_fusao = st.multiselect("Selecione os cargos para fundir:", options=todos_docs, max_selections=4)
            with col_fusao2:
                nome_fusao = st.text_input("Nome Curto para a Fusão:", value="Fusão Personalizada")
                
            if len(selecionados_fusao) >= 2:
                if st.button("Aplicar Fusão"):
                    if 'cargos_virtuais' not in st.session_state:
                        st.session_state['cargos_virtuais'] = {}
                        
                    if len(st.session_state['cargos_virtuais']) >= 5:
                        st.error("Limite máximo de 5 cargos virtuais atingido. Remova um antes de criar outro.")
                    else:
                        st.session_state['cargos_virtuais'][nome_fusao] = {
                            'nome': nome_fusao,
                            'cargos': selecionados_fusao
                        }
                        st.rerun()
                
            if 'cargos_virtuais' in st.session_state and st.session_state['cargos_virtuais']:
                for cv_name, cv in list(st.session_state['cargos_virtuais'].items()):
                    col_cv1, col_cv2 = st.columns([4, 1])
                    with col_cv1:
                        st.success(f"🟢 Cargo Virtual Ativo: **{cv['nome']}** ({len(cv['cargos'])} origens).")
                    with col_cv2:
                        if st.button("Remover", key=f"del_cv_{cv_name}"):
                            del st.session_state['cargos_virtuais'][cv_name]
                            st.rerun()
                    
        # Injetar cargo virtual nas matrizes dinamicamente
        if 'cargos_virtuais' in st.session_state and st.session_state['cargos_virtuais']:
            # Cópia explícita para não alterar o cache do Streamlit acidentalmente
            sim_tfidf = sim_tfidf.copy()
            sim_spacy = sim_spacy.copy()
            word_weights = word_weights.copy()
            if topic_models:
                import copy
                topic_models = copy.deepcopy(topic_models)
                
            for cv_name, cv in st.session_state['cargos_virtuais'].items():
                nome = cv['nome']
                pais = cv['cargos']
                
                # Média das similaridades
                for df_sim in [sim_tfidf, sim_spacy]:
                    if df_sim is not None:
                        pais_existentes = [p for p in pais if p in df_sim.index]
                        if pais_existentes:
                            nova_coluna = df_sim.loc[pais_existentes].mean(axis=0)
                            df_sim[nome] = nova_coluna
                            df_sim.loc[nome] = nova_coluna
                            df_sim.loc[nome, nome] = 1.0
                            
                # Média dos Word Weights (TF-IDF)
                virtual_words = {}
                valid_parents_words = 0
                for p in pais:
                    if p in word_weights:
                        valid_parents_words += 1
                        for w, weight in word_weights[p].items():
                            virtual_words[w] = virtual_words.get(w, 0) + weight
                if valid_parents_words > 0:
                    virtual_words = {k: v / valid_parents_words for k, v in virtual_words.items()}
                    word_weights[nome] = dict(sorted(virtual_words.items(), key=lambda item: item[1], reverse=True)[:50])
                
                # Média dos Tópicos (NMF)
                if topic_models:
                    for k, k_data in topic_models.items():
                        topic_sum = {}
                        valid_parents_topics = 0
                        for p in pais:
                            if p in k_data["document_topics"]:
                                valid_parents_topics += 1
                                for t, v in k_data["document_topics"][p].items():
                                    topic_sum[t] = topic_sum.get(t, 0) + v
                        if valid_parents_topics > 0:
                            topic_sum = {t_k: t_v / valid_parents_topics for t_k, t_v in topic_sum.items()}
                            k_data["document_topics"][nome] = topic_sum
                            
        with st.expander("🔄 Consulta Histórica (Tabela de Conversão de Cargos)", expanded=False):
            try:
                df_conv = pd.read_csv("Tabela_Conversao_Cargos.CSV", sep=";", encoding="latin1")
                col_atual = [c for c in df_conv.columns if "Atual Sem" in c]
                col_decreto = [c for c in df_conv.columns if "47788" in c]
                if col_atual and col_decreto:
                    df_display = df_conv[[col_atual[0], col_decreto[0]]].dropna().drop_duplicates()
                    df_display = df_display.rename(columns={
                        col_atual[0]: "Atual (2023)",
                        col_decreto[0]: "Decreto 47.788 (1967)"
                    })
                    st.dataframe(df_display, hide_index=True, use_container_width=True)
            except Exception as e:
                st.error(f"Erro ao carregar a tabela: {e}")

    # Seção 8.1: Textos Normativos Brutos
    if current_section == 'sub_nlp_raw_title' or current_section is None:
        st.subheader(i18n.t("sub_nlp_raw_title", default="8.1. Textos Normativos Brutos"))
        
        if st.session_state.get('show_explanations', False):
            st.info(i18n.t("tut_sec_nlp", default="O módulo de PLN utiliza modelos vetoriais para analisar a semântica dos textos das atribuições, permitindo buscas inteligentes e comparações baseadas no significado, não apenas em palavras-chave exatas."))
            
        df_raw = parse_raw_texts("Texto_Atribuicoes_Bruto.md")
        
        if not df_raw.empty:
            st.markdown("Navegue pela tabela abaixo para visualizar os textos brutos originais que alimentarão o pipeline de Processamento de Linguagem Natural (PLN).")
            
            with st.expander("🔍 Filtros de Pesquisa / Search Filters", expanded=True):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    cargos_unicos = sorted([str(x) for x in df_raw['Cargo'].dropna().unique()])
                    selected_cargos = st.multiselect("Filtrar por Cargo", options=cargos_unicos, default=[])
                
                with col2:
                    docs_unicos = sorted([str(x) for x in df_raw['Documento'].dropna().unique()])
                    selected_docs = st.multiselect("Filtrar por Documento", options=docs_unicos, default=[])
                    
                with col3:
                    anos_unicos = sorted([str(x) for x in df_raw['Ano'].dropna().unique()])
                    selected_anos = st.multiselect("Filtrar por Ano", options=anos_unicos, default=[])

                search_term = st.text_input("Pesquisa livre no Texto Bruto (Ex: armas, investigação):", key="search_nlp_raw")

            # Aplica filtros
            df_display = df_raw.copy()
            if selected_cargos:
                df_display = df_display[df_display['Cargo'].isin(selected_cargos)]
            if selected_docs:
                df_display = df_display[df_display['Documento'].isin(selected_docs)]
            if selected_anos:
                df_display = df_display[df_display['Ano'].isin(selected_anos)]
                
            if search_term:
                mask = df_display.apply(lambda row: row.astype(str).str.contains(search_term, case=False, na=False).any(), axis=1)
                df_display = df_display[mask]
                
            st.markdown(f"**Total de registros:** {len(df_display)}")
            
            st.dataframe(
                df_display, 
                use_container_width=True, 
                hide_index=True,
                column_config={
                    "Documento": st.column_config.TextColumn("Documento", width="small"),
                    "Cargo": st.column_config.TextColumn("Cargo", width="medium"),
                    "Ano": st.column_config.TextColumn("Ano", width="small"),
                    "Texto Bruto Completo": st.column_config.TextColumn("Texto Bruto Completo", width="large"),
                }
            )
        else:
            st.warning("Não foi possível carregar os textos brutos de Texto_Atribuicoes_Bruto.md")
            
        if interaction_ui and hasattr(interaction_ui, 'render_like_button'):
            interaction_ui.render_like_button("8.1 Textos Brutos", "8_1")

    # Seção 8.2: Processamento e Limpeza Inicial
    elif current_section == 'sub_nlp_proc_title':
        st.subheader(i18n.t("sub_nlp_proc_title", default="8.2. Processamento e Limpeza Inicial (PLN)"))
        
        metrics = None
        if os.path.exists("nlp_metrics.json"):
            try:
                with open("nlp_metrics.json", "r", encoding="utf-8") as f:
                    metrics = json.load(f)
            except:
                pass
                
        if tem_dados and metrics:
            st.success("Dados de Processamento de Linguagem Natural carregados com sucesso do armazenamento local!")
            
            # 1. Métricas de Redução de Ruído
            st.markdown("### 📉 Redução de Ruído e Extração de Vocabulário")
            st.markdown("O pipeline converte os textos brutos em entidades matemáticas, removendo pontuações, conectivos (stopwords) e reduzindo as palavras às suas raízes (Lemas).")
            
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Palavras Brutas Lidas", f"{metrics['total_raw']:,}".replace(",", "."))
            c2.metric("Ruído Removido (Stopwords)", f"- {metrics['total_removed']:,}".replace(",", "."), delta_color="normal")
            c3.metric("Lemas Únicos (Vocabulário)", f"{metrics['total_lemmas']:,}".replace(",", "."))
            if 'silhouette_score' in metrics:
                c4.metric("Coesão Semântica (Silhueta)", f"{metrics['silhouette_score']:.3f}", help="Varia de -1 a 1. Valores maiores que 0 indicam que os cargos formam grupos coerentes (clusters bem definidos).")
            
            st.markdown("---")
            
            # 2. O "Antes e Depois" Visual
            st.markdown("### 🔍 O \"Antes e Depois\" na Prática")
            st.markdown("Veja como a Inteligência Artificial (SpaCy) interpreta uma frase real do corpus. Escolha um documento abaixo para analisar o processamento das suas primeiras palavras:")
            
            if 'demo_steps_dict' in metrics:
                # Seletor de documento
                doc_keys = list(metrics['demo_steps_dict'].keys())
                selected_demo_doc = st.selectbox("Selecione um documento para visualizar o processamento:", doc_keys)
                
                demo_data = metrics['demo_steps_dict'][selected_demo_doc]
                st.info(f"**Texto Original (trecho inicial):** *{demo_data['demo_text']}*")
                
                demo_html = "<div style='padding: 10px; background-color: rgba(0,0,0,0.1); border-radius: 5px; margin-bottom: 20px;'>"
                for token in demo_data['demo_steps']:
                    word = token['word']
                    lemma = token['lemma']
                    if token['status'] == 'drop':
                        demo_html += f"<span style='color: #ff4b4b; text-decoration: line-through; margin-right: 8px;'>{word}</span>"
                    else:
                        demo_html += f"<span style='color: #00cc96; font-weight: bold; margin-right: 8px;' title='Lema: {lemma}'>{word} ({lemma})</span>"
                demo_html += "</div>"
                
                st.markdown(demo_html, unsafe_allow_html=True)
                st.markdown("*(Palavras em vermelho foram descartadas por não conterem peso analítico. Palavras em verde foram mantidas e lematizadas).*")
            
            st.markdown("---")
            
            # 3. Raio-X do Vocabulário Geral
            st.markdown("### 🌟 Raio-X Institucional (Top Global)")
            st.markdown("Antes de analisarmos cada cargo, estas são as palavras e expressões mais pesadas (TF-IDF) em **toda** a instituição somada:")
            
            if 'top_global_words' in metrics:
                col_slider, col_radio = st.columns([1, 2])
                with col_slider:
                    top_k = st.slider("Quantidade a mostrar:", min_value=5, max_value=100, value=20, step=5)
                with col_radio:
                    opcoes_tamanho_ngram = ["1 palavra", "2 palavras", "3 palavras", "4 palavras", "5 palavras"]
                    tamanhos_selecionados_ngram = st.multiselect(
                        "Filtrar por Tamanho (N-Grams):", 
                        options=opcoes_tamanho_ngram, 
                        default=opcoes_tamanho_ngram
                    )
                
                # Filtrar os itens baseado no tamanho do n-gram (número de espaços + 1)
                filtered_items = []
                for word, weight in metrics['top_global_words'].items():
                    word_len = word.count(' ') + 1
                    len_str = f"{word_len} palavra{'s' if word_len > 1 else ''}"
                    if len_str in tamanhos_selecionados_ngram:
                        filtered_items.append((word, weight))
                        
                # Ordenar e converter para DataFrame limitando ao top_k
                filtered_items = sorted(filtered_items, key=lambda x: x[1], reverse=True)
                df_global = pd.DataFrame(filtered_items[:top_k], columns=["Palavra/Expressão", "Peso Global"])
                
                fig_global = px.bar(df_global, x="Peso Global", y="Palavra/Expressão", orientation='h',
                                    color="Peso Global", color_continuous_scale="Teal",
                                    title=f"Top {top_k} Conceitos Matemáticos (TF-IDF)")
                                    
                fig_global.update_layout(
                    height=max(400, top_k * 20),
                    yaxis={'categoryorder':'total ascending', 'dtick': 1}
                )
                st.plotly_chart(fig_global, use_container_width=True)
            
            st.markdown("---")
            
            # 4. Extração Sintática (Noun Chunks com SpaCy)
            st.markdown("### 🧩 Análise Sintática (Expressões Nominais)")
            st.markdown("Diferente do cálculo estatístico cego acima, aqui a IA gramatical leu o texto, entendeu o que é um substantivo e separou os **'pacotes de significado'**. Veja as expressões mais cruciais que definem a PCSP:")
            if 'top_noun_chunks' in metrics:
                col_slider_chunks, col_multi_chunks = st.columns([1, 2])
                with col_slider_chunks:
                    top_k_chunks = st.slider("Quantidade de expressões a mostrar:", min_value=5, max_value=100, value=20, step=5, key="slider_chunks_8_2")
                with col_multi_chunks:
                    opcoes_tamanho_chunk = ["1 palavra", "2 palavras", "3 palavras", "4 palavras", "5 ou mais palavras"]
                    tamanhos_selecionados = st.multiselect("Filtrar por Tamanho da Expressão:", options=opcoes_tamanho_chunk, default=opcoes_tamanho_chunk)
                
                filtered_chunks = []
                for expr, freq in metrics['top_noun_chunks'].items():
                    word_len = expr.count(' ') + 1
                    len_str = f"{word_len} palavra{'s' if word_len > 1 else ''}"
                    if word_len >= 5:
                        len_str = "5 ou mais palavras"
                        
                    if len_str in tamanhos_selecionados:
                        filtered_chunks.append((expr, freq))
                        
                df_chunks = pd.DataFrame(filtered_chunks, columns=["Expressão (Noun Chunk)", "Frequência"])
                
                fig_chunks = px.bar(df_chunks.head(top_k_chunks).sort_values(by="Frequência", ascending=True), 
                                    x="Frequência", y="Expressão (Noun Chunk)", orientation='h',
                                    color="Frequência", color_continuous_scale="Purpor",
                                    title=f"Top {top_k_chunks} Expressões Compostas (Sintaxe SpaCy)")
                fig_chunks.update_layout(yaxis={'categoryorder':'total ascending', 'dtick': 1}, height=max(400, top_k_chunks * 20))
                st.plotly_chart(fig_chunks, use_container_width=True)
            
            st.markdown("---")
            
            # 5. Visão Global dos Tópicos Latentes
            st.markdown("### 🧩 Temas Ocultos na Instituição (Modelagem NMF)")
            st.markdown("Além de contar palavras isoladas, a IA vasculhou a correlação entre os termos em toda a base e agrupou os conceitos em 'temas' subjacentes (tópicos). Mude o valor de K (granularidade) para ver as palavras fundamentais de cada um desses temas globais:")
            if topic_models:
                num_t = st.slider("Quantidade de tópicos (K) a explorar:", min_value=2, max_value=10, value=6, step=1, key="slider_topics_82")
                
                k_key = str(num_t)
                if k_key in topic_models:
                    words_dict = topic_models[k_key]["topic_words"]
                    
                    cols = st.columns(3)
                    idx = 0
                    for i in range(1, num_t + 1):
                        t_key = f"Tópico {i}"
                        if t_key in words_dict:
                            top_w_dict = words_dict[t_key]
                            top_w = list(top_w_dict.keys())
                            nice_name = f"T{i} ({top_w[0].title()} / {top_w[1].title()})"
                            
                            with cols[idx % 3]:
                                st.info(f"**{nice_name}**\n\n{', '.join(top_w[:7])}")
                            idx += 1
            else:
                st.info("Arquivos de Tópicos (NMF) não encontrados. Execute o Processador NLP.")
                
            st.markdown("---")
            
            # 6. Painel Didático: TF-IDF vs Embeddings
            with st.expander("🧠 Entenda os Motores Analíticos: TF-IDF vs Embeddings (SpaCy)"):
                st.markdown("""
                Para as análises das próximas seções, utilizamos dois modelos matemáticos diferentes para comparar as atribuições dos cargos. Por que usar dois?
                
                | Recurso | TF-IDF (Matemático) | Embeddings SpaCy (IA Vetorial) |
                | :--- | :--- | :--- |
                | **Como funciona?** | Conta a frequência das palavras exatas. | Transforma a frase em um vetor matemático de 300 dimensões apontando para conceitos no espaço. |
                | **O que ele entende?** | Que `investigar` é importante se aparecer muito. | Que `investigar` e `apurar` significam quase a mesma coisa, mesmo sendo palavras diferentes. |
                | **Limitação** | Se um cargo usar a palavra "Viatura" e o outro usar "Veículo", ele dirá que os cargos não têm nada a ver. | É mais pesado de processar e às vezes encontra similaridades "filosóficas" demais. |
                | **Uso neste projeto** | Nuvem de Palavras e Grafo de Discursos. | Heatmaps e Distância Semântica profunda. |
                """)
                
        else:
            st.warning("Arquivos de métricas de PLN não encontrados. Execute o script 'nlp_processor.py' novamente para gerá-los.")
            
        if interaction_ui and hasattr(interaction_ui, 'render_like_button'):
            interaction_ui.render_like_button("8.2 Processamento PLN", "8_2")
        
    # Seção 8.3: Matrizes de Distância Semântica
    elif current_section == 'sub_nlp_heat_title':
        st.subheader(i18n.t("sub_nlp_heat_title", default="8.3. Matrizes de Distância Semântica"))
        if not tem_dados:
            st.warning("Arquivos de PLN não encontrados. Execute 'nlp_processor.py' primeiro.")
            return
            
        metodo = st.radio("Selecione o método de similaridade:", 
                          options=["Embeddings Semânticos (Contexto/SpaCy)", "TF-IDF (Palavras Exatas)"])
        
        df_plot = sim_spacy if "SpaCy" in metodo else sim_tfidf
        
        # Encurtar rótulos muitos longos (como "30, de 14 de novembro de 2012, conforme...")
        def shorten_label(label):
            return label[:32] + "..." if len(label) > 35 else label
            
        df_plot.columns = [shorten_label(c) for c in df_plot.columns]
        df_plot.index = [shorten_label(c) for c in df_plot.index]
        
        todos_cargos = list(df_plot.columns)
        
        col_filtro, col_destaque = st.columns(2)
        with col_filtro:
            selecionados = st.multiselect("Filtrar documentos para comparar:", options=todos_cargos, default=todos_cargos)
        
        with col_destaque:
            destaques = st.multiselect("🎨 Destaque Visual (Realçar Eixos):", options=selecionados, default=[])
        
        if selecionados:
            df_filtrado = df_plot.loc[selecionados, selecionados]
            import visualizations
            fig = visualizations.plot_adjacency_heatmap(
                df_filtrado, 
                title="Mapa de Calor de Similaridade (0 a 1)", 
                cargos_destaque=destaques,
                colorscale="Viridis" if "SpaCy" in metodo else "Plasma"
            )
            fig.update_layout(height=650)
            st.plotly_chart(fig, use_container_width=True)
            

        
        if interaction_ui and hasattr(interaction_ui, 'render_like_button'):
            interaction_ui.render_like_button("8.3 Matrizes PLN", "8_3")
        
    # Seção 8.4: Nuvens de Palavras (TF-IDF)
    elif current_section == 'sub_nlp_cloud_title':
        st.subheader(i18n.t("sub_nlp_cloud_title", default="8.4. Nuvens de Palavras (TF-IDF)"))
        if not tem_dados:
            st.warning("Arquivos de PLN não encontrados. Execute 'nlp_processor.py' primeiro.")
            return
            
        if not HAS_WORDCLOUD:
            st.warning("Para visualizar as nuvens de palavras, instale as bibliotecas executando no terminal:\npip install wordcloud matplotlib")
            return
            
        cargo = st.selectbox("Selecione o Documento/Cargo:", options=list(word_weights.keys()))
        
        if cargo:
            pesos = word_weights[cargo]
            if pesos:
                col_cmap, col_tema = st.columns(2)
                with col_cmap:
                    cmap = st.selectbox("Esquema de Cores:", options=['viridis', 'plasma', 'magma', 'inferno', 'cividis', 'Blues', 'Reds'])
                with col_tema:
                    tema_nuvem = st.selectbox("Fundo da Nuvem:", options=['Escuro (Dark)', 'Claro (Light)'])
                
                bg_color = '#0E1117' if tema_nuvem == 'Escuro (Dark)' else '#FFFFFF'
                
                # Gerar em altíssima resolução para evitar o borrado
                wc = WordCloud(
                    width=1600, 
                    height=800, 
                    background_color=bg_color, 
                    colormap=cmap
                ).generate_from_frequencies(pesos)
                
                # Converter imagem para Base64 para renderizar via HTML (permite CSS customizado)
                import io
                import base64
                
                img = wc.to_image()
                buffered = io.BytesIO()
                img.save(buffered, format="PNG")
                img_str = base64.b64encode(buffered.getvalue()).decode()
                
                st.markdown(f"### Termos mais relevantes: {cargo}")
                st.markdown(
                    f'''
                    <div style="display: flex; justify-content: center; padding: 10px;">
                        <img src="data:image/png;base64,{img_str}" style="width: 100%; max-width: 900px; border-radius: 24px; box-shadow: 0 10px 20px rgba(0,0,0,0.4);">
                    </div>
                    ''',
                    unsafe_allow_html=True
                )
                
                st.markdown("---")
                col_slider_84, col_radio_84 = st.columns([1, 2])
                with col_slider_84:
                    top_k_cargo = st.slider("Quantidade de palavras a exibir no gráfico de barras:", min_value=5, max_value=50, value=20, step=5, key="slider_8_4")
                with col_radio_84:
                    tipo_ngram_84 = st.radio(
                        "Filtrar por Tamanho (N-Grams):", 
                        ["Todos", "Apenas Palavras Isoladas (1)", "Pares (Bigramas)", "Trios (Trigramas)", "Quartetos (4-grams)", "Quintetos (5-grams)"],
                        horizontal=True,
                        key="radio_ngram_8_4"
                    )
                
                # Filtrar os itens baseado no tamanho do n-gram (número de espaços + 1)
                filtered_pesos = []
                for word, weight in pesos.items():
                    word_len = word.count(' ') + 1
                    if tipo_ngram_84 == "Apenas Palavras Isoladas (1)" and word_len == 1:
                        filtered_pesos.append((word, weight))
                    elif tipo_ngram_84 == "Pares (Bigramas)" and word_len == 2:
                        filtered_pesos.append((word, weight))
                    elif tipo_ngram_84 == "Trios (Trigramas)" and word_len == 3:
                        filtered_pesos.append((word, weight))
                    elif tipo_ngram_84 == "Quartetos (4-grams)" and word_len == 4:
                        filtered_pesos.append((word, weight))
                    elif tipo_ngram_84 == "Quintetos (5-grams)" and word_len == 5:
                        filtered_pesos.append((word, weight))
                    elif tipo_ngram_84 == "Todos":
                        filtered_pesos.append((word, weight))
                        
                df_pesos = pd.DataFrame(filtered_pesos, columns=["Palavra", "Peso TF-IDF"]).sort_values("Peso TF-IDF", ascending=False).head(top_k_cargo)
                
                # Pre-calculate shared roles for each word
                hover_texts = []
                for word in df_pesos["Palavra"]:
                    shared = [c for c, w in word_weights.items() if c != cargo and word in w]
                    if shared:
                        # Limit to top 5 shared roles to avoid giant tooltips
                        if len(shared) > 5:
                            shared_str = ", ".join(shared[:5]) + f" (+{len(shared)-5} cargos)"
                        else:
                            shared_str = ", ".join(shared)
                        hover_texts.append(f"Também destaque em:<br>{shared_str}")
                    else:
                        hover_texts.append("Exclusivo deste cargo/documento!")
                        
                df_pesos["Hover_Text"] = hover_texts
                
                fig_bar = px.bar(
                    df_pesos, 
                    x="Peso TF-IDF", 
                    y="Palavra", 
                    orientation='h',
                    title=f"Top {top_k_cargo} Palavras: {cargo}",
                    color="Peso TF-IDF",
                    color_continuous_scale=cmap,
                    hover_name="Palavra",
                    hover_data={"Palavra": False, "Peso TF-IDF": ":.3f", "Hover_Text": True}
                )
                # Ocultar o Hover_Text literal e usar customdata ou atualizar traces
                fig_bar.update_traces(
                    hovertemplate="<b>%{y}</b><br>Peso: %{x:.3f}<br><br>%{customdata[0]}",
                    customdata=df_pesos[["Hover_Text"]].values
                )
                fig_bar.update_layout(yaxis={'categoryorder':'total ascending', 'dtick': 1}, height=max(400, top_k_cargo * 22))
                
                st.plotly_chart(fig_bar, use_container_width=True)
                
                # --- Análise Morfológica (POS Tagging) ---
                metrics = None
                if os.path.exists("nlp_metrics.json"):
                    try:
                        with open("nlp_metrics.json", "r", encoding="utf-8") as f:
                            metrics = json.load(f)
                    except:
                        pass
                
                if metrics and 'lemma_pos_map' in metrics:
                    st.markdown("---")
                    st.markdown("### 🧩 Perfil Morfológico do Cargo")
                    st.markdown("Como o vocabulário base (Top N acima) se divide gramaticalmente?")
                    
                    pos_map = metrics['lemma_pos_map']
                    
                    verbos = []
                    subs = []
                    adjs = []
                    
                    for word in df_pesos["Palavra"]:
                        if " " in word:
                            continue # Expressão composta, não mapeamos 1 a 1 aqui
                        
                        pos = pos_map.get(word, "OUTRO")
                        if pos == "VERB":
                            verbos.append(word.title())
                        elif pos in ["NOUN", "PROPN"]:
                            subs.append(word.title())
                        elif pos == "ADJ":
                            adjs.append(word.title())
                            
                    pos_counts = {"Ações (Verbos)": len(verbos), "Objetos (Subst.)": len(subs), "Características (Adj.)": len(adjs)}
                    pos_counts = {k: v for k, v in pos_counts.items() if v > 0}
                    
                    if pos_counts:
                        c_pie_l, c_pie_c, c_pie_r = st.columns([1, 2, 1])
                        with c_pie_c:
                            fig_pie = px.pie(
                                names=list(pos_counts.keys()), 
                                values=list(pos_counts.values()),
                                hole=0.5,
                                color_discrete_sequence=["#FF7F0E", "#1F77B4", "#2CA02C"] # Laranja (Ações), Azul (Objetos), Verde (Adj)
                            )
                            fig_pie.update_layout(
                                margin=dict(t=0, b=10, l=0, r=0),
                                legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
                            )
                            st.plotly_chart(fig_pie, use_container_width=True)
                        
                        st.markdown("#### Detalhamento das Classes")
                        col_v, col_s, col_a = st.columns(3)
                        with col_v:
                            st.markdown("🎯 **Ações**")
                            if verbos:
                                st.markdown("- " + "\n- ".join([f"**{v}**" for v in sorted(verbos)]))
                            else:
                                st.info("Nenhuma ação dominante.")
                        with col_s:
                            st.markdown("📦 **Objetos/Conceitos**")
                            if subs:
                                st.markdown("- " + "\n- ".join([f"**{s}**" for s in sorted(subs)]))
                            else:
                                st.info("Nenhum objeto dominante.")
                        with col_a:
                            st.markdown("✨ **Características**")
                            if adjs:
                                st.markdown("- " + "\n- ".join([f"**{a}**" for a in sorted(adjs)]))
                            else:
                                st.info("Nenhuma característica dominante.")
                    else:
                        st.info("Nenhum dado morfológico disponível para estas palavras.")
                                
            else:
                st.info("Não há palavras com peso suficiente para este cargo.")
                
        if interaction_ui and hasattr(interaction_ui, 'render_like_button'):
            interaction_ui.render_like_button("8.4 Nuvem Palavras", "8_4")
        
    # Seção 8.5: Rede de Discurso Institucional
    elif current_section == 'sub_nlp_network_title':
        st.subheader(i18n.t("sub_nlp_network_title", default="8.5. Rede de Discurso Institucional"))
        if not tem_dados:
            st.warning("Arquivos de PLN não encontrados. Execute 'nlp_processor.py' primeiro.")
            return
            
        if not HAS_NETWORKX:
            st.warning("Para gerar os grafos de rede, instale a biblioteca executando no terminal:\npip install networkx")
            return
            
        metodo = st.radio("Método para conexões da rede:", 
                          options=["Embeddings Semânticos (Contexto/SpaCy)", "TF-IDF (Palavras Exatas)"])
                          
        df_plot = sim_spacy if "SpaCy" in metodo else sim_tfidf
        
        all_roles = list(df_plot.columns)
        roles_selected = st.multiselect("Selecione os cargos para compor a rede:", options=all_roles, default=all_roles)
        
        # Ignorar cargos virtuais para o alerta de viés
        cargos_virtuais = list(st.session_state.get('cargos_virtuais', {}).keys())
        cargos_reais_selecionados = [r for r in roles_selected if r not in cargos_virtuais]
        cargos_reais_totais = [r for r in all_roles if r not in cargos_virtuais]
        
        if len(cargos_reais_selecionados) < len(cargos_reais_totais):
            import explanations
            st.warning(explanations.get_short_bias_warning(st.session_state.get('language', 'PT-BR')))
            
        if len(roles_selected) < 2:
            st.warning("Selecione ao menos 2 cargos para gerar a rede.")
            return
            
        df_plot = df_plot.loc[roles_selected, roles_selected]
        
        col1, col2 = st.columns([1, 2])
        with col1:
            threshold_range = st.slider("Limiar de Similaridade (Arestas)", 
                                        min_value=0.0, max_value=1.0, value=(0.6, 1.0), step=0.05, 
                                        help="Exibe uma conexão entre documentos se a similaridade estiver dentro desta faixa.")
            
        with col2:
            st.markdown(f"**Grafo gerado com conexões entre {threshold_range[0] * 100:.0f}% e {threshold_range[1] * 100:.0f}% de similaridade.**")
        
        # Gerar rede
        G = nx.Graph()
        # Adicionar nós
        for doc in df_plot.columns:
            G.add_node(doc)
            
        # Adicionar arestas
        for i, row_node in enumerate(df_plot.index):
            for j, col_node in enumerate(df_plot.columns):
                if i < j:
                    weight = float(df_plot.iloc[i, j])
                    if threshold_range[0] <= weight <= threshold_range[1]:
                        G.add_edge(row_node, col_node, weight=weight)
                        
        if G.number_of_edges() == 0:
            st.warning("Nenhuma conexão encontrada com o limiar selecionado. Tente expandir os valores.")
        else:
            # Layout Force-Directed Kamada-Kawai (melhor para visualização em rede se houver nós o suficiente)
            try:
                pos = nx.kamada_kawai_layout(G)
            except:
                pos = nx.spring_layout(G, k=0.5, iterations=50, seed=42)
                
            is_light = st.session_state.get("light_mode", False)
            
            # Detecção de Comunidades
            from networkx.algorithms import community
            try:
                communities = list(community.greedy_modularity_communities(G))
                community_map = {}
                for i, comm in enumerate(communities):
                    for node in comm:
                        community_map[node] = i
            except:
                community_map = {n: 0 for n in G.nodes()}
                    
            edge_traces = []
            
            # Helper to find top common words for edge tooltip
            def get_top_common_words(node1, node2, top_n=3):
                if word_weights and node1 in word_weights and node2 in word_weights:
                    w1 = set(word_weights[node1].keys())
                    w2 = set(word_weights[node2].keys())
                    common = w1.intersection(w2)
                    if common:
                        # Pesar a interseção somando os TF-IDFs de ambos os cargos para as palavras comuns
                        scored_common = [(w, word_weights[node1][w] + word_weights[node2][w]) for w in common]
                        scored_common = sorted(scored_common, key=lambda x: x[1], reverse=True)[:top_n]
                        return ", ".join([f"{w}" for w, _ in scored_common])
                return "Dados de vocabulário indisponíveis"
            
            # Criar arestas do Plotly
            for edge in G.edges(data=True):
                x0, y0 = pos[edge[0]]
                x1, y1 = pos[edge[1]]
                weight = edge[2]['weight']
                
                mid_x = (x0 + x1) / 2
                mid_y = (y0 + y1) / 2
                
                # Normalizar peso da aresta para opacidade
                opacity = max(0.15, min(1.0, weight))
                # Cor baseada no peso (escala de avermelhado/laranja se forte, cinza se fraco)
                edge_color = f'rgba(255, 65, 54, {opacity})' if weight > 0.7 else (f'rgba(150, 150, 150, {opacity})' if not is_light else f'rgba(100, 100, 100, {opacity})')
                
                # Linha visível
                edge_traces.append(go.Scatter(
                    x=[x0, x1, None],
                    y=[y0, y1, None],
                    line=dict(width=1 + (weight * 4), color=edge_color),
                    hoverinfo='none',
                    mode='lines'
                ))
                
                # Ponto invisível para tooltip
                top_words = get_top_common_words(edge[0], edge[1])
                tooltip_text = f"<b>{edge[0]} ↔ {edge[1]}</b><br>Similaridade: {weight:.2f}<br><i>Top em Comum: {top_words}</i>"
                
                edge_traces.append(go.Scatter(
                    x=[mid_x],
                    y=[mid_y],
                    mode='markers',
                    marker=dict(size=12, color='rgba(0,0,0,0)'),
                    text=[tooltip_text],
                    hoverinfo='text',
                    showlegend=False
                ))
                
            # Criar nós do Plotly
            node_x = []
            node_y = []
            node_text = []
            node_colors = []
            node_sizes = []
            
            for node in G.nodes():
                x, y = pos[node]
                node_x.append(x)
                node_y.append(y)
                grau = G.degree(node)
                comm_id = community_map.get(node, 0)
                node_text.append(f"<b>{node}</b><br>Conexões: {grau}<br>Comunidade Visual: {comm_id + 1}")
                node_colors.append(comm_id)
                node_sizes.append(15 + (grau * 3)) # Tamanho dinâmico pelo grau
                
            node_trace = go.Scatter(
                x=node_x, y=node_y,
                mode='markers+text',
                text=[n for n in G.nodes()],
                textposition="bottom center",
                hovertext=node_text,
                hoverinfo="text",
                marker=dict(
                    showscale=True,
                    colorscale='viridis' if len(set(node_colors)) <= 8 else 'jet',
                    color=node_colors,
                    size=node_sizes,
                    colorbar=dict(
                        thickness=15,
                        title=dict(text='Comunidades', side='right'),
                        xanchor='left',
                        tickvals=list(set(node_colors)),
                        tickmode='array'
                    ),
                    line_width=2,
                    line_color='white' if not is_light else 'black'
                )
            )
            
            fig = go.Figure(data=edge_traces + [node_trace],
                          layout=go.Layout(
                              title=dict(text='<br>Rede Semântica dos Normativos (Comunidades e Palavras-Chave)', font=dict(size=18)),
                              showlegend=False,
                              hovermode='closest',
                              margin=dict(b=20,l=5,r=5,t=50),
                              annotations=[ dict(
                                  text="Arraste os nós ou faça zoom. Passe o mouse no meio das linhas para ver as palavras que os conectam.",
                                  showarrow=False,
                                  xref="paper", yref="paper",
                                  x=0.005, y=-0.002 ) ],
                              xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                              yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                              plot_bgcolor='rgba(0,0,0,0)',
                              paper_bgcolor='rgba(0,0,0,0)'
                          ))
            
            st.plotly_chart(fig, use_container_width=True)
            
        if interaction_ui and hasattr(interaction_ui, 'render_like_button'):
            interaction_ui.render_like_button("8.5 Rede PLN", "8_5")

    # Seção 8.6: Grafo de Rede de Palavras (Bipartido)
    elif current_section == 'sub_nlp_wordnet_title':
        st.subheader(i18n.t("sub_nlp_wordnet_title", default="8.6. Grafo de Rede de Palavras (Bipartido)"))
        if not tem_dados or word_weights is None:
            st.warning("Arquivos de PLN não encontrados. Execute 'nlp_processor.py' primeiro.")
            return
            
        if not HAS_NETWORKX:
            st.warning("Para gerar os grafos de rede, instale a biblioteca executando no terminal:\npip install networkx")
            return
            
        st.markdown("Visualize as conexões diretas entre Cargos/Documentos e as Palavras mais relevantes de suas atribuições.")
        
        # Filtros
        col1, col2 = st.columns(2)
        with col1:
            all_roles = list(word_weights.keys())
            selected_roles = st.multiselect("Filtrar Cargos/Documentos", options=all_roles, default=all_roles)
            
        # Extrair todas as palavras e calcular min/max de pesos
        all_words = set()
        min_w = 1.0
        max_w = 0.0
        
        for r in selected_roles:
            if r in word_weights:
                for w, weight in word_weights[r].items():
                    all_words.add(w)
                    if weight < min_w: min_w = weight
                    if weight > max_w: max_w = weight
                    
        # Evitar slider bugado se min == max ou sem palavras
        if min_w >= max_w:
            min_w = 0.0
            max_w = 1.0
            
        with col2:
            selected_words = st.multiselect("Filtrar Palavras (opcional)", options=sorted(list(all_words)))
            
        weight_range = st.slider("Filtrar por Peso (TF-IDF)", 
                                 min_value=float(min_w), max_value=float(max_w), 
                                 value=(float(min_w), float(max_w)), 
                                 step=0.01)
                                 
        if not selected_roles:
            st.info("Selecione ao menos um cargo.")
            return
            
        # Construir o Grafo
        from visualizations import plot_bipartite_network
        
        G = nx.Graph()
        
        # Adicionar nós e arestas
        for role in selected_roles:
            if role not in word_weights:
                continue
            G.add_node(role, bipartite=0, weight=30) # 0 = Cargo
            
            for word, weight in word_weights[role].items():
                if selected_words and word not in selected_words:
                    continue
                if weight_range[0] <= weight <= weight_range[1]:
                    if not G.has_node(word):
                        G.add_node(word, bipartite=1, weight=10 + (weight * 40)) # 1 = Palavra (tamanho dinamico)
                    G.add_edge(role, word, weight=weight)
                    
        # Remover nós isolados (cargos sem palavras no range)
        isolated = list(nx.isolates(G))
        G.remove_nodes_from(isolated)
        
        if G.number_of_nodes() == 0:
            st.warning("Nenhum dado para mostrar com os filtros atuais.")
        else:
            fig = plot_bipartite_network(G, title="Rede Bipartida: Cargos ↔ Palavras")
            st.plotly_chart(fig, use_container_width=True)
        
        if interaction_ui and hasattr(interaction_ui, 'render_like_button'):
            interaction_ui.render_like_button("8.6 Grafo de Palavras", "8_6")

    # Seção 8.7: Comparador Fino de Cargos e Modelagem de Tópicos
    elif current_section == 'sub_nlp_comparative_title':
        st.subheader(i18n.t("sub_nlp_comparative_title", default="8.7. Comparação Direta e Tópicos"))
        if not tem_dados or topic_models is None:
            st.warning("Arquivos de Tópicos não encontrados. Execute 'nlp_processor.py' primeiro.")
            return
            
        st.markdown("Selecione de 2 a 5 cargos para uma comparação semântica detalhada e visualize a sua composição em tópicos latentes (temas ocultos modelados matematicamente).")
        
        all_roles = list(sim_tfidf.columns)
        
        col1, col2 = st.columns([3, 1])
        with col1:
            selected_roles = st.multiselect("Selecione os cargos para comparar (Máx 5):", options=all_roles, max_selections=5)
        with col2:
            num_topics = st.slider("Qtd de Tópicos Modelados:", min_value=2, max_value=10, value=6, step=1, help="Define o nível de granularidade dos temas descobertos.")
            
        if len(selected_roles) >= 2:
            st.divider()
            
            k_key = str(num_topics)
            if k_key in topic_models:
                topic_data = topic_models[k_key]
                
                c_radar, c_words = st.columns([1, 1])
                
                with c_radar:
                    st.markdown("### 🕸️ Radar Semântico de Tópicos")
                    # Build Radar Chart
                    fig = go.Figure()
                    for role in selected_roles:
                        if role in topic_data["document_topics"]:
                            dist = topic_data["document_topics"][role]
                            # Mapear os valores e criar um nome descritivo (Top 2 palavras)
                            categories = []
                            values = []
                            for i in range(1, num_topics + 1):
                                t_key = f"Tópico {i}"
                                top_words = list(topic_data["topic_words"][t_key].keys())[:2]
                                nice_name = f"T{i} ({top_words[0].title()})"
                                categories.append(nice_name)
                                values.append(dist.get(t_key, 0))
                                
                            # Close the polygon
                            values.append(values[0])
                            cat_closed = categories + [categories[0]]
                            
                            fig.add_trace(go.Scatterpolar(
                                r=values,
                                theta=cat_closed,
                                fill='toself',
                                name=role
                            ))
                            
                    fig.update_layout(
                        polar=dict(
                            radialaxis=dict(visible=True, range=[0, 1])
                        ),
                        showlegend=True,
                        legend=dict(orientation="h", y=-0.2)
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    st.markdown("**O que significa cada tópico?**")
                    with st.expander("Ver palavras-chave dos Tópicos", expanded=False):
                        for i in range(1, num_topics + 1):
                            t_key = f"Tópico {i}"
                            words_dict = topic_data["topic_words"][t_key]
                            top_words = list(words_dict.keys())
                            t_name = f"T{i} ({top_words[0].title()} / {top_words[1].title()})"
                            top_w = ", ".join(top_words[:7])
                            st.markdown(f"- **{t_name}**: {top_w}")
                            
                with c_words:
                    st.markdown("### 🧩 Intersecção Exata (TF-IDF)")
                    
                    # Intersecção e exclusividade
                    vocab_sets = []
                    for role in selected_roles:
                        if role in word_weights:
                            vocab_sets.append(set(word_weights[role].keys()))
                        else:
                            vocab_sets.append(set())
                            
                    common_vocab = set.intersection(*vocab_sets) if vocab_sets else set()
                    
                    st.success(f"**Vocabulário em Comum ({len(common_vocab)} palavras):**\n" + ", ".join(sorted(common_vocab)))
                    
                    for i, role in enumerate(selected_roles):
                        others = [vocab_sets[j] for j in range(len(selected_roles)) if j != i]
                        exclusive = vocab_sets[i].difference(*others) if others else set()
                        st.info(f"**Exclusivo de {role}:**\n" + ", ".join(sorted(exclusive)))
                        
                    st.markdown("### 📏 Distância Matemática Direta")
                    st.markdown("Quão próximos esses cargos estão no espaço vetorial global?")
                    # Distâncias
                    for i in range(len(selected_roles)):
                        for j in range(i + 1, len(selected_roles)):
                            r1 = selected_roles[i]
                            r2 = selected_roles[j]
                            val_tfidf = sim_tfidf.loc[r1, r2]
                            val_spacy = sim_spacy.loc[r1, r2]
                            
                            st.markdown(f"**{r1}** ↔ **{r2}**")
                            c_dist1, c_dist2 = st.columns(2)
                            c_dist1.metric("Similaridade (Palavras)", f"{val_tfidf*100:.1f}%")
                            c_dist2.metric("Similaridade (Contexto)", f"{val_spacy*100:.1f}%")
            else:
                st.error("Modelo de tópicos não encontrado para este valor de K. Execute nlp_processor.py novamente.")
        else:
            st.info("Selecione pelo menos 2 cargos para gerar a comparação detalhada.")
            
        if interaction_ui and hasattr(interaction_ui, 'render_like_button'):
            interaction_ui.render_like_button("8.7 Comparador Tópicos", "8_7")

    # Seção 8.8: Validação Estatística (Teste de Mantel)
    elif current_section == 'sub_nlp_stats_title':
        st.subheader(i18n.t("sub_nlp_stats_title", default="8.8. Validação Estatística"))
        if not tem_dados:
            st.warning("Arquivos de PLN não encontrados. Execute 'nlp_processor.py' primeiro.")
            return
            
        st.markdown("Nesta seção, avaliamos matematicamente se os dois motores analíticos (TF-IDF e SpaCy Embeddings) concordam sobre a estruturação e a similaridade entre os cargos da instituição.")
        
        # Carregar métricas
        metrics = {}
        try:
            with open("nlp_metrics.json", "r", encoding='utf-8') as f:
                metrics = json.load(f)
        except:
            pass
            
        sil_tfidf = metrics.get('silhouette_score', 0.0)
        sil_spacy = metrics.get('silhouette_score_spacy', 0.0)
        r_mantel = metrics.get('mantel_r', 0.0)
        p_mantel = metrics.get('mantel_p', 0.0)
        rho_spearman = metrics.get('spearman_rho', 0.0)
        
        if r_mantel == 0.0:
            st.warning("As métricas do Teste de Mantel não foram encontradas. Execute 'nlp_processor.py' para gerar os dados estatísticos.")
        else:
            st.markdown("### 1. Teste de Mantel (Correlação de Matrizes)")
            st.markdown("O Teste de Mantel compara duas matrizes de distância para verificar se elas estão correlacionadas de forma não-aleatória.")
            st.info("**Correlação Linear (Pearson R)**: Mede o quanto a intensidade (o valor exato da similaridade) bate nos dois modelos. Valores altos indicam que a similaridade semântica cresce junto com a similaridade de palavras exatas.\n\n**Correlação Monotônica (Spearman ρ)**: Avalia apenas o *ranking*. Se o Cargo A é o vizinho mais próximo do Cargo B no primeiro modelo, ele continua sendo o vizinho mais próximo no segundo modelo?")
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Correlação Linear (Pearson R)", f"{r_mantel:.3f}")
            c2.metric("Correlação Monotônica (Spearman ρ)", f"{rho_spearman:.3f}")
            c3.metric("Significância (p-valor)", f"{p_mantel:.4f}")
            
            with st.expander("📖 Guia de Leitura (O que significam esses números?)"):
                st.markdown("""
                **Como ler os Coeficientes (Pearson R e Spearman ρ):**
                Vão de **-1 a 1**. 
                * **1.0** = Concordância absoluta (clones perfeitos).
                * **0.7 a 0.9** = Correlação Forte (eles concordam muito).
                * **0.4 a 0.6** = Correlação Moderada (concordam um pouco).
                * **0.0** = Zero concordância (totalmente aleatório).
                * **Negativo** = Correlação Inversa (quando um acha parecido, o outro acha o oposto).
                
                **Como ler a Significância (p-valor):**
                Mede o risco do nosso resultado ter sido "pura sorte".
                * **Abaixo de 0.05:** É estatisticamente seguro afirmar que a correlação é real. 
                * **Acima de 0.05:** O resultado pode ser coincidência (falta de robustez estatística).
                """)
                
            if p_mantel < 0.05:
                if r_mantel > 0.7:
                    st.success("Temos uma **correlação FORTE** e estatisticamente **SIGNIFICANTE**. Os modelos TF-IDF e SpaCy concordam majoritariamente sobre quais cargos são próximos.")
                elif r_mantel > 0.4:
                    st.info("Temos uma **correlação MODERADA** e estatisticamente **SIGNIFICANTE**. Os modelos concordam em parte, revelando nuances diferentes da mesma base.")
                else:
                    st.warning("Temos uma **correlação FRACA**, porém significante. Os modelos estão interpretando os textos de formas estruturalmente distintas.")
            else:
                st.error("A correlação **NÃO É SIGNIFICATIVA** (p >= 0.05). Não podemos descartar a aleatoriedade.")
                
            st.markdown("---")
            st.markdown("### 2. Dispersão de Concordância (TF-IDF vs SpaCy)")
            st.markdown("Cada ponto representa um par de cargos. Quanto mais perto da diagonal, maior a concordância absoluta entre os motores.")
            
            # Pegar triângulo superior das matrizes
            n = len(sim_tfidf.columns)
            import numpy as np
            idx = np.triu_indices(n, k=1)
            
            # Limpar nomes
            names = list(sim_tfidf.columns)
            pares = []
            for i in range(len(idx[0])):
                pares.append(f"{names[idx[0][i]]} ↔ {names[idx[1][i]]}")
                
            df_scatter = pd.DataFrame({
                "Par": pares,
                "TF-IDF": sim_tfidf.values[idx],
                "SpaCy": sim_spacy.values[idx]
            })
            
            import plotly.express as px
            fig_scatter = px.scatter(df_scatter, x="TF-IDF", y="SpaCy", hover_name="Par",
                                     trendline="ols", trendline_color_override="red",
                                     title="Concordância TF-IDF vs SpaCy",
                                     labels={"TF-IDF": "Similaridade TF-IDF (Frequência)", "SpaCy": "Similaridade SpaCy (Semântica)"})
            st.plotly_chart(fig_scatter, use_container_width=True)
            
            st.markdown("#### 🔎 Micro-Correlações (Irmãos Gêmeos)")
            st.markdown("Para exemplificar a diferença real dos motores estatísticos, veja abaixo quais são os pares de cargos que cada modelo classificou como os **mais idênticos** de toda a base. Note como a semântica (SpaCy) pode encontrar pares diferentes da contagem exata (TF-IDF):")
            
            top_n_micro = st.slider("Quantidade de pares no Top Ranking:", min_value=3, max_value=20, value=5, step=1, key="slider_top_micro")
            
            c_top1, c_top2 = st.columns(2)
            
            with c_top1:
                st.markdown(f"**🏆 Top {top_n_micro} (Vocabulário Exato - TF-IDF)**")
                df_top_tfidf = df_scatter.sort_values(by="TF-IDF", ascending=False).head(top_n_micro)
                for _, row_t in df_top_tfidf.iterrows():
                    st.markdown(f"- {row_t['Par']} *(**{row_t['TF-IDF']*100:.1f}%**)*")
                    
            with c_top2:
                st.markdown(f"**🏆 Top {top_n_micro} (Semântica e Contexto - SpaCy)**")
                df_top_spacy = df_scatter.sort_values(by="SpaCy", ascending=False).head(top_n_micro)
                for _, row_t in df_top_spacy.iterrows():
                    st.markdown(f"- {row_t['Par']} *(**{row_t['SpaCy']*100:.1f}%**)*")
                    
            import plotly.graph_objects as go
            import plotly.figure_factory as ff
            
            st.markdown("#### Distribuição de Densidade (KDE)")
            st.markdown("A curva abaixo revela o comportamento massivo do modelo. Se a curva do SpaCy estiver mais à direita, significa que o modelo semântico enxerga a instituição como mais homogênea/unida do que o modelo focado apenas em palavras.")
            try:
                hist_data = [df_scatter['TF-IDF'].values, df_scatter['SpaCy'].values]
                group_labels = ['TF-IDF (Palavras)', 'SpaCy (Semântica)']
                colors = ['#1f77b4', '#d62728']
                fig_kde = ff.create_distplot(hist_data, group_labels, colors=colors, show_hist=False, show_rug=False)
                fig_kde.update_layout(title_text="Distribuição de Similaridades (TF-IDF vs SpaCy)", xaxis_title="Score de Similaridade", yaxis_title="Densidade")
                st.plotly_chart(fig_kde, use_container_width=True)
            except Exception as e:
                pass
            
            st.markdown("---")
            st.markdown("### 3. Matriz de Divergência (Onde os motores discordam?)")
            st.markdown("O mapa abaixo representa a diferença crua entre os modelos (**SpaCy menos TF-IDF**). Onde for intensamente **vermelho**, a Inteligência Semântica achou muito parecido, mas a métrica de palavras discorda. Onde for **azul**, as atribuições têm as exatas mesmas palavras, mas contextos isolados.")
            
            diff_matrix = sim_spacy - sim_tfidf
            
            # Encurtar inteligentemente as legendas para caber, mas mantendo o ano para não gerar duplicadas
            def shorten_name(name):
                text = str(name)
                text = text.replace("Agente de Telecomunicações Policial", "Ag. Telecomunicações")
                text = text.replace("Desenhista Técnico Pericial", "Desenhista Téc.")
                text = text.replace("Auxiliar de Autópsia", "Aux. Autópsia")
                # Trocar (2017) por ('17)
                import re
                text = re.sub(r'\(20(\d{2})\)', r"('\1)", text)
                text = re.sub(r'\(19(\d{2})\)', r"('\1)", text)
                return text

            short_labels = [shorten_name(x) for x in diff_matrix.columns]
            
            # Usar .values para contornar a limitação de nomes duplicados no dataframe base (narwhals)
            fig_diff = px.imshow(diff_matrix.values, 
                                 x=short_labels,
                                 y=short_labels,
                                 color_continuous_scale="RdBu_r", zmin=-0.5, zmax=0.5,
                                 title="Mapa de Divergência (SpaCy - TF-IDF)",
                                 aspect="auto")
            
            fig_diff.update_layout(
                height=600,
                margin=dict(l=10, r=10, t=50, b=10)
            )
            fig_diff.update_xaxes(tickangle=45, tickfont=dict(size=11))
            fig_diff.update_yaxes(tickfont=dict(size=11))
            
            st.plotly_chart(fig_diff, use_container_width=True)
            
            st.markdown("---")
            st.markdown("### 4. Coesão de Agrupamentos (Silhouette Score)")
            st.markdown("O Silhouette Score (variando de -1 a 1) mede a coesão interna dos grupos gerados pelo algoritmo K-Means. Valores maiores indicam que os cargos de um mesmo grupo são mais parecidos entre si do que com cargos de outros grupos.")
            
            col_sil1, col_sil2 = st.columns(2)
            col_sil1.metric("Silhouette Score (TF-IDF)", f"{sil_tfidf:.3f}")
            col_sil2.metric("Silhouette Score (SpaCy)", f"{sil_spacy:.3f}")
            
            if sil_spacy > sil_tfidf:
                st.markdown("> O motor vetorial **SpaCy formou grupos mais coesos** na nossa base do que o TF-IDF.")
            elif sil_tfidf > sil_spacy:
                st.markdown("> O motor matemático **TF-IDF formou grupos mais coesos** na nossa base do que o SpaCy.")
            else:
                st.markdown("> Os motores apresentaram **a mesma coesão estrutural**.")
                
            sil_samples_tfidf = metrics.get('silhouette_samples_tfidf', {})
            sil_samples_spacy = metrics.get('silhouette_samples_spacy', {})
            
            if sil_samples_tfidf and sil_samples_spacy:
                st.markdown("#### Perfil de Silhouette Individual")
                st.markdown("Cargos com barras grandes apontadas para a **direita** (positivas) estão perfeitamente encaixados nos seus agrupamentos originais. Barras apontadas para a **esquerda** (negativas) representam cargos 'alienígenas' ou híbridos, que foram forçados num grupo mas possuem fortes afinidades com outros ramos.")
                df_sil_ind = pd.DataFrame({
                    "Cargo": list(sil_samples_tfidf.keys()),
                    "TF-IDF": list(sil_samples_tfidf.values()),
                    "SpaCy": list(sil_samples_spacy.values())
                })
                df_sil_ind = df_sil_ind.melt(id_vars=["Cargo"], var_name="Modelo", value_name="Silhouette")
                fig_sil = px.bar(df_sil_ind, x="Silhouette", y="Cargo", color="Modelo", barmode="group",
                                 title="Coesão Individual por Cargo", orientation="h")
                fig_sil.update_layout(height=800, yaxis={'categoryorder':'total ascending'})
                st.plotly_chart(fig_sil, use_container_width=True)
                
        if interaction_ui and hasattr(interaction_ui, 'render_like_button'):
            interaction_ui.render_like_button("8.8 Validação Estatística", "8_8")
