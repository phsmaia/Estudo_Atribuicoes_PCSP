import os
import shutil

project_dir = r"c:\Users\maiap\OneDrive\Desktop\Desenvolvimento\Estudo_Atribuicoes_PCSP"
assets_dir = os.path.join(project_dir, "assets")

if not os.path.exists(assets_dir):
    os.makedirs(assets_dir)

# Artifacts directory
artifacts_dir = r"C:\Users\maiap\.gemini\antigravity-ide\brain\ae9371df-6c3c-41ab-8af3-b66cfecd9248"

# Images to copy
images = {
    "mascote_coruja.png": "mascot_owl_1786281349179.png",
    "mascote_capivara.png": "mascot_capybara_investigator_1786284816866.png",
    "mascote_cao.png": "mascot_dog_detective_1786284825702.png"
}

for dest_name, src_name in images.items():
    src_path = os.path.join(artifacts_dir, src_name)
    dest_path = os.path.join(assets_dir, dest_name)
    if os.path.exists(src_path):
        shutil.copy2(src_path, dest_path)
        print(f"Copied {src_name} to {dest_name}")
    else:
        print(f"Source file not found: {src_path}")
