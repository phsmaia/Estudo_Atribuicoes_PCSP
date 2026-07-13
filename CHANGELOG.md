# Changelog

Todas as modificações notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado no [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/).

## [Unreleased] - 2026-07-12

### Added
- **UI/UX Navegação Flutuante**: Inclusão de TOC (Table of Contents) flutuante à direita da tela na Visão Geral (Modo 1) para facilitar o salto entre subseções extensas (`floating_toc.py`).
- **Errata Científica Metodológica**: Inclusão de explicações detalhadas em Português e Inglês, no escopo Técnico e Leigo, explicitando a diferença real entre as métricas de Jaccard e Gower e destacando a discrepância metodológica dos gráficos do artigo publicado (`explanations.py`).

### Changed
- **Desacoplamento Cognitivo de Métricas**: Substituição do menu global de métricas por seletores de Distância e Agrupamento individuais embutidos discretamente abaixo de cada gráfico dependente (Seções 1.5, 1.6 e 1.7), prevenindo vazamento de contexto no fluxo de leitura leigo.
- **Isolamento de Estado de Menu**: Separação estrutural de layout nas gavetas (*popovers*) dos Modos de Visão e Configurações Analíticas, garantindo renderização harmônica com o novo TOC.

### Fixed
- **Anomalia de Renderização de Eixos**: Correção do erro no seletor de Carreira Base da Régua de Afinidade (1.6) que, por distorção matricial, exibia dezenas de atribuições textuais em vez de nomes de cargos.
- **Falhas de Casting do Protobuf (Streamlit)**: Resolução de crashes de UI do Pandas via cast forçado de string pura `[str(x)]` nos seletores de referência.

## [Unreleased] - 2026-07-10
- **Expansão de Traduções (Modos 3 e 4)**: Inclusão completa das chaves de internacionalização da interface, tooltips (ajudas e explicações dos gráficos) e cabeçalhos para os rastreamentos longitudinal e global em inglês (`i18n.py`).
- **Glossários e Ajuda Integrados**: Propagação dos módulos "Brazilian Police Roles Glossary" e "Assignments Translation Table" nos cabeçalhos dos Modos 2 e 4 em ambiente inglês, dispensando a necessidade de retornar ao explorador individual para checar conversões.

### Fixed
- **Vazamentos de Labels em Português no Módulo EN**: Refatoração generalizada da passagem de dados em gráficos longitudinais e nos cabeçalhos e emblemas de sistema (ex: "Viés Amostral", "Configurações de Modo") para acionar chaves de `i18n` em `app.py` e `longitudinal_view.py`.
- **Anomalia de Estado em Multiselects**: Refatoração das caixas de seleção da Visão Comparativa (Fluxo, Afinidade, Rede e Árvore) adotando armazenamento de "chaves-invisíveis" ao invés de strings traduzidas, curando o vazamento e o desaparecimento de dados nas tabelas pós-troca de idioma.
- **Deseleção Indesejada de Menus**: Alteração na lógica dos *Radio Buttons* de Explicações para desacoplar as *labels* dinâmicas (Inglês/Português) da chave de indexação armazenada no `st.session_state`.

## [Unreleased] - 2026-07-09

### Added
- **Suporte a Múltiplos Idiomas (i18n)**: Implementação arquitetural robusta para tradução completa do painel para o Inglês (`i18n.py`).
- **Tradução com Regex Resiliente**: Criação da função `_traduzir_atribuicao_simples` que varre, limpa e padroniza strings brutas (ex: eliminando espaços invisíveis `\xa0` e duplos espaços) garantindo a correspondência no dicionário mesmo com variações no texto original.
- **Função de Escopo Isolado `t_lang`**: Nova sub-rotina de tradução explicitly injetável por parâmetro (`lang`) desenhada para contornar perdas de contexto de sessão do Streamlit no interior de loops do Pandas.

