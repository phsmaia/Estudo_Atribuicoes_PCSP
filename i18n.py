import streamlit as st

import pandas as pd
import os

# Base static dictionaries (fallback)
dic_traducao_cargos = {
    "Investigador de Polícia (+ Apoio)": "Police Investigator (+ Support)",
    "Policial Civil (todos os cargos)": "Civil Police (all roles)"
}

dic_traducao_atribuicoes = {
    "Portar arma de fogo e documento de identidade funcional": "Carry a firearm and official ID",
    "Atuar com possibilidade de exposição a situações de risco": "Act with potential exposure to risk situations",
    "Realizar diligências": "Conduct police diligences/investigations",
    "Conduzir viaturas policiais": "Drive police vehicles",
    "Atendimento ao público": "Customer/Public service",
    "Cumprir mandados": "Execute warrants",
    "Elaborar relatórios": "Prepare reports",
    "Preservar local de crime": "Preserve crime scenes",
    
    # Missing explicit generic assignments from older scenarios
    "portar arma, distintivo e algemas": "Carry weapon, badge, and handcuffs",
    "atender sempre, com urbanidade e eficiência, o público em geral, pessoalmente ou por telefone": "Always serve the general public, in person or by phone, with urbanity and efficiency",
    "elaborar, sob orientação da Autoridade Policial, registro de ocorrência": "Prepare incident reports under the guidance of the Police Authority",
    "conduzir viatura policial": "Drive police vehicles",
    "cumprir diligência e/ou requisição determinada pela Autoridade Policial, elaborando relatório respectivo": "Fulfill diligences and/or requests determined by the Police Authority, preparing the respective report",
    "proceder à abordagem de pessoas suspeitas da prática de ilícitos, realizando busca pessoal quando necessário": "Approach individuals suspected of illicit practices, performing personal searches when necessary",
    "identificar pessoas, inclusive por meio digital, nas hipóteses em que tal providência se faça necessária": "Identify people, including by digital means, when necessary",
    "conduzir e apresentar pessoas legalmente presas à Autoridade Policial competente ou onde for por ela determinado": "Escort and present legally arrested people to the competent Police Authority",
    "auxiliar a Autoridade Policial na formalização de atos de polícia judiciária": "Assist the Police Authority in formalizing acts of judicial police",
    "operar os sistemas de comunicação e de dados da Polícia Civil": "Operate the Civil Police's communication and data systems",
    
    "secretariar atos de polícia judiciária": "Serve as secretary for judicial police acts",
    "transporte de pessoas / coisas de ocorrência policial": "Transport people/goods related to police occurrences",
    "transporte de pessoas/ coisas...": "Transport people/goods...",
    "análises de substâncias orgânica / inorgânicas": "Analyze organic/inorganic substances",
    "análises de substâncias...": "Analyze organic/inorganic substances...",
    "identificação civil e criminal com papiloscopia e retrato falado": "Civil and criminal identification using papiloscopy and composite sketches",
    "identificação civil e criminal...": "Civil and criminal identification...",
    "projeções de envelhecimento e rejuvenecimento": "Age progression and regression projections",
    "projeções de envelhecimento...": "Age progression...",
    "registrar e encaminhar dados de clssificação papiloscópica": "Register and forward papiloscopic classification data",
    "registrar e encaminhar dados...": "Register and forward papiloscopic data...",
    "elaborar levantamento planimétrico": "Prepare planimetric surveys",
    "assessoramento técnico papiloscópico": "Papiloscopic Technical Assistance",
    "suporte a desastres": "Disaster Support",
    
    # Just in case, the ones with trailing ellipses the user mentioned:
    "atender sempre, com urbanidade...": "Always serve the general public, with urbanity...",
    "elaborar, sob orientação da Autoridade Policia...": "Prepare incident reports under the guidance...",
    "cunpri diligência e/ou requisição...": "Fulfill diligences and/or requests...",
    "proceder à abordagem de pessoas suspeitas...": "Approach individuals suspected of illicit practices..."
}

def init_translations():
    # Carregar Cargos
    try:
        if os.path.exists('cargos_ingles_descricao.csv'):
            df_cargos = pd.read_csv('cargos_ingles_descricao.csv', encoding='utf-8')
            pt_col = 'Cargo em Português' if 'Cargo em Português' in df_cargos.columns else df_cargos.columns[0]
            en_col = 'Melhor Tradução em Inglês' if 'Melhor Tradução em Inglês' in df_cargos.columns else df_cargos.columns[1]
            for _, row in df_cargos.iterrows():
                pt_val = str(row[pt_col]).strip()
                en_val = str(row[en_col]).strip()
                if pt_val and en_val and pt_val != 'nan':
                    dic_traducao_cargos[pt_val] = en_val
    except:
        pass

    # Carregar Atribuições
    try:
        if os.path.exists('Atribuicoes_Carreiras_Editais.CSV'):
            df_editais = None
            for enc in ['utf-8', 'iso-8859-1', 'cp1252']:
                try:
                    df_editais = pd.read_csv('Atribuicoes_Carreiras_Editais.CSV', sep=';', encoding=enc)
                    break
                except UnicodeDecodeError:
                    pass
            
            if df_editais is not None:
                if 'atribuicao' in df_editais.columns and 'atribuicao_inglês' in df_editais.columns:
                    for _, row in df_editais.iterrows():
                        pt_val = str(row['atribuicao']).strip()
                        en_val = str(row['atribuicao_inglês']).strip()
                        if pt_val and en_val and pt_val != 'nan' and en_val != 'nan':
                            dic_traducao_atribuicoes[pt_val] = en_val
                            
                if 'Reduzida' in df_editais.columns and 'Reduzida_Inglês' in df_editais.columns:
                    for _, row in df_editais.iterrows():
                        pt_val = str(row['Reduzida']).strip()
                        en_val = str(row['Reduzida_Inglês']).strip()
                        if pt_val and en_val and pt_val != 'nan' and en_val != 'nan':
                            dic_traducao_atribuicoes[pt_val] = en_val
    except:
        pass

    # Forçar traduções hardcoded genéricas por cima do CSV caso o CSV esteja mal traduzido nessas linhas
    hardcoded = {
        "Portar arma de fogo e documento de identidade funcional": "Carry a firearm and official ID",
        "Atuar com possibilidade de exposição a situações de risco": "Act with potential exposure to risk situations",
        "Realizar diligências": "Conduct police diligences/investigations",
        "Conduzir viaturas policiais": "Drive police vehicles",
        "Atendimento ao público": "Customer/Public service",
        "Cumprir mandados": "Execute warrants",
        "Elaborar relatórios": "Prepare reports",
        "Preservar local de crime": "Preserve crime scenes"
    }
    dic_traducao_atribuicoes.update(hardcoded)

