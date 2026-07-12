# Estudo de Atribuições e Similaridades de Cargos da Polícia Civil de São Paulo

## Visão Geral
Este projeto busca mapear, analisar e comparar as atribuições dos diversos cargos da Polícia Civil do Estado de São Paulo (PCSP). Através da análise de dados e técnicas computacionais, identificamos similaridades nas atividades exercidas pelos diferentes cargos. O projeto é dividido em duas partes principais: os estudos analíticos e quantitativos que basearam um artigo científico, e uma futura Aplicação Web interativa para explorar esses dados.

---

## Artigo Científico e Scripts

Esta seção contempla os códigos e análises realizados para o estudo que embasa o artigo científico.

> **Aviso Importante (para não programadores):**
> Se você quer ver os códigos e arquivos exatamente como estavam quando o artigo foi publicado, acesse a versão chamada [`scientific-publication`](https://github.com/phsmaia/Estudo_Atribuicoes_PCSP/tree/scientific-publication). Na programação, chamamos essas versões de *branches*, que funcionam como uma "foto" do projeto congelada no tempo. Já as melhorias e atualizações contínuas do projeto acontecem na versão principal, chamada `main`.

### Como rodar os scripts localmente
- Recomenda-se o uso de **Jupyter Notebook** ou **Google Colab**.
- Siga a ordem dos scripts numéricos (`.ipynb`) na primeira execução para entender o fluxo de geração das tabelas. Posteriormente, podem ser executados livremente, desde que se entenda a lógica das variáveis.
- É necessário instalar as bibliotecas citadas no início de cada script.
- Adicione as tabelas `.csv` (fornecidas no repositório) no diretório de execução para que os códigos consigam ler os dados.
- O mapeamento de atribuições, bem como a geração de tabelas binárias e de adjacências, foram automatizados seguindo a ordem correta dos códigos.

---

## Aplicação Web Interativa (Dashboard)

Para facilitar a exploração dos dados por leigos e gestores, o projeto agora conta com uma **Aplicação Web Interativa** completa, construída em Python (Streamlit).

### Principais Funcionalidades do Painel:
- **Matrizes Interativas**: Heatmaps que expõem as atribuições brutas e compartilhadas entre todos os cargos.
- **Rede de Grafos**: Simulação magnética demonstrando a interligação de afinidade das carreiras.
- **Régua de Gower & Dendograma**: Regimes de similaridade e agrupamentos hierárquicos entre carreiras de referência.
- **Modo Educacional (Acadêmico/Leigo)**: Explicações dinâmicas injetadas ao vivo abaixo de cada gráfico, guiando a leitura metodológica e matemática do sistema.
- **Sistema Anti-Viés**: Emissão automática de alertas de viés estatístico quando uma amostra restrita de cargos gera distorções topológicas.
- **Explorador Dinâmico**: Abas para buscar cruzamentos diretos "Por Cargo" ou "Por Atribuição" sob demanda, contando com filtros algorítmicos de exclusividade global e inter-cargos.

### Como executar o Painel Localmente:
1. Certifique-se de ter o Python instalado.
2. Instale as dependências executando:
   ```bash
   pip install -r requirements.txt
   ```
3. Inicie o servidor do Streamlit:
   ```bash
   python -m streamlit run app.py
   ```
4. (Obrigatório) **Configuração do Banco de Dados**: A aplicação utiliza PostgreSQL para suportar múltiplos acessos simultâneos sem travar. Crie uma pasta `.streamlit` na raiz e adicione o arquivo `secrets.toml` (ou um `.env`) contendo a sua conexão:
   ```toml
   DATABASE_URL = "postgresql://usuario:senha@host:5432/nome_do_banco"
   ```


O painel abrirá automaticamente no seu navegador padrão.

---

## Citação e Referência

Sinta-se à vontade para utilizar a lógica e os códigos para estudos próprios de cargos e instituições, desde que seja feita a devida referência a este repositório.

**Citação (Zenodo)**:
[![DOI](https://zenodo.org/badge/883525251.svg)](https://doi.org/10.5281/zenodo.14284482)

Futuras alterações, acréscimos e dashboards são planejados. Para acompanhar, verifique o histórico de commits.
