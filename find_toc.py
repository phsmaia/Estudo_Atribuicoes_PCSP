with open("app.py", "r", encoding="utf-8") as f:
    lines = f.readlines()
for i, line in enumerate(lines):
    if "render_toc" in line:
        print(f"Line {i+1}: {line.strip()}")
