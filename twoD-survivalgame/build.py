import os
import sys
import subprocess
import datetime
import pathlib
import json

from game import paths


with open(paths.GAME_CONFIG, "r") as f:
    game_config = json.load(f)

_name = game_config["name"]
_version = game_config["version"]
_icon_image_path = pathlib.Path("game") / pathlib.Path(game_config["icon_image_path"])

ROOT = pathlib.Path(__file__).resolve().parent
DIR_NAME = datetime.datetime.now().strftime(f"{_name}_v{_version}_%Y%m%d_%H%M%S")

BUILD_ROOT = pathlib.Path(__file__).resolve().parent.parent / "build" / "win" / DIR_NAME
BUILD_ROOT.mkdir(parents=True, exist_ok=True)


spec_file = BUILD_ROOT / f"{_name}.spec"
if spec_file.exists():
    spec_file.unlink()

sep = os.pathsep  # Windows: ";"  /  Mac・Linux: ":"

cmd = [
    sys.executable, "-m", "PyInstaller",
    "--onedir",
    "--contents-directory", ".",
    "--noconsole",
    "--name",        _name,
    "--icon",        str((ROOT / _icon_image_path).resolve()),
    "--add-data",    f"{ROOT / 'game'/'config.json'}{sep}game",
    "--add-data",    f"{ROOT / 'game' / 'assets'}{sep}game/assets",
    "--distpath",    str(BUILD_ROOT / "dist"),
    "--workpath",    str(BUILD_ROOT / "build"),
    "--specpath",    str(BUILD_ROOT),
    str((ROOT / "main.py").resolve()),
]

subprocess.run(cmd)