### Fixed
- **Quebra de Tradução na Seção 1.8**: Resolução da falha nas traduções (labels em português vazando em ambiente EN) do Gráfico de Barras UpSet, abandonando a varredura `.get` direta para forçar a passagem na nova engine central.
- **Conflito de Escopo Python/Streamlit**: Contorno definitivo para o bloqueio de cache no carregamento modular do Streamlit causador do erro (TypeError/AttributeError) nas atualizações quentes de arquivos secundários (`visualizations.py`).

## [Unreleased] - 2026-06-29

### Added
- **Explicações Metodológicas Dinâmicas (Modos 3 e 4)**: Implementação de textos de explicação acadêmica e leiga sob demanda (`st.info`) para as seções macroscópicas e para cada etapa do rastreamento longitudinal.
- **Sistema de Testes Automatizados**: Inclusão de testes permanentes com `pytest` focados na biblioteca `data_processing.py` para prevenção de regressões matemáticas (cálculo Gower, Aglutinação e Matriz de Adjacência).
- **Hard Reload Anti-Cache (Streamlit)**: Aplicação de `importlib.reload()` no núcleo (`app.py`) forçando o subsistema a contornar o bloqueio de cache de views modulares (Modos 3 e 4) e componentes textuais compartilhados.

### Changed
- **Aviso de Viés Amostral**: Refatoração do banner de viés (amostra incompleta) para disparar transversalmente entre as abas e seções sempre que a totalidade de carreiras da corporação não for selecionada.
- **Header HTML (Bugfix)**: Higienização do código HTML injetado no Streamlit Markdown Parser, impedindo vazamento de marcações `<div>` causadas por conflitos de sintaxe com linhas em branco.
- **Gestão de Estado em Botões (Toggle)**: Refatoração do estado de seleção de explicações ("Acadêmico/Leigo") no Modo 2, utilizando o rastreador nativo `st.session_state` acoplado via argumento `key` para impedir perdas contextuais.

## [Unreleased] - 2026-06-22

### Added
- **Painel Dinâmico de Destaque Visual**: Injeção de paleta de cores hexadecimais variáveis no mapa de calor de Gower, marcadores em formato de Estrela (⭐) no gráfico Radar e colorização condicional nas tabelas do Modo Comparativo A x B. Inserção de um *badge* rastreador exclusivo fixado ao *Sticky Header*.
- **SAST Automático (Security Tests)**: Implementação permanente do framework `pre-commit` com `bandit` inserido diretamente na esteira de *hooks* do Git. Qualquer vulnerabilidade de segurança bloqueará novos commits automaticamente.
- **Formatação de Fluxo Normativo**: Regras visuais (Pandas Styler) aplicadas na tabela de transição de cargos, destacando em Verde atribuições adquiridas e em Vermelho atribuições revogadas.

### Fixed
- **Vazamento de DOM (Streamlit Markdown Parser Bug)**: Supressão de um erro gráfico nativo do framework onde a ausência de conteúdo de uma variável induzia a motor Markdown a fechar erroneamente as tags, exibindo strings `</div>` na interface do usuário.
- **Caching Memory Block (Streamlit)**: Adição do comando de expurgo `importlib.reload()` no ciclo principal (`app.py`) forçando o subsistema do Python a recompilar a árvore do `comparative_view.py` recém-escrita, prevenindo crashes relacionados ao "TypeError: positional arguments".

## [Unreleased] - 2026-06-04

### Added
- **Filtros Dinâmicos de Tabela (Modo 2)**: Inclusão de `st.multiselect` interativos acima de todas as tabelas analíticas de comparação direta (Ganhos/Perdas, Afinidade, Rede de Adjacência e Hierarquia Dendrográfica) para depuração de tendências específicas.
- **Painel Flutuante (Glassmorphism)**: Transformação completa do cabeçalho estático em um menu interativo fixo flutuante e translúcido.
- **Botão de Redução Dinâmico**: Substituição dos tradicionais expanders Streamlit por um popover moderno para concentrar configurações analíticas em pouco espaço (`st.popover`).
- **Head-Up Display (HUD) de Contatos**: Novo rodapé injetado dinamicamente via JS (`window.parent.document.body`) formatado como "Pílula expansível", anulando interferências de DOM do Streamlit. Com subtítulos explicativos adicionados.
- **Filtros de Exclusividade Algorítmica**: Adição de botões de rádio no Explorador Dinâmico para varredura de atribuições 'Exclusivas', 'Compartilhadas Globalmente' ou 'Compartilhadas Internamente', combinadas com iconografia de status.