# Initialize once
init_translations()

def _traduzir_cargo_simples(cargo):
    c_limpo = cargo.strip()
    if c_limpo in dic_traducao_cargos:
        return dic_traducao_cargos[c_limpo]
        
    c_lower = c_limpo.lower()
    for k, v in dic_traducao_cargos.items():
        if k.lower() == c_lower:
            return v
    return cargo

def traduzir_cargo(cargo_pt):
    if pd.isna(cargo_pt):
        return cargo_pt
    cargo_pt_str = str(cargo_pt).strip()
    
    # Se já existe no dicionário exato, retorna direto
    if cargo_pt_str in dic_traducao_cargos:
        return dic_traducao_cargos[cargo_pt_str]
    
    # Q1-A: Regra dinâmica para mesclagens (ex: "Cargo A (+ Cargo B + Cargo C)")
    if "(+" in cargo_pt_str:
        partes = cargo_pt_str.split("(+")
        cargo_base = partes[0].strip()
        cargos_extra = partes[1].replace(")", "").split("+")
        
        base_trad = _traduzir_cargo_simples(cargo_base)
        extras_trad = []
        for extra in cargos_extra:
            trad = _traduzir_cargo_simples(extra.strip())
            # A lógica retira "Police " de itens secundários para evitar repetição excessiva, ex "Investigator (+ Agent)"
            trad = trad.replace("Police ", "")
            extras_trad.append(trad)
            
        return f"{base_trad} (+ {' + '.join(extras_trad)})"
        
    # Fallback ignorando case
    return _traduzir_cargo_simples(cargo_pt_str)

import re

def _traduzir_atribuicao_simples(atrib):
    atrib_str = str(atrib).strip(" .")
    # Q2-A: Tenta traduzir exato
    if atrib_str in dic_traducao_atribuicoes:
        return dic_traducao_atribuicoes[atrib_str]
        
    # Fallback super resiliente
    # Remove \xa0, \t, etc e normaliza múltiplos espaços para um só
    a_norm = re.sub(r'\s+', ' ', atrib_str.lower().replace('\xa0', ' ')).strip()
    
    for k, v in dic_traducao_atribuicoes.items():
        k_norm = re.sub(r'\s+', ' ', str(k).lower().replace('\xa0', ' ')).strip(" .")
        if k_norm == a_norm:
            return v
            
    # Como último recurso, tenta ver se a chave do dicionário está CONTIDA na atribuição
    for k, v in dic_traducao_atribuicoes.items():
        k_norm = re.sub(r'\s+', ' ', str(k).lower().replace('\xa0', ' ')).strip(" .")
        if len(k_norm) > 10 and k_norm in a_norm:
            return v
            
    return atrib

def traduzir_atribuicao(atrib_pt):
    if pd.isna(atrib_pt):
        return atrib_pt
    
    atrib_pt_str = str(atrib_pt).strip()
    
    # Lida com colunas aglutinadas geradas por condensar_dataframe ("A / B")
    if ' / ' in atrib_pt_str:
        partes = [p.strip() for p in atrib_pt_str.split(' / ')]
        return ' / '.join([_traduzir_atribuicao_simples(p) for p in partes])
        
    return _traduzir_atribuicao_simples(atrib_pt_str)


