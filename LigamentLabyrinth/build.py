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

    PyInstaller.__main__.run(args)
    print(f"\nBuild complete! dist/{APP_NAME}")

if __name__ == "__main__":
    build()