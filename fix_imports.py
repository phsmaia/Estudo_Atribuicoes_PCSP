import sys

with open('comparative_view.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for i, line in enumerate(lines):
    stripped = line.strip()
    if stripped == 'import data_processing' and i > 10:
        continue
    if stripped == 'from data_processing import get_cophenetic_comparison_table':
        continue
    new_lines.append(line)

with open('comparative_view.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
