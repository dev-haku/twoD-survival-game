from __future__ import annotations
from dataclasses import dataclass
from enum import StrEnum
import pathlib
import pygame
import functools

from ...paths import APP_ASSET_DIR

@functools.cache
def _load_cache(sheet_path: pathlib.Path) -> pygame.Surface:
    return pygame.image.load(sheet_path).convert_alpha()


class SheetType(StrEnum):
    TILE = "tile"
    ITEM = "item"
    PROP = "prop"
    EFFECT = "effect"

SHEETPATHS: dict[SheetType, pathlib.Path] = {
    SheetType.TILE : APP_ASSET_DIR / "image" / "sprite_sheet" / "tiles.png",
    SheetType.ITEM : APP_ASSET_DIR / "image" / "sprite_sheet" / "items.png",
    SheetType.PROP : APP_ASSET_DIR / "image" / "sprite_sheet" / "props.png",
    SheetType.EFFECT : APP_ASSET_DIR / "image" / "sprite_sheet" / "effects.png"
}

@dataclass(frozen=True)
class Sprite:
    sheet_path: pathlib.Path
    x: int
    y: int
    w: int
    h: int
    
    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(self.x, self.y, self.w, self.h)

    def build_surface(self) -> pygame.Surface:
        return _load_cache(self.sheet_path).subsurface(self.get_rect())
