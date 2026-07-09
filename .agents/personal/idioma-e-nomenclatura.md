# Idioma e Nomenclatura do Projeto

Esta regra define o padrão bilíngue do nosso projeto. O objetivo é maximizar a performance da Inteligência Artificial na escrita da lógica, enquanto garantimos que a interface suporte internacionalização.

## 1. Regra Estrutural (Lógica em Inglês)
Para garantir a melhor qualidade de geração de código, aderência a padrões de software e eficiência dos Modelos de Linguagem (LLMs):
- **Nomes de Variáveis, Constantes, Funções e Classes:** Devem ser sempre escritos em Inglês (ex: `user_age`, `def fetch_data():`).
- **Lógica e Nomes Internos de Dicionários/Schemas:** Inglês, para evitar problemas de acentuação e traduções ambíguas no código estrutural.

## 2. Textos e Documentação (Português BR)
O que é lido por humanos no código ou no repositório deve ser em Português do Brasil:
- **Comentários de código e Docstrings:** Devem ser explicativos e em Português.
- **Documentação:** Arquivos Markdown, README, regras de Agentes, etc.

## 3. Internacionalização da Interface (i18n) e Textos Visuais
O painel Streamlit possui sistema de internacionalização (Português e Inglês).
- **Regra de Ouro para Novas Adições:** A cada adição feita ao projeto que não seja código estrutural (ou seja, explicações, textos em visuais, tooltips e mensagens na UI), o conteúdo DEVE ser criado obrigatoriamente para ambos os idiomas: **Português (Default)** e **Inglês**.
- Todos os textos voltados ao usuário (User-Facing) exibidos na tela devem passar pelo sistema de internacionalização (`i18n.py` ou equivalentes).
- Ao atualizar ou criar novas páginas/módulos, não 'engesse' strings na UI. Use a função de tradução: `i18n.t("chave_do_texto")` ou passe a variável de idioma para as funções que geram os textos dinamicamente.
