import re

# 1. Update i18n.py
with open('i18n.py', 'r', encoding='utf-8') as f:
    i18n = f.read()

def replace_i18n(content, old_str, new_str):
    return content.replace(old_str, new_str)

# PT-BR
i18n = replace_i18n(i18n, '"mode_1": "1. Explorador Individual"', '"mode_1": "1. Catálogo de Atribuições e Cargos"')
i18n = replace_i18n(i18n, '"mode_2": "2. Análise de Cenários (Comparativo A x B)"', '"mode_2": "2. Explorador Individual"')
i18n = replace_i18n(i18n, '"mode_3": "3. Comparação Global (Macro)"', '"mode_3": "3. Análise de Cenários (Comparativo A x B)"')
i18n = replace_i18n(i18n, '"mode_4": "4. Rastreamento Longitudinal (Micro)"', '"mode_4": "4. Comparação Global (Macro)"')
i18n = replace_i18n(i18n, '"mode_5": "5. Modo Criativo / Interativo"', '"mode_5": "5. Rastreamento Longitudinal (Micro)"')
i18n = replace_i18n(i18n, '"mode_6": "6. Fontes e Princípios"', '"mode_6": "6. Modo Criativo / Interativo"')
i18n = replace_i18n(i18n, '"mode_7": "7. Catálogo de Atribuições e Cargos"', '"mode_7": "7. Fontes e Princípios"')

# EN
i18n = replace_i18n(i18n, '"mode_1": "1. Individual Explorer"', '"mode_1": "1. Assignments & Roles Catalog"')
i18n = replace_i18n(i18n, '"mode_2": "2. Scenario Analysis (A x B Comparative)"', '"mode_2": "2. Individual Explorer"')
i18n = replace_i18n(i18n, '"mode_3": "3. Global Comparison (Macro)"', '"mode_3": "3. Scenario Analysis (A x B Comparative)"')
i18n = replace_i18n(i18n, '"mode_4": "4. Longitudinal Tracking (Micro)"', '"mode_4": "4. Global Comparison (Macro)"')
i18n = replace_i18n(i18n, '"mode_5": "5. Creative / Interactive Mode"', '"mode_5": "5. Longitudinal Tracking (Micro)"')
i18n = replace_i18n(i18n, '"mode_6": "6. Sources and Principles"', '"mode_6": "6. Creative / Interactive Mode"')
i18n = replace_i18n(i18n, '"mode_7": "7. Assignments & Roles Catalog"', '"mode_7": "7. Sources and Principles"')

# Update badges
i18n = replace_i18n(i18n, '"badge_mode_3": "⚙️ Modo: <strong>Comparação Global (Macro)</strong>"', '"badge_mode_3": "⚙️ Modo: <strong>Análise de Cenários (Comparativo A x B)</strong>"')
i18n = replace_i18n(i18n, '"badge_mode_3": "⚙️ Mode: <strong>Global Comparison (Macro)</strong>"', '"badge_mode_3": "⚙️ Mode: <strong>Scenario Analysis (A x B Comparative)</strong>"')

i18n = replace_i18n(i18n, '"badge_mode_4": "⚙️ Modo: <strong>Rastreamento Longitudinal (Micro)</strong>"', '"badge_mode_4": "⚙️ Modo: <strong>Comparação Global (Macro)</strong>"')
i18n = replace_i18n(i18n, '"badge_mode_4": "⚙️ Mode: <strong>Longitudinal Tracking (Micro)</strong>"', '"badge_mode_4": "⚙️ Mode: <strong>Global Comparison (Macro)</strong>"')

with open('i18n.py', 'w', encoding='utf-8') as f:
    f.write(i18n)

# 2. Update app.py conditionals
with open('app.py', 'r', encoding='utf-8') as f:
    app = f.read()

# Replace layout checks
app = app.replace('st.session_state.last_modo_visao not in ["mode_1", "mode_2", "mode_3", "mode_4"]', 'st.session_state.last_modo_visao not in ["mode_2", "mode_3", "mode_4", "mode_5"]')
app = app.replace('for k in ["mode_1", "mode_2", "mode_3", "mode_4"]:', 'for k in ["mode_2", "mode_3", "mode_4", "mode_5"]:')
app = app.replace('st.session_state.modo_visao_radio in ["mode_1", "mode_2", "mode_3", "mode_4"]', 'st.session_state.modo_visao_radio in ["mode_2", "mode_3", "mode_4", "mode_5"]')
app = app.replace('if current_mode_for_layout in ["mode_3", "mode_6", "mode_7"]', 'if current_mode_for_layout in ["mode_4", "mode_7", "mode_1"]')
app = app.replace('is_mode_7 = (modo_visao_key == "mode_7")', 'is_mode_7 = (modo_visao_key == "mode_1")')

# Rename the blocks (this requires a tricky regex or manual string replace)
# Let's replace the string `if modo_visao == i18n.t("mode_X"):`
app = app.replace('if modo_visao == i18n.t("mode_1"):', 'if modo_visao == i18n.t("TEMP_2"):')
app = app.replace('elif modo_visao == i18n.t("mode_2"):', 'elif modo_visao == i18n.t("TEMP_3"):')
app = app.replace('elif modo_visao == i18n.t("mode_3"):', 'elif modo_visao == i18n.t("TEMP_4"):')
app = app.replace('elif modo_visao == i18n.t("mode_4"):', 'elif modo_visao == i18n.t("TEMP_5"):')
app = app.replace('elif modo_visao == i18n.t("mode_5"):', 'elif modo_visao == i18n.t("TEMP_6"):')
app = app.replace('elif modo_visao == i18n.t("mode_6"):', 'elif modo_visao == i18n.t("TEMP_7"):')
app = app.replace('elif modo_visao == i18n.t("mode_7"):', 'elif modo_visao == i18n.t("TEMP_1"):')

# Same for other occurrences
app = app.replace('if modo_visao == i18n.t("mode_2"):', 'if modo_visao == i18n.t("TEMP_3"):')
app = app.replace('if modo_visao == i18n.t("mode_1") and df_cenario', 'if modo_visao == i18n.t("TEMP_2") and df_cenario')

# Replace TEMPs back to mode_X
app = app.replace('TEMP_1', 'mode_1')
app = app.replace('TEMP_2', 'mode_2')
app = app.replace('TEMP_3', 'mode_3')
app = app.replace('TEMP_4', 'mode_4')
app = app.replace('TEMP_5', 'mode_5')
app = app.replace('TEMP_6', 'mode_6')
app = app.replace('TEMP_7', 'mode_7')

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(app)

print("Files updated successfully.")
