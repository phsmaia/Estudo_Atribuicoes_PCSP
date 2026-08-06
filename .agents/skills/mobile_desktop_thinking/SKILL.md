---
name: mobile-desktop-thinking
description: Instruções de UX e Design Responsivo para garantir que novas implementações de componentes visuais, tabelas e gráficos funcionem perfeitamente em telas de Computador (Desktop) e Celular (Mobile).
---

# Mobile & Desktop Thinking

Ao implementar novas funcionalidades, visualizações de dados, tabelas ou componentes de UI no Streamlit, **obrigatoriamente** planeje e codifique considerando dois contextos de tela: Desktop e Mobile.

A aplicação conta com uma variável global no `session_state` chamada `is_mobile` que indica se o usuário habilitou a visualização simplificada.

## Regras de Implementação

1. **Leitura do Estado Mobile:**
   No início de qualquer função de renderização, sempre recupere o estado do dispositivo:
   ```python
   is_mobile = st.session_state.get("is_mobile", False)
   is_light = st.session_state.get("light_mode", False)
   ```

2. **Substituição de Heatmaps e Matrizes Complexas:**
   Gráficos do tipo `px.imshow` (Heatmaps) ou grafos de rede muito densos são ilegíveis em telas de celular.
   - **Desktop:** Renderize a visualização complexa normalmente.
   - **Mobile (`if is_mobile:`):** Oculte a visualização densa. Exiba um seletor (`st.multiselect`) para o usuário isolar 1 a 3 entidades (cargos, cenários, etc). Em seguida, apresente os dados dessas entidades selecionadas através de **gráficos simples (barras, linhas)** e uma **tabela interativa** (`st.dataframe` com `.style.background_gradient`).

3. **Tabelas HTML Largas:**
   Qualquer tabela HTML customizada deve ser envolvida em um contêiner com rolagem horizontal (Scroll) para evitar a quebra do layout no Mobile:
   ```html
   <div style='overflow-x: auto;'>
       <table class='html-table'>...</table>
   </div>
   ```

4. **Anotações (Textos) em Gráficos Scatter e Line:**
   Em celulares, o usuário não tem o cursor do mouse para dar *hover* nos pontos do gráfico.
   - Sempre que plotar um `px.scatter` ou `px.line` e `is_mobile` for verdadeiro, injete textos flutuantes (`fig.add_annotation`) sobre os pontos.
   - Se houver muitos pontos/linhas, injete as anotações **apenas** nas entidades marcadas como destaque (variável `cargos_destaque` ou similar) para evitar poluição visual severa.

5. **Contraste de Cores (Light/Dark Mode):**
   Textos fixos (como anotações flutuantes) não se ajustam automaticamente se você forçar uma cor.
   Sempre crie uma variável de contraste para fontes customizadas:
   ```python
   txt_color = "black" if is_light else "white"
   # Use txt_color em add_annotation(font=dict(color=txt_color))
   ```

6. **Banners Informativos:**
   Quando uma visualização for drasticamente alterada ou omitida por causa do modo celular, exiba um aviso no topo da seção (usando `st.info`) para avisar o usuário que ele está no "Modo Simplificado (Mobile)".

Ao desenhar novas seções, assuma a postura de um Designer UX/UI e aplique estas heurísticas proativamente.
