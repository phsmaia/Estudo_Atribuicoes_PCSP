import os
import re
import pandas as pd
import numpy as np
import json
try:
    import spacy
except ImportError:
    print("ERRO: A biblioteca 'spacy' não está instalada. Instale com: pip install spacy")
    print("Você também precisará baixar o modelo em português: python -m spacy download pt_core_news_md")
    exit(1)

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import NMF
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, silhouette_samples
from collections import Counter

def parse_raw_texts(filepath):
    """Lê o arquivo Markdown e extrai os textos brutos das atribuições."""
    data = []
    if not os.path.exists(filepath):
        print(f"Arquivo não encontrado: {filepath}")
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
            
        # Cria um identificador único para as matrizes (ex: "Delegado de Polícia (2023)")
        uid = f"{cargo} ({ano})"
            
        data.append({
            "UID": uid,
            "Documento": documento,
            "Cargo": cargo,
            "Ano": ano,
            "Texto_Bruto": text
        })
        
    return pd.DataFrame(data)

def preprocess_text(text, nlp):
    """
    Realiza o processamento inicial: lowercasing, remoção de pontuação,
    stopwords e lematização usando SpaCy.
    """
    doc = nlp(text.lower())
    tokens_lematizados = []
    
    for token in doc:
        # Remove pontuação, espaços em branco e stopwords
        if not token.is_punct and not token.is_space and not token.is_stop:
            # Além disso, remove números se não forem relevantes (opcional, mas recomendado)
            if not token.like_num:
                tokens_lematizados.append(token.lemma_)
                
    return " ".join(tokens_lematizados)

