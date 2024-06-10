import importlib.util
import shlex
import subprocess
from pathlib import Path

# Скрипт запуска One-File EXE проекта

if __name__ == "__main__":
    name = "sh(x)cleaner"
    entry_point = "main.py"
    noconsole = True
    icon = "assets/icon.ico"
    assets = {
        "assets/white.png": "./assets/",
        "assets/white.jpg": "./assets/",
        "assets/min.svg": "./assets/",
        "assets/close.svg": "./assets/",
        "assets/Exo2.ttf": "./assets/",
        "assets/icon.ico": "./assets/"
    }
    use_venv = False
    venv_path = "venv"

    # Убеждаемся, что pyinstaller установлен
    try:
        importlib.util.find_spec("pyinstaller")
    except ImportError:
        print("Pyinstaller module not installed")
        exit()

    # Формируем команду сборки
    command = ["pyinstaller", "--onefile", "--clean"]
    if noconsole:
        command.append("--noconsole")

    if use_venv:
        command.extend(["--paths", f"{venv_path}/Lib/site-packages"])

    command.extend(["--icon", str(Path(icon).resolve())])
    for asset, target in assets.items():
        command.extend([
            "--add-data",
            f"{str(Path(asset).resolve())}:{target}"
        ])

    command.extend(["--name", name])
    command.append(str(Path(entry_point).resolve()))

    print(f"Running: {shlex.join(command)}")
    # Собираем
    subprocess.run(command)
