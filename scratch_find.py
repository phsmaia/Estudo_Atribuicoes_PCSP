import sys
with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
for i, line in enumerate(lines):
    if 'st.sidebar' in line or 'st.radio' in line or 'st.selectbox' in line or 'Modo de Vis' in line:
        print(f"{i+1}: {line.strip()}")