### Changed
- **Desativação de Âncora Fixa CSS**: Remoção de hacks avançados de injeção de CSS em `#sticky-header-anchor` visando restaurar o fluxo livre da página e sanar bugs de estabilidade no motor nativo do Streamlit.
- **Otimização Estrutural do Popover (Modo 1)**: Ajuste arquitetural dos controles para design horizontal em 2 camadas de linhas (Cenários/Filtros/Gerais em cima; Destaque Visual e KPIs em baixo) aniquilando barras de rolagem artificiais.
- **UX do Rastreamento Longitudinal (Modo 4)**: Substituição radical da restrita arquitetura de "Abas" (`st.tabs`) por uma fluida rolagem em subseções numeradas (Ex: 4.1 Volume Normativo, 4.2 Atribuições Exclusivas) integradas via `st.markdown`.
- **UX de Análise de Cenários (Modo 2)**: Elevação e encapsulamento dos seletores "Cenário Base (A)" e "Cenário Alvo (B)" diretamente para a engrenagem principal (`st.popover`), promovendo navegação unificada *Cockpit* por toda a aplicação.
- **Segurança Antifraude / Remoção de SMTP**: Remoção drástica do sistema nativo de mensagens integradas (`contact_manager.py`) visando a segurança do autor contra mensagens falsas não-rastreáveis, trocando tudo por conexões estáticas `mailto:` seguras.
- **Otimização de Renderização Visual**: Substituição dos alertas gigantes (`st.info` e `transparency-box`) por textos inline e expanders minimalistas, liberando altura no Viewport para visualização fluída das Matrizes e dos cálculos Gower.
- **Reset State no Explorador Dinâmico**: Modificação da lógica para esvaziar os filtros em transições de cenário, evitando a persistência poluidora de dados entre diferentes arranjos da Polícia Civil.
- **Micro-interações e KPIs**: Reorganização geométrica do seletor *Multiselect* para uso em *full-width* na gaveta e homogeneização de todos os ícones nativos de contexto para "ⓘ" limpo.
- Atualização do `README.md` expurgando credenciais e menções ao formulário de contato anterior.

## [Unreleased] - 2026-06-03

### Added
- **Auditoria de Segurança (SAST/SCA)**: Realizada verificação contra SQL Injection, XSS e vazamento de dependências.
- **Segurança de Dados Locais**: Criação de regras de exclusão no `.gitignore` impedindo versionamento indevido de logs, caches e bancos de dados locais.

### Changed
- **Migração de Banco de Dados**: Refatoração estrutural da aplicação (arquivos `logger.py`, `contact_manager.py` e novo `db.py`) de **SQLite para PostgreSQL**. A arquitetura agora utiliza `psycopg2-binary` e suporta conexões em nuvem para eliminar bloqueios de banco de dados (`database is locked`) sob alta concorrência de usuários no painel interativo.

## [Unreleased] - 2026-06-02

### Added
- **Módulo Explorador Dinâmico**: Nova seção em abas com cruzamentos interativos "Por Cargo" e "Por Atribuição", automatizando verificações do Jupyter Notebook original e provendo selos visuais de status (ex: Exclusiva de 1 cargo).
- **Botões de Ajuda Metodológica**: Adição do parâmetro `help` aos subtítulos gerando pop-ups integrados para explicar como interpretar e os cálculos de cada gráfico.
- **Animações Premium CSS**: Implementação de efeito *Fade & Focus* nas renderizações.
- **Logger LGPD (`logger.py`)**: Desenvolvimento de banco de dados SQLite furtivo no backend focado em métricas e visitações, protegendo a privacidade por meio de Hash unidirecional (SHA-256) aplicado sobre os IPs.
- **Mídia Social e Repositórios**: Inserção de Badges com formatação shields.io nativa apontando para Artigo, Github, Zenodo e LinkedIn na barra lateral.
- **Formulário de Contato Nativo**: Implementação de sistema direto de comunicação na barra lateral, com persistência segura em banco de dados SQLite (`contacts.db`).
- **Engine SMTP para E-mails**: Disparo assíncrono de notificações de contato para o autor alimentado pelo provedor de *secrets* do Streamlit (`secrets.toml`).