TRANSLATIONS = {
    "PT-BR": {
        "title": "Painel Interativo: Estudo de Atribuições da PCSP (2024)",
        "view_modes": "Modos de Visão:",
        "nav_analytic": "Navegação Analítica:",
        "mode_1": "1. Explorador Individual",
        "mode_2": "2. Análise de Cenários (Comparativo A x B)",
        "mode_3": "3. Comparação Global (Macro)",
        "mode_4": "4. Rastreamento Longitudinal (Micro)",
        "explanation_mode": "📖 Modo de Explicações Detalhadas",
        "reading_tone": "Tom de Leitura:",
        "tone_academic": "👨‍🔬 Acadêmico / Técnico",
        "tone_layman": "🗣️ Leigo / Simplificado",
        "language_selector": "🌐 Idioma / Language",
        
        "config_analytic": "⚙️ Configurações Analíticas e Controles",
        "select_scenario": "Selecione o Cenário:",
        "fast_filter": "Filtro Rápido de Cargos:",
        "filter_all": "Todos os cargos da Polícia Civil",
        "filter_no_cientifica": "Polícia Civil sem cargos da Polícia Científica",
        "filter_only_cientifica": "Polícia Civil com somente Polícia Científica",
        "filter_custom": "Personalizado",
        "include_generic": "Incluir Atribuições Genéricas a Todos",
        "matrix_format": "Formato da Matriz:",
        "condensed": "Condensada (Aglutina repetições)",
        "original": "Original (Dados brutos)",
        "expand_texts": "Expandir textos nos tooltips",
        "roles_analyze": "Cargos para Analisar:",
        "visual_highlight": "🎨 Destaque Visual (Opcional):",
        "config_compare": "⚙️ Configurações do Comparativo A x B",
        "scenario_a": "📌 Cenário A (Base):",
        "scenario_b": "📌 Cenário B (Comparação):",
        "career_detail": "🔎 Selecione a Carreira para Análise Detalhada:",
        "none_overview": "Nenhuma (Visão Geral)",
        "highlight_help": "Realça essas carreiras nos gráficos e tabelas.",
        "badge_scenario": "⚙️ Cenário:",
        "badge_matrix": "📊 Matriz:",
        "badge_generic": "👥 Genéricas:",
        "badge_texts": "🏷️ Textos Extensos:",
        "badge_roles": "🚓 Cargos:",
        "badge_mode": "⚙️ Modo:",
        "badge_filtered_careers": "🔍 Carreiras Filtradas:",
        "lbl_condensed": "Condensada",
        "lbl_original": "Original",
        "lbl_on": "ON",
        "lbl_off": "OFF",
        "lbl_selected": "Selecionados",
        "kpi_orig_title": "Atribuições Originais",
        "kpi_orig_help": "Total de atribuições únicas extraídas dos editais para os cargos selecionados, antes de aglutinar as redundâncias.",
        "kpi_cond_title": "Atribuições Condensadas",
        "kpi_cond_help": "Quantidade de colunas exclusivas na matriz após juntar numa só as atribuições idênticas que eram comuns a múltiplos cargos.",
        "kpi_red_title": "Redução",
        "kpi_red_help": "Diferença absoluta entre as atribuições originais e as condensadas (quantidade de ruído/redundância eliminada).",
        "kpi_pct_title": "Porcentagem de Redução",
        "kpi_pct_help": "Percentual que representa o nível de redundância normativa que foi superada pela metodologia na comparação.",
        "expander_math": "ⓘ Suposição Matemática Ativa (Metodologia de Condensação)",
        "expander_math_text": "As matrizes abaixo transformam listas de atribuições textuais em coordenadas numéricas. Ao passarem pela **Condensação**, repetições exatas entre os mesmos cargos viram uma única coluna. Isso impede que atribuições divididas em 10 itens no edital (mas que significam a mesma coisa) causem um 'peso estatístico artificial' que aproxime duas carreiras de forma incorreta.",
        "sub_matrix": "1.1. Matriz de Atribuições",
        "sub_matrix_help": "**Como interpretar:** Exibe o valor '1' se o cargo possui a atribuição normativa e '0' caso não possua. \n\n**Cálculo:** Construída lendo os manuais e editais. No modo 'Condensada', a matriz aglutina atribuições que possuem o exato mesmo padrão de repetição (ex: atribuições comuns a um mesmo grupo de cargos viram uma única coluna com peso 1) para evitar que redundâncias documentais criem distorções de peso estatístico.",
        "tip_hover": "💡 <em>Dica: Passe o mouse sobre as células (quadrados coloridos) para ler a atribuição normativa completa.</em>",
        "sub_adj": "1.2. Matriz de Adjacência (Atribuições Compartilhadas)",
        "sub_adj_help": "**Como interpretar:** Exibe a contagem absoluta de quantas atribuições normativas dois cargos distintos compartilham entre si. Valores mais altos (cores fortes) indicam forte justaposição funcional.\n\n**Cálculo:** Feito através do Produto Escalar cruzando a Matriz de Atribuições contra si própria (sua transposta).",
        "sub_dyn": "1.3. Explorador Dinâmico de Atribuições",
        "sub_dyn_help": "**Como interpretar:** Permite cruzar dados manualmente simulando as tabelas dinâmicas do estudo original. Nota: No artigo o cruzamento limitou-se a 3 carreiras por falta de espaço em página, mas aqui o sistema calcula e confronta todas as carreiras ativas simultaneamente.\n\n**Porcentagens:** Exibe o volume de atribuições que cada cargo representa em relação ao somatório total de atribuições únicas na Polícia Civil.",
        "warning_bias": "⚠️ VIÉS AMOSTRAL",
        "roles_explanation": "💡 **Sobre os Nomes dos Cargos:** Os títulos oficiais (*Investigador de Polícia, Perito Criminal*, etc.) são mantidos em português para preservar a integridade jurídica e a precisão documental do estudo, já que não existem traduções equivalentes diretas para a estrutura policial brasileira em outras culturas.",
        "tab_roles": "Filtro por Cargo (O que eles compartilham?)",
        "tab_assignments": "Filtro por Atribuição (Quem faz isso?)",
        "base_total": "Base Total de Análise:",
        "base_desc": "atribuições normativas possíveis na matriz de dados.",
        "roles_label": "Cargos:",
        "filter_assignments": "Filtro de Atribuições:",
        "op_all": "🌟 Mostrar Todas",
        "op_excl": "🔸 Somente Exclusivas da Seleção (Nenhum cargo de fora faz)",
        "op_comp_out": "🔹 Somente Compartilhadas (Cargos de fora também fazem)",
        "op_comp_in": "✅ Somente Compartilhadas (Cargos selecionados)",
        "status_all": "✅ Compartilhada por Todos",
        "status_excl": "🔸 Exclusiva de 1 Cargo",
        "status_some": "🔹 Compartilhada por Alguns",
        "norm_weight": "##### Peso Normativo (Montante de Atribuições por Cargo)",
        "cross_table": "##### Quadro de Cruzamento de Atribuições",
        "select_assignments_desc": "Selecione uma ou mais atribuições para descobrir quais carreiras policiais as possuem formalmente em seus escopos.",
        "assignments_label": "Atribuições:",
        "sub_graph": "1.4. Grafo de Similaridade (Baseado em Adjacência)",
        "sub_graph_help": "**Como interpretar:** Representação de rede onde as 'bolas' (nós) representam as carreiras policiais e as 'linhas' (arestas) indicam que há uma intersecção de funções. A espessura da linha simboliza a quantidade de funções compartilhadas.\n\n**Cálculo:** Renderizado pelo motor NetworkX com física Fruchterman-Reingold (Spring Layout), que cria forças de repulsão magnética entre os nós, permitindo que cargos altamente conectados 'puxem' uns aos outros para o centro do agrupamento (cluster).",
        "threshold_adj": "Corte de Adjacência (Threshold de Conexões):",
        "sub_gower": "1.5. Mapa de Calor de Similaridade (Distância de Gower)",
        "sub_gower_help": "**Como interpretar o Mapa:** Visão térmica do distanciamento. Áreas vermelhas representam cargos idênticos (Distância próxima de 0.0).\n\n**Cálculo:** Diferente da adjacência (contagem bruta), este usa o Coeficiente de Gower entre 0 e 1, cruzando arrays de presenças (1) e ausências (0) penalizando distorções.",
        "sub_ruler": "1.6. Régua de Afinidade Unidimensional (Gower)",
        "sub_ruler_help": "**Como interpretar:** Transforma a matriz complexa do Gower em um Ranking simples, tomando um cargo específico como 'ponto zero' e listando os demais em ordem de distância funcional.\n\n**Uso:** Excelente para ver quem é o cargo mais próximo e o mais distante funcionalmente da carreira selecionada.",
        "select_ruler_role": "📌 Selecione a Carreira de Referência (Ponto Zero):",
        "sub_dendro": "1.7. Árvore Hierárquica (Dendograma)",
        "sub_dendro_help": "**Como interpretar:** Classifica e agrupa sub-blocos de carreiras que possuem alta afinidade. Se duas carreiras se conectam mais para baixo (mais à esquerda nos eixos X), significa que são funcionalmente muito idênticas e foram agrupadas primeiro na base.\n\n**Cálculo:** Utiliza Algoritmo de Clusterização Hierárquica sobre as métricas da Matriz de Gower. Foi utilizado o método aglomerativo *Single-linkage*, que calcula a distância mínima entre membros de grupos adjacentes.",
        "dendro_method": "Agrupamento hierárquico das distâncias de Gower usando o método *single*.",
        "dendro_warning": "Selecione mais de um cargo para gerar a árvore hierárquica.",
        "dendro_title": "Dendograma Gower",
        "sub_upset": "1.8. Diagrama de Conjuntos (Interseções Exatas)",
        "sub_upset_help": "**Como interpretar:** Funciona como um 'Diagrama de Venn' escalável. Ele varre as centenas de combinações possíveis entre os cargos e lista as maiores fatias em comum. A barra revela exatamente quantas atribuições aquele 'bloco' de cargos exclusivo possui.\n\n**Por que não usar um Diagrama de Venn circular?** Matematicamente, círculos só conseguem se sobrepor em todas as permutações para, no máximo, 4 conjuntos. Como possuímos 14 cargos diferentes, um Venn seria geometricamente impossível de ser desenhado sem violar as leis espaciais. Este formato (UpSet Plot) é o padrão ouro na visualização multicamadas na Ciência de Dados.",
        "upset_title": "Top Interseções Normativas (Granular)",
        
        # --- MODO 2: COMPARATIVO A X B ---
        "mode2_tooltip": "Modo 2: Permite comparar o grau de distanciamento, afinidade e fluxo de funções normativas entre as carreiras policiais nos dois cenários temporais.",
        "badge_scenario_a": "📌 A: ",
        "badge_scenario_b": "📌 B: ",
        "scenario_origin_tooltip": "Cenário de Origem da comparação (De onde os cargos partiram)",
        "scenario_dest_tooltip": "Cenário de Destino da comparação (Para onde os cargos foram)",
        "tracking_title": "Rastreia as perdas e ganhos funcionais de uma carreira específica entre os dois cenários escolhidos.",
        "tracking_main": "🔍 Rastreando carreira principal:",
        "highlights_lbl": "🎨 Destaques:",
        "warning_diff_scenarios": "Selecione cenários diferentes no Painel Superior para comparar.",
        "sub_delta_title": "2.1. Delta de Similaridade de Gower ({cenario_a} → {cenario_b})",
        "sub_delta_help": "**O que é isso?**\nEste mapa de calor matemático calcula a diferença vetorial exata entre os dois cenários.\n\n**Como ler:**\n- **Azul (Negativo)**: A distância entre os cargos diminuiu. Eles se tornaram mais parecidos (Aglutinação de funções).\n- **Vermelho (Positivo)**: A distância aumentou. Eles se afastaram e tornaram-se mais exclusivos/distintos.\n- **Branco (Zero)**: Não houve alteração na relação matemática entre os cargos.",
        "delta_subtitle": "Valores negativos (Azul) indicam aproximação (ficaram mais similares). Valores positivos (Vermelho) indicam distanciamento.",
        "sub_flow_title": "2.2. Fluxo Normativo (Ganhos e Perdas)",
        "sub_flow_help": "**O que é isso?**\nExibe explicitamente quais atribuições foram adicionadas (ganho), removidas (perda) ou mantidas para a carreira selecionada na transição entre os cenários.",
        "flow_no_career_warning": "💡 Selecione uma 'Carreira para Análise Detalhada' no topo para visualizar o Fluxo Normativo (Ganhos e Perdas).",
        "status_lost": "🔴 Perdeu",
        "status_gained": "🟢 Ganhou",
        "status_maintained": "⚪ Manteve",
        "lbl_yes": "Sim",
        "lbl_no": "Não",
        "flow_filter_label": "Filtrar Status da Atribuição:",
        "flow_no_attr_warning": "Nenhuma atribuição encontrada para esta carreira.",
        "flow_career_not_found": "Carreira não localizada nos dados para comparação direta de atribuições.",
        "sub_radar_title": "2.3. Régua Evolutiva por Cargo (Radar de Afinidade)",
        "sub_radar_help": "**O que é isso?**\nUm gráfico bidimensional que sobrepõe a similaridade do cargo selecionado contra as outras carreiras da polícia nos dois cenários.\n\n**Como ler:**\n- Quanto mais a ponta do radar se esticar para a borda externa, mais as carreiras são **similares**.\n- Se a área laranja (Cenário Alvo) for maior que a ciano (Cenário Base), o cargo selecionado *absorveu* funções e se aproximou das demais carreiras.\n- Se a área encolher, o cargo sofreu um expurgo normativo e isolou-se.",
        "radar_no_career_warning": "💡 Selecione uma 'Carreira para Análise Detalhada' no topo para visualizar o Radar de Afinidade e o Detalhamento Analítico.",
        "radar_hover": "<b>Carreira:</b> %{theta}<br><b>Afinidade Jaccard:</b> %{r:.1%}<extra></extra>",
        "radar_highlight": "Destaque",
        "sub_affinity_title": "#### 2.4. Detalhamento Analítico de Afinidade",
        "sub_affinity_help": "**Como a afinidade é calculada?**\nA Afinidade é calculada matematicamente pelo **Índice de Similaridade de Jaccard**. Ela leva em conta estritamente o que é *COMPARTILHADO E PRESENTE* entre os cargos. Atribuições que **nenhum dos dois** exerce não entram na conta e não aproximam artificialmente os cargos, corrigindo falhas analíticas de matrizes simples. Se Afinidade for `100%`, eles exercem exatamente as mesmas funções em comum.",
        "trend_approached": "🟢 ↗ Aproximou",
        "trend_distanced": "🔴 ↘ Afastou",
        "trend_stable": "⚪ ➡ Estável",
        "col_related_career": "Carreira Relacionada",
        "col_base_affinity": "Afinidade Base",
        "col_new_affinity": "Nova Afinidade",
        "col_delta_var": "Δ Variação",
        "col_trend": "Tendência",
        "affinity_filter_label": "Filtrar Tendência de Afinidade:",
        "sub_network_comp_title": "2.5. Rede de Adjacência Comparativa (Grafo de Similaridade)",
        "sub_network_comp_help": "**O que é isso?**\nExibe as 'teias de aranha' de conexões lado a lado. Se o cenário alvo fragmentou as atribuições, você verá o grafo B mais desconectado ou as linhas mais finas. Se aglutinou, o grafo ficará mais denso e as carreiras mais puxadas para o centro.",
        "network_comp_slider": "Corte de Adjacência Comparativa (Threshold):",
        "network_graph_base": "Grafo Cenário Base",
        "network_graph_target": "Grafo Cenário Alvo",
        "network_details_title": "#### Detalhamento Estrutural da Rede",
        "network_details_caption": "A tabela abaixo contabiliza quantas conexões fortes (acima do corte de {threshold} atribuições em comum) cada carreira formou na teia.",
        "net_more_connected": "🔗 ↗ Mais Conectado",
        "net_less_connected": "✂️ ↘ Menos Conectado",
        "net_stable": "⚪ ➡ Estável",
        "col_conn_base": "Conexões no Grafo ({cenario})",
        "col_conn_var": "Variação (Nº de Arestas)",
        "col_net_impact": "Impacto na Rede",
        "network_filter_label": "Filtrar Impacto na Rede:",
        "sub_tree_comp_title": "2.6. Árvore Hierárquica Comparativa (Dendrograma)",
        "sub_tree_comp_help": "**O que é isso?**\nExibe as estruturas hierárquicas de classificação lado a lado. Você pode avaliar como as carreiras mudaram de 'galhos' na árvore evolutiva entre o Cenário Base e o Cenário Alvo.",
        "tree_graph_base": "Árvore Cenário Base",
        "tree_graph_target": "Árvore Cenário Alvo",
        "tree_details_title": "#### Detalhamento Estrutural da Árvore",
        "tree_details_caption": "A tabela abaixo identifica o vizinho funcional mais próximo de cada carreira na árvore hierárquica (o primeiro 'galho' com quem ela se funde) e verifica se houve salto de ramo metodológico.",
        "branch_jumped": "🌳 🔀 Sim (Saltou)",
        "branch_maintained": "⚪ Não (Manteve)",
        "col_closest_neighbor": "Vizinho Mais Próximo",
        "col_new_neighbor": "Novo Vizinho",
        "col_distance": "Distância",
        "col_branch_change": "Mudança de Ramo?",
        "tree_filter_label": "Filtrar Mudança de Ramo:",
        "tree_warning": "Não há carreiras suficientes para gerar a árvore hierárquica.",        
        # --- GRAFICOS (HOVERS) ---
        "hover_career": "Carreira",
        "hover_assignment": "Atribuição",
        "hover_value": "Valor",
        "hover_career_a": "Carreira A",
        "hover_career_b": "Carreira B",
        "hover_shared_assignments": "Atribuições em Comum",
        "hover_qty_assignments": "Qtd. Atribuições",
        "hover_common": "Comum",
        "hover_force": "Força",
        "hover_gower_dist": "Distância de Gower",
        "hover_mean": "Média",
        "hover_median": "Mediana",
        "hover_represent": "Representatividade",
        "hover_roles_involved": "Cargos Envolvidos",
        "hover_shared_attr": "Atribuições Compartilhadas",
        "used_in_paper": "(usado no artigo)",
        
        "footer_title": "Referências e Contato",
        "footer_ref_title": "Referências do Estudo",
        "footer_ref_desc": "Material para consulta, teste e checagem",
        "footer_repo": "💻 Repositório GitHub",
        "footer_article": "📜 Artigo Científico",
        "footer_data": "📊 Dados Brutos (Zenodo)",
        "footer_contact_title": "Fale com o Autor",
        "footer_contact_desc": "Críticas, sugestões, elogios ou outros",
        "footer_linkedin": "🔗 LinkedIn (Pedro Maia)",
        
        "title_matrix_prefix": "Matriz",
        "title_adj_prefix": "Adjacência",
        "title_gower_prefix": "Matriz de Distância de Gower",
        "col_roles": "Cargo",
        "col_qtd": "Qtd Atribuições",
        "col_rep": "Representatividade (%)",
        "none_text": "Nenhuma",
        "upset_all_roles": "Todos os Cargos",
        "upset_exclusive": "(Exclusiva)",
        "upset_roles_count": "Cargos",
        "upset_more_attr": "... e mais {count} atribuições."
    },
    "EN": {
        "title": "Interactive Dashboard: PCSP Assignments Study (2024)",
        "view_modes": "View Modes:",
        "nav_analytic": "Analytic Navigation:",
        "mode_1": "1. Individual Explorer",
        "mode_2": "2. Scenario Analysis (A x B Comparative)",
        "mode_3": "3. Global Comparison (Macro)",
        "mode_4": "4. Longitudinal Tracking (Micro)",
        "explanation_mode": "📖 Detailed Explanations Mode",
        "reading_tone": "Explanation Tone:",
        "tone_academic": "🔬 Academic / Scientific",
        "tone_layman": "💬 Layman / Simplified",
        "language_selector": "🌐 Idioma / Language",
        
        "config_analytic": "⚙️ Analytic Settings & Controls",
        "select_scenario": "Select Time Scenario:",
        "fast_filter": "Fast Role Filter:",
        "filter_all": "All Civil Police roles",
        "filter_no_cientifica": "Civil Police without Scientific Police roles",
        "filter_only_cientifica": "Only Scientific Police roles",
        "filter_custom": "Custom Selection",
        "include_generic": "Include Generic/Common Assignments",
        "matrix_format": "Matrix Format:",
        "condensed": "Condensed (Agglutinates repetitions)",
        "original": "Original (Raw data)",
        "expand_texts": "Expand texts in tooltips",
        "roles_analyze": "Roles to Analyze:",
        "visual_highlight": "🎨 Visual Highlight (Optional):",
        "config_compare": "⚙️ A x B Comparative Settings",
        "scenario_a": "📌 Scenario A (Base):",
        "scenario_b": "📌 Scenario B (Comparison):",
        "career_detail": "🔎 Select Career for Detailed Analysis:",
        "none_overview": "None (Overview)",
        "highlight_help": "Highlights these careers in charts and tables.",
        "badge_scenario": "⚙️ Scenario:",
        "badge_matrix": "📊 Matrix:",
        "badge_generic": "👥 Generics:",
        "badge_texts": "🏷️ Full Texts:",
        "badge_roles": "🚓 Roles:",
        "badge_mode": "⚙️ Mode:",
        "badge_filtered_careers": "🔍 Filtered Careers:",
        "lbl_condensed": "Condensed",
        "lbl_original": "Original",
        "lbl_on": "ON",
        "lbl_off": "OFF",
        "lbl_selected": "Selected",
        "kpi_orig_title": "Original Assignments",
        "kpi_orig_help": "Total unique assignments extracted from edicts for the selected roles, before agglutinating redundancies.",
        "kpi_cond_title": "Condensed Assignments",
        "kpi_cond_help": "Amount of exclusive columns in the matrix after merging identical assignments common to multiple roles.",
        "kpi_red_title": "Reduction",
        "kpi_red_help": "Absolute difference between original and condensed assignments (amount of noise/redundancy eliminated).",
        "kpi_pct_title": "Reduction Percentage",
        "kpi_pct_help": "Percentage representing the level of normative redundancy overcome by the methodology in this comparison.",
        "expander_math": "ⓘ Active Mathematical Assumption (Condensation Methodology)",
        "expander_math_text": "The matrices below transform lists of textual assignments into numerical coordinates. By passing through **Condensation**, exact repetitions among the same roles become a single column. This prevents an assignment divided into 10 items in the edict (but meaning the same thing) from causing an 'artificial statistical weight' that incorrectly approximates two careers.",
        "sub_matrix": "1.1. Assignments Matrix",
        "sub_matrix_help": "**How to interpret:** Displays the value '1' if the role possesses the normative assignment and '0' if it does not. \n\n**Calculation:** Built by reading the manuals and edicts. In 'Condensed' mode, the matrix agglutinates assignments that have the exact same repetition pattern (e.g., assignments common to a specific group of roles become a single column with weight 1) to prevent documentary redundancies from creating statistical weight distortions.",
        "tip_hover": "💡 <em>Tip: Hover over the cells (colored squares) to read the full normative assignment.</em>",
        "sub_adj": "1.2. Adjacency Matrix (Shared Assignments)",
        "sub_adj_help": "**How to interpret:** Displays the absolute count of how many normative assignments two distinct roles share with each other. Higher values (stronger colors) indicate strong functional juxtaposition.\n\n**Calculation:** Made through the Dot Product crossing the Assignments Matrix against itself (its transpose).",
        "sub_dyn": "1.3. Dynamic Assignments Explorer",
        "sub_dyn_help": "**How to interpret:** Allows manually crossing data simulating the dynamic tables of the original study. Note: In the paper, crossing was limited to 3 careers due to page space constraints, but here the system calculates and confronts all active careers simultaneously.\n\n**Percentages:** Displays the volume of assignments each role represents relative to the total sum of unique assignments in the Civil Police.",
        "warning_bias": "⚠️ SAMPLE BIAS",
        "roles_explanation": "💡 **About Role Titles:** The official titles (*Investigador de Polícia, Perito Criminal*, etc.) are kept in Portuguese to preserve legal integrity and documentary accuracy of the study, as there are no direct equivalent translations for the Brazilian police structure in other cultures.",
        "Atual Sem Correção": "Current (No Correction)",
        "Atual Com Correção": "Current (With Correction)",
        "LONPC Sem Correção": "LONPC (No Correction)",
        "LONPC Com Correção": "LONPC (With Correction)",
        "Reestruturação 2024": "2024 Restructuring",
        "tab_roles": "Role Filter (What do they share?)",
        "tab_assignments": "Assignment Filter (Who does this?)",
        "base_total": "Total Analysis Base:",
        "base_desc": "possible normative assignments in the data matrix.",
        "roles_label": "Roles:",
        "filter_assignments": "Assignments Filter:",
        "op_all": "🌟 Show All",
        "op_excl": "🔸 Only Exclusive to Selection (No outside role does it)",
        "op_comp_out": "🔹 Only Shared (Outside roles also do it)",
        "op_comp_in": "✅ Only Shared (Selected roles)",
        "status_all": "✅ Shared by All",
        "status_excl": "🔸 Exclusive to 1 Role",
        "status_some": "🔹 Shared by Some",
        "norm_weight": "##### Normative Weight (Amount of Assignments per Role)",
        "cross_table": "##### Assignments Crossing Table",
        "select_assignments_desc": "Select one or more assignments to find out which police careers formally have them in their scopes.",
        "assignments_label": "Assignments:",
        "sub_graph": "1.4. Similarity Graph (Adjacency Based)",
        "sub_graph_help": "**How to interpret:** Network representation where 'balls' (nodes) represent police careers and 'lines' (edges) indicate a function intersection. The thickness of the line symbolizes the amount of shared functions.\n\n**Calculation:** Rendered by the NetworkX engine with Fruchterman-Reingold physics (Spring Layout), creating magnetic repulsion forces between nodes, allowing highly connected roles to 'pull' each other to the center of the cluster.",
        "threshold_adj": "Adjacency Cutoff (Connections Threshold):",
        "sub_gower": "1.5. Similarity Heatmap (Gower Distance)",
        "sub_gower_help": "**How to interpret the Map:** Thermal vision of distancing. Red areas represent identical roles (Distance close to 0.0).\n\n**Calculation:** Unlike adjacency (raw count), this uses the Gower Coefficient between 0 and 1, crossing presence (1) and absence (0) arrays, penalizing distortions.",
        "sub_ruler": "1.6. One-Dimensional Affinity Ruler (Gower)",
        "sub_ruler_help": "**How to interpret:** Transforms the complex Gower matrix into a simple Ranking, taking a specific role as 'zero point' and listing the others in order of functional distance.\n\n**Usage:** Excellent to see who is the closest and furthest functionally from the selected career.",
        "select_ruler_role": "📌 Select the Reference Career (Zero Point):",
        "sub_dendro": "1.7. Hierarchical Tree (Dendrogram)",
        "sub_dendro_help": "**How to interpret:** Classifies and groups sub-blocks of careers that have high affinity. If two careers connect further down (further left on the X axes), it means they are functionally very identical and were grouped first at the base.\n\n**Calculation:** Uses Hierarchical Clustering Algorithm on the Gower Matrix metrics. The agglomerative *Single-linkage* method was used, which calculates the minimum distance between members of adjacent groups.",
        "dendro_method": "Hierarchical clustering of Gower distances using the *single* method.",
        "dendro_warning": "Select more than one role to generate the hierarchical tree.",
        "dendro_title": "Gower Dendrogram",
        "sub_upset": "1.8. Set Diagram (Exact Intersections)",
        "sub_upset_help": "**How to interpret:** Works like a scalable 'Venn Diagram'. It scans the hundreds of possible combinations between roles and lists the largest common slices. The bar reveals exactly how many assignments that exclusive 'block' of roles has.\n\n**Why not use a circular Venn Diagram?** Mathematically, circles can only overlap in all permutations for a maximum of 4 sets. Since we have 14 different roles, a Venn would be geometrically impossible to draw without violating spatial laws. This format (UpSet Plot) is the gold standard for multi-layered visualization in Data Science.",
        "upset_title": "Top Normative Intersections (Granular)",
        
        # --- MODO 2: COMPARATIVO A X B ---
        "mode2_tooltip": "Mode 2: Allows comparing the degree of distancing, affinity, and flow of normative functions between police careers in the two temporal scenarios.",
        "badge_scenario_a": "📌 A: ",
        "badge_scenario_b": "📌 B: ",
        "scenario_origin_tooltip": "Origin scenario of the comparison (Where the roles started)",
        "scenario_dest_tooltip": "Destination scenario of the comparison (Where the roles went)",
        "tracking_title": "Tracks the functional gains and losses of a specific career between the two chosen scenarios.",
        "tracking_main": "🔍 Tracking main career:",
        "highlights_lbl": "🎨 Highlights:",
        "warning_diff_scenarios": "Select different scenarios in the Top Panel to compare.",
        "sub_delta_title": "2.1. Gower Similarity Delta ({cenario_a} → {cenario_b})",
        "sub_delta_help": "**What is this?**\nThis mathematical heatmap calculates the exact vectorial difference between the two scenarios.\n\n**How to read:**\n- **Blue (Negative)**: The distance between roles decreased. They became more similar (Agglutination of functions).\n- **Red (Positive)**: The distance increased. They moved apart and became more exclusive/distinct.\n- **White (Zero)**: There was no change in the mathematical relationship between the roles.",
        "delta_subtitle": "Negative values (Blue) indicate approach (became more similar). Positive values (Red) indicate distancing.",
        "sub_flow_title": "2.2. Normative Flow (Gains and Losses)",
        "sub_flow_help": "**What is this?**\nExplicitly displays which assignments were added (gain), removed (loss), or maintained for the selected career in the transition between scenarios.",
        "flow_no_career_warning": "💡 Select a 'Career for Detailed Analysis' at the top to view the Normative Flow (Gains and Losses).",
        "status_lost": "🔴 Lost",
        "status_gained": "🟢 Gained",
        "status_maintained": "⚪ Maintained",
        "lbl_yes": "Yes",
        "lbl_no": "No",
        "flow_filter_label": "Filter Assignment Status:",
        "flow_no_attr_warning": "No assignments found for this career.",
        "flow_career_not_found": "Career not found in the data for direct assignment comparison.",
        "sub_radar_title": "2.3. Career Evolutionary Ruler (Affinity Radar)",
        "sub_radar_help": "**What is this?**\nA two-dimensional chart that overlaps the similarity of the selected role against the other police careers in both scenarios.\n\n**How to read:**\n- The closer the tip of the radar stretches to the outer edge, the more **similar** the careers are.\n- If the orange area (Target Scenario) is larger than the cyan area (Base Scenario), the selected role *absorbed* functions and moved closer to the other careers.\n- If the area shrinks, the role suffered a normative purge and became isolated.",
        "radar_no_career_warning": "💡 Select a 'Career for Detailed Analysis' at the top to view the Affinity Radar and Analytical Detailing.",
        "radar_hover": "<b>Career:</b> %{theta}<br><b>Jaccard Affinity:</b> %{r:.1%}<extra></extra>",
        "radar_highlight": "Highlight",
        "sub_affinity_title": "#### 2.4. Affinity Analytical Detailing",
        "sub_affinity_help": "**How is affinity calculated?**\nAffinity is calculated mathematically by the **Jaccard Similarity Index**. It strictly considers what is *SHARED AND PRESENT* between the roles. Assignments that **neither** of them exercises are not counted and do not artificially approach the roles, correcting analytical flaws of simple matrices. If Affinity is `100%`, they exercise exactly the same functions in common.",
        "trend_approached": "🟢 ↗ Approached",
        "trend_distanced": "🔴 ↘ Distanced",
        "trend_stable": "⚪ ➡ Stable",
        "col_related_career": "Related Career",
        "col_base_affinity": "Base Affinity",
        "col_new_affinity": "New Affinity",
        "col_delta_var": "Δ Variation",
        "col_trend": "Trend",
        "affinity_filter_label": "Filter Affinity Trend:",
        "sub_network_comp_title": "2.5. Comparative Adjacency Network (Similarity Graph)",
        "sub_network_comp_help": "**What is this?**\nDisplays the connection 'cobwebs' side-by-side. If the target scenario fragmented assignments, you will see graph B more disconnected or with thinner lines. If it agglutinated, the graph will become denser and the careers pulled closer to the center.",
        "network_comp_slider": "Comparative Adjacency Cutoff (Threshold):",
        "network_graph_base": "Base Scenario Graph",
        "network_graph_target": "Target Scenario Graph",
        "network_details_title": "#### Network Structural Detailing",
        "network_details_caption": "The table below counts how many strong connections (above the cutoff of {threshold} shared assignments) each career formed in the web.",
        "net_more_connected": "🔗 ↗ More Connected",
        "net_less_connected": "✂️ ↘ Less Connected",
        "net_stable": "⚪ ➡ Stable",
        "col_conn_base": "Graph Connections ({cenario})",
        "col_conn_var": "Variation (Edges Count)",
        "col_net_impact": "Network Impact",
        "network_filter_label": "Filter Network Impact:",
        "sub_tree_comp_title": "2.6. Comparative Hierarchical Tree (Dendrogram)",
        "sub_tree_comp_help": "**What is this?**\nDisplays hierarchical classification structures side-by-side. You can assess how careers changed 'branches' in the evolutionary tree between the Base Scenario and Target Scenario.",
        "tree_graph_base": "Base Scenario Tree",
        "tree_graph_target": "Target Scenario Tree",
        "tree_details_title": "#### Tree Structural Detailing",
        "tree_details_caption": "The table below identifies the closest functional neighbor of each career in the hierarchical tree (the first 'branch' it merges with) and checks if a methodological branch jump occurred.",
        "branch_jumped": "🌳 🔀 Yes (Jumped)",
        "branch_maintained": "⚪ No (Maintained)",
        "col_closest_neighbor": "Closest Neighbor",
        "col_new_neighbor": "New Neighbor",
        "col_distance": "Distance",
        "col_branch_change": "Branch Change?",
        "tree_filter_label": "Filter Branch Change:",
        "tree_warning": "Not enough careers to generate the hierarchical tree.",        
        # --- GRAFICOS (HOVERS) ---
        "hover_career": "Role",
        "hover_assignment": "Assignment",
        "hover_value": "Value",
        "hover_career_a": "Role A",
        "hover_career_b": "Role B",
        "hover_shared_assignments": "Shared Assignments",
        "hover_qty_assignments": "Qty. Assignments",
        "hover_common": "Common",
        "hover_force": "Force",
        "hover_gower_dist": "Gower Distance",
        "hover_mean": "Mean",
        "hover_median": "Median",
        "hover_represent": "Representativeness",
        "hover_roles_involved": "Roles Involved",
        "hover_shared_attr": "Shared Assignments",
        "used_in_paper": "(used in paper)",
        
        "footer_title": "References & Contact",
        "footer_ref_title": "Study References",
        "footer_ref_desc": "Material for reference, testing and validation",
        "footer_repo": "💻 GitHub Repository",
        "footer_article": "📜 Scientific Article",
        "footer_data": "📊 Raw Data (Zenodo)",
        "footer_contact_title": "Contact the Author",
        "footer_contact_desc": "Feedback, suggestions, or questions",
        "footer_linkedin": "🔗 LinkedIn (Pedro Maia)",
        
        "title_matrix_prefix": "Matrix",
        "title_adj_prefix": "Adjacency",
        "title_gower_prefix": "Gower Distance Matrix",
        "title_network": "Careers Network (Adjacency >= {threshold})",
        "col_roles": "Role",
        "col_qtd": "Qty Assignments",
        "col_rep": "Representativeness (%)",
        "none_text": "None",
        "upset_all_roles": "All Roles",
        "upset_exclusive": "(Exclusive)",
        "upset_roles_count": "Roles",
        "upset_more_attr": "... and {count} more assignments."
    }
}

def t(key):
    """
    Retorna a tradução da chave fornecida de acordo com o idioma selecionado no session_state.
    Returns the translation of the provided key according to the selected language in session_state.
    """
    lang = st.session_state.get('language', 'PT-BR')
    return TRANSLATIONS.get(lang, TRANSLATIONS["PT-BR"]).get(key, key)

def t_lang(key, lang):
    """
    Tradução explícita baseada no parâmetro lang.
    """
    return TRANSLATIONS.get(lang, TRANSLATIONS["PT-BR"]).get(key, key)
