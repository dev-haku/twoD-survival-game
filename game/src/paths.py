from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
print(ROOT)

ASSET_DIR = ROOT / "assets" 

DEFAULT_ICON_IMAGE = ASSET_DIR / "image" / "default_icon.ico"