### Changed
- **Arquitetura Visual**: Layout do Streamlit transformado em Dashboard Vertical 100% (*wide*), sobrepondo componentes na totalidade do eixo Y.
- **Painel de Controle Central**: Deslocamento da seleção de cenários (Matrizes, Originais) e KPIs de redução dimensional diretamente para a `sidebar`.
- **UX em Matrizes**: Encurtamento do título "Investigador de Polícia (+ Agente de Telecomunicações policial + Agente Policial + Carcereiro Policial)" para "Investigador de Polícia (+ Apoio)" afim de viabilizar leitura ótica das colunas.
- **Ordenação Lógica**: O eixo Y das Matrizes (Atribuição e Adjacência) foi invertido (`autorange="reversed"`) garantindo o topo com o escopo de Delegado de Polícia.
- **UX Dendograma e Gower**: Adicionadas as marcações de Médias, além de caixas numéricas semi-transparentes em cada braço hierárquico informando o peso gravitacional da junção de carreiras.
- **Micro-interações CSS na Barra Lateral**: Achatamento completo de margens, *paddings* e uso intensivo de *Flexbox* e componentes flutuantes (`absolute`) para aniquilar as barras de rolagem nativas e manter os KPIs de Redução (Originais, Condensadas, Redução e Eficácia) em uma malha horizontal perfeita.

### Fixed
- **Erro de Memória de Matriz**: Corrigido `ValueError: underlying array is read-only` decorrente de manipulação matemática de vetores Numpy 2.0+ no Plotly;
- **Refatoração Gráfica**: Corrigido bug grave na ausência do `NetworkX` via injeção direta dos cálculos matemáticos de arestas (Edges) exclusivamente dentro da camada de processamento `data_processing.py`.
- **KeyError do Explorador Dinâmico**: Corrigida a indexação reversa onde a aplicação tentava rastrear siglas (A_01) em um DataFrame já re-composto pelas longas orações normativas originárias.
- **Bug do Iframe (Barras de rolagem artificiais)**: Removidos parâmetros restritivos `width=800` do Python e `transform: rotate` do CSS Global do aplicativo que induziam falha no motor de *Resize Observer* do próprio Streamlit.
- **Índice Nulo no Gower**: Corrigido bug de injeção da pseudo-carreira genérica onde colunas preenchidas com strings (ao invés de números) quebravam a nomeação do Pandas, fazendo a Matriz de Gower cuspir rótulos "0" na renderização visual do Plotly.

## [Unreleased] - 2026-06-01

### Added
- Inicialização do arquivo `CHANGELOG.md` para gerenciamento de continuidade e rastreamento das sessões do projeto, adotando a diretriz do "technical-change-skill".
- Início da Etapa 2: Planejamento arquitetural para conversão dos scripts analíticos em um painel interativo com Streamlit.

### Changed
- Adição de nota explicativa no `README.md` indicando a branch [`scientific-publication`](https://github.com/phsmaia/Estudo_Atribuicoes_PCSP/tree/scientific-publication) (versão estática do artigo) e a branch `main` (atualizações contínuas), em linguagem acessível para leigos.
- Reestruturação completa do arquivo `README.md`:
  - Criação da seção de **Visão Geral** para introdução do projeto a leigos.
  - Separação clara da seção do **Artigo Científico e Scripts Analíticos**, incluindo orientações de execução local.
  - Adição da seção sobre a futura **Aplicação Web Interativa**, sinalizada para implementação posterior.
  - Movimentação e destaque para a **Citação do Zenodo** na área de Referências.
