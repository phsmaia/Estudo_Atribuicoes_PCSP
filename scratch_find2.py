import sys
with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
for i, line in enumerate(lines):
    if 'st.sidebar' in line and ('radio' in line or 'selectbox' in line or 'expand' in line or 'Visão' in line):
        print(f"{i+1}: {line.strip()}")
