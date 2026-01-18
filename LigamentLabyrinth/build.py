#AI generated

import PyInstaller.__main__
import os
import shutil

APP_NAME = "LigamentLabyrinth"
ENTRY_POINT = "main.py"

DATA_FILES = [
    ('music', 'music'),
    ('sounds', 'sounds'),
    ('textures', 'textures'),
    ('mapData', 'mapData'),
    ('config.json', '.'),
]

def build():
    if os.path.exists("build"): shutil.rmtree("build")
    if os.path.exists("dist"): shutil.rmtree("dist")

    args = [
        ENTRY_POINT,
        f'--name={APP_NAME}',
        '--onedir',
        '--windowed',
        '--noconfirm',
        '--clean',
    ]

    for src, dest in DATA_FILES:
        # Check if the SOURCE folder exists before trying to add it
        if os.path.exists(src):
            args.append(f'--add-data={src};{dest}')
        else:
            print(f"Warning: Could not find folder '{src}', skipping...")

    print("Building Executable...")
    PyInstaller.__main__.run(args)

    print("Performing Post-Build Copy...")    
    src_config = 'config.json'
    dest_config = os.path.join('dist', APP_NAME, 'config.json')
    
    if os.path.exists(src_config):
        shutil.copy(src_config, dest_config)
        print(f" [OK] Copied {src_config} -> {dest_config}")
    else:
        print(f" [WARN] {src_config} not found! User will start with defaults.")

    print(f"\nBuild complete! Your game is ready in: dist/{APP_NAME}")

if __name__ == "__main__":
    build()