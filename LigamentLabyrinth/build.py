#AI generated

import PyInstaller.__main__
import os
import shutil

# Project Name
APP_NAME = "LigamentLabyrinth"
ENTRY_POINT = "main.py"

# --- UPDATED DATA FILES ---
# We map your actual folders to the names the code expects.
# (Source Folder on Disk, Destination Folder in EXE)
DATA_FILES = [
    ('music', 'music'),
    ('sounds', 'sounds'),
    ('textures', 'textures'),
    # Add your map files individually since they are in the root
    ('map.txt', '.'),
    ('map_ceiling.txt', '.'),
    ('map_floor.txt', '.'),
]

def build():
    # Clean up previous attempts
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
        if os.path.exists(src):
            args.append(f'--add-data={src};{dest}')
        else:
            print(f"Warning: Could not find {src}, skipping...")

    PyInstaller.__main__.run(args)
    print(f"\nBuild complete! dist/{APP_NAME}")

if __name__ == "__main__":
    build()