def main():
    print("Iniciando o Processador PLN...")
    
    # 1. Carregar o Modelo SpaCy
    try:
        print("Carregando modelo SpaCy (pt_core_news_md)...")
        nlp = spacy.load("pt_core_news_md")
    except OSError:
        print("ERRO: Modelo 'pt_core_news_md' não encontrado.")
        print("Execute no terminal: python -m spacy download pt_core_news_md")
        return

    # 2. Ler os textos brutos
    df = parse_raw_texts("Texto_Atribuicoes_Bruto.md")
    if df.empty:
        return
        
    print(f"{len(df)} documentos carregados. Iniciando pré-processamento...")
    
    # 3. Limpeza e Lematização
    df['Texto_Processado'] = df['Texto_Bruto'].apply(lambda x: preprocess_text(x, nlp))
    
    # 4. Vetorização TF-IDF (Para Nuvens de Palavras, Similaridade Exata e N-Grams)
    print("Calculando matrizes TF-IDF (com Bigramas, Trigramas, Quartetos e Quintetos)...")
    tfidf_vectorizer = TfidfVectorizer(ngram_range=(1, 5))
    tfidf_matrix = tfidf_vectorizer.fit_transform(df['Texto_Processado'])
    
    # Obter os nomes das palavras (features)
    feature_names = tfidf_vectorizer.get_feature_names_out()
    
    # Exportar todos os N-Grams para um arquivo MD para auditoria (falsos negativos / stopwords)
    print("Exportando a lista completa de N-Grams gerados para 'Todos_NGrams_Gerados.md'...")
    ngrams_dict = {i: [] for i in range(1, 6)}
    for feature in feature_names:
        word_count = feature.count(' ') + 1
        if 1 <= word_count <= 5:
            ngrams_dict[word_count].append(feature)
            
    with open("Todos_NGrams_Gerados.md", "w", encoding='utf-8') as f:
        f.write("# Lista de Todos os N-Grams Gerados pelo TF-IDF\n\n")
        f.write("Este arquivo contém todas as expressões matemáticas geradas para identificar possíveis falsos negativos que deveriam ser adicionados às stopwords.\n\n")
        for i in range(1, 6):
            f.write(f"## {i}-grams\n\n")
            for ngram in sorted(ngrams_dict[i]):
                f.write(f"- {ngram}\n")
            f.write("\n")
    
    # Gerar pesos das palavras para Nuvens de Palavras
    word_weights = {}
    for idx, row in df.iterrows():
        uid = row['UID']
        # Pega a linha da matriz TF-IDF
        row_vector = tfidf_matrix.getrow(idx).toarray()[0]
        # Pegar as top 50 palavras com maior peso
        top_indices = row_vector.argsort()[-50:][::-1]
        top_words = {feature_names[i]: float(row_vector[i]) for i in top_indices if row_vector[i] > 0}
        word_weights[uid] = top_words
        
    # Salvar pesos TF-IDF em JSON
    with open("nlp_tfidf_word_clouds.json", "w", encoding='utf-8') as f:
        json.dump(word_weights, f, ensure_ascii=False, indent=2)
        
    # Extrair Métricas e Salvar
    total_raw_words = sum(len(str(t).split()) for t in df['Texto_Bruto'])
    total_processed_words = sum(len(str(t).split()) for t in df['Texto_Processado'])
    
    # Exemplos interativos (Um para cada documento)
    demo_steps_dict = {}
    for idx, row in df.iterrows():
        uid = row['UID']
        # Pega a primeira frase ou os primeiros 200 caracteres para evitar algo gigante
        texto_curto = row['Texto_Bruto'].split('.')[0] + "."
        if len(texto_curto) > 300:
            texto_curto = texto_curto[:300] + "..."
            
        demo_doc = nlp(texto_curto.lower())
        demo_steps = []
        for t in demo_doc:
            status = "drop" if (t.is_punct or t.is_space or t.is_stop or t.like_num) else "keep"
            demo_steps.append({"word": t.text, "lemma": t.lemma_, "status": status})
            
        demo_steps_dict[uid] = {
            "demo_text": texto_curto,
            "demo_steps": demo_steps
        }
        
    # Palavras globais mais frequentes (Top 500 para permitir filtragem na UI)
    global_weights = np.asarray(tfidf_matrix.sum(axis=0)).flatten()
    top_global_idx = global_weights.argsort()[-500:][::-1]
    top_global_words = {feature_names[i]: float(global_weights[i]) for i in top_global_idx}
    
    # Extração Gramatical Sintática (Noun Chunks) via SpaCy
    print("Extraindo entidades gramaticais sintáticas (Noun Chunks)...")
    chunks_counter = Counter()
    lemma_pos_map = {}
    
    for text in df['Texto_Bruto']:
        doc = nlp(text.lower())
        
        # 1. Extração de Noun Chunks
        for chunk in doc.noun_chunks:
            # Lematiza e limpa as partes do chunk
            chunk_lemma = " ".join([t.lemma_ for t in chunk if not t.is_stop and not t.is_punct and not t.is_space and not t.like_num])
            if len(chunk_lemma.split()) > 1: # Apenas expressões compostas
                chunks_counter[chunk_lemma] += 1
                
        # 2. Mapeamento de Classes Gramaticais (POS Tagging)
        for t in doc:
            if not t.is_stop and not t.is_punct and not t.is_space and not t.like_num:
                if t.lemma_ not in lemma_pos_map:
                    lemma_pos_map[t.lemma_] = t.pos_
                
    top_noun_chunks = dict(chunks_counter.most_common(100))
    
    # 5. Avaliação de Métricas (Clustering K-Means k=5 para Silhouette)
    print("Avaliando métrica matemática (Silhouette Score)...")
    try:
        kmeans = KMeans(n_clusters=5, random_state=42)
        cluster_labels = kmeans.fit_predict(tfidf_matrix)
        sil_score = silhouette_score(tfidf_matrix, cluster_labels)
        sil_samples_tfidf = silhouette_samples(tfidf_matrix, cluster_labels)
        sil_samples_tfidf_dict = {df.iloc[i]['UID']: float(sil_samples_tfidf[i]) for i in range(len(df))}
    except:
        sil_score = 0.0
        sil_samples_tfidf_dict = {}
        
    metrics = {
        "total_raw": int(total_raw_words),
        "total_removed": int(total_raw_words - total_processed_words),
        "total_lemmas": int(len(feature_names)),
        "demo_steps_dict": demo_steps_dict,
        "top_global_words": top_global_words,
        "top_noun_chunks": top_noun_chunks,
        "lemma_pos_map": lemma_pos_map,
        "silhouette_score": float(sil_score),
        "silhouette_samples_tfidf": sil_samples_tfidf_dict
    }
    
    # 6. Modelagem de Tópicos (NMF) para k = 2 até 10
    print("Gerando Modelagem de Tópicos (NMF)...")
    topic_models = {}
    
    for k in range(2, 11):
        nmf_model = NMF(n_components=k, random_state=42, max_iter=500)
        W = nmf_model.fit_transform(tfidf_matrix) # Distribuição Tópico x Documento
        H = nmf_model.components_ # Distribuição Tópico x Palavra
        
        # Normalizar W para que a soma dos tópicos de um doc = 100%
        W_norm = W / (W.sum(axis=1, keepdims=True) + 1e-10)
        
        k_data = {
            "document_topics": {},
            "topic_words": {}
        }
        
        # Para cada tópico, extrair as top 15 palavras
        for topic_idx, topic_weights in enumerate(H):
            top_word_indices = topic_weights.argsort()[-15:][::-1]
            top_words_dict = {feature_names[i]: float(topic_weights[i]) for i in top_word_indices}
            k_data["topic_words"][f"Tópico {topic_idx + 1}"] = top_words_dict
            
        # Para cada documento, salvar sua distribuição de tópicos
        for idx, row in df.iterrows():
            uid = row['UID']
            k_data["document_topics"][uid] = {f"Tópico {i + 1}": float(W_norm[idx][i]) for i in range(k)}
            
        topic_models[str(k)] = k_data
        
    with open("nlp_topics.json", "w", encoding='utf-8') as f:
        json.dump(topic_models, f, ensure_ascii=False, indent=2)
        
    # Similaridade de Cosseno via TF-IDF (Foco na similaridade de palavras exatas)
    cosine_sim_tfidf = cosine_similarity(tfidf_matrix, tfidf_matrix)
    df_sim_tfidf = pd.DataFrame(cosine_sim_tfidf, index=df['UID'], columns=df['UID'])
    df_sim_tfidf.to_csv("nlp_sim_matrix_tfidf.csv")
    
    # 5. Similaridade Semântica via Embeddings do SpaCy (Word2Vec)
    print("Calculando similaridade semântica via Embeddings (SpaCy)...")
    spacy_docs = [nlp(texto) for texto in df['Texto_Processado']]
    n = len(spacy_docs)
    sim_matrix_spacy = np.zeros((n, n))
    
    for i in range(n):
        for j in range(n):
            sim_matrix_spacy[i][j] = spacy_docs[i].similarity(spacy_docs[j])
            
    df_sim_spacy = pd.DataFrame(sim_matrix_spacy, index=df['UID'], columns=df['UID'])
    df_sim_spacy.to_csv("nlp_sim_matrix_spacy.csv")
    
    # 7. Validação Estatística (Mantel Test e Silhouette SpaCy)
    print("Calculando Silhouette Score para SpaCy...")
    try:
        spacy_vectors = [doc.vector for doc in spacy_docs]
        kmeans_spacy = KMeans(n_clusters=5, random_state=42)
        cluster_labels_spacy = kmeans_spacy.fit_predict(spacy_vectors)
        sil_score_spacy = silhouette_score(spacy_vectors, cluster_labels_spacy)
        sil_samples_spacy = silhouette_samples(spacy_vectors, cluster_labels_spacy)
        sil_samples_spacy_dict = {df.iloc[i]['UID']: float(sil_samples_spacy[i]) for i in range(len(df))}
    except:
        sil_score_spacy = 0.0
        sil_samples_spacy_dict = {}
        
    print("Executando Teste de Mantel (1000 permutações)...")
    from scipy.stats import pearsonr, spearmanr
    
    # Extrair os triângulos superiores das matrizes (sem a diagonal)
    idx = np.triu_indices(n, k=1)
    vec_tfidf = cosine_sim_tfidf[idx]
    vec_spacy = sim_matrix_spacy[idx]
    
    r_val, _ = pearsonr(vec_tfidf, vec_spacy)
    spearman_val, _ = spearmanr(vec_tfidf, vec_spacy)
    
    # Permutações do Teste de Mantel
    permutations = 1000
    greater_count = 0
    np.random.seed(42)
    
    for _ in range(permutations):
        perm = np.random.permutation(n)
        permuted_spacy = sim_matrix_spacy[perm, :][:, perm]
        vec_spacy_perm = permuted_spacy[idx]
        r_perm, _ = pearsonr(vec_tfidf, vec_spacy_perm)
        if r_perm >= r_val:
            greater_count += 1
            
    p_value = (greater_count + 1) / (permutations + 1)
    
    metrics["silhouette_score_spacy"] = float(sil_score_spacy)
    metrics["silhouette_samples_spacy"] = sil_samples_spacy_dict
    metrics["mantel_r"] = float(r_val)
    metrics["mantel_p"] = float(p_value)
    metrics["spearman_rho"] = float(spearman_val)
    
    with open("nlp_metrics.json", "w", encoding='utf-8') as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)
    
    print("\nProcessamento concluído com sucesso!")
    print("Arquivos gerados para o aplicativo Streamlit:")
    print("1. nlp_tfidf_word_clouds.json (Pesos das palavras para Nuvem)")
    print("2. nlp_sim_matrix_tfidf.csv (Matriz de Similaridade baseada em palavras exatas)")
    print("3. nlp_sim_matrix_spacy.csv (Matriz de Similaridade baseada em significado/contexto)")
    print("4. nlp_topics.json (Modelos de Tópicos extraídos para k=2 até 10)")
    print("5. Todos_NGrams_Gerados.md (Lista de auditoria para falsos negativos)")

if __name__ == "__main__":
    main()
