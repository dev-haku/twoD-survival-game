from __future__ import annotations
from typing import TYPE_CHECKING

import pygame

from ...paths import APP_ASSET_DIR

from ...package import (
    Gameobject,
    RectTransform,
    SpriteRenderer,
    Text
)

from ..defs.thing_id import ThingID

if TYPE_CHECKING:
    from ..defs.schema import ItemDef
    from ..gameobjects.player import Player


class HealthGauge(Gameobject):
    pass


class Hotbar(Gameobject):

    SLOT_IMAGE_SIZE = (32,32)

    def __init__(self, engine, scene, kwargs):
        super().__init__(engine, scene, kwargs)

        self.rect_transform = self.add_component(RectTransform)
        self.rect_transform.position = kwargs["position"]
        self.rect_transform.scale = kwargs["scale"]
        self.rect_transform.layer = kwargs["layer"]

        self.player: Player = self.scene.get_gameobject("Player")

        self.hotbar_slot_count = self.player.hotbar.MAX_SLOTS

        self.hotbar_surface = pygame.Surface(
            (
                self.SLOT_IMAGE_SIZE[0] * self.hotbar_slot_count, 
                self.SLOT_IMAGE_SIZE[1]
            ),
            pygame.SRCALPHA
        )

        sprite_sheet = pygame.image.load(APP_ASSET_DIR / "image" / "sprite_sheet" / "ui.png").convert_alpha()

        number_rects= [pygame.Rect(16 * x, 16*4 + 16 * y, 16, 16) for y in range(2) for x in range(5)]
        self.number_surfaces = {i : pygame.transform.scale(sprite_sheet.subsurface(number_rects[i]), (self.SLOT_IMAGE_SIZE[0]*0.3,self.SLOT_IMAGE_SIZE[1]*0.3)) for i in range(10)}

        
        slot_sprite_rect = pygame.Rect(0, 16 * 3, 16, 16)
        self.slot_surface = pygame.transform.scale(sprite_sheet.subsurface(slot_sprite_rect), self.SLOT_IMAGE_SIZE)

        self.sprite_renderer = self.add_component(SpriteRenderer)

        self.frame_surface = self._make_frame_surface()

        self.previous_slots = None
        self.previous_selected_slot_index = None

    def _make_frame_surface(self):
        surface = pygame.Surface((self.SLOT_IMAGE_SIZE[0] * 0.9, self.SLOT_IMAGE_SIZE[1] * 0.9), pygame.SRCALPHA)
        surface.fill((255, 255, 0, 255))
        w, h = surface.get_size()
        pygame.draw.rect(
            surface,
            (0, 0, 0, 0),
            pygame.Rect(w*0.1, h*0.1, w*0.9, h*0.9)
        )  
        return surface

    def update(self):

        current_slots = self.player.inventory.get_snapshot()
        current_selected_slot_index = self.player.hotbar.selected_slot_index
        if self.previous_slots != current_slots or self.previous_selected_slot_index != current_selected_slot_index:

            self._reset_hotbar_surface()

            for x in range(self.hotbar_slot_count):
                # Slot SUrface
                self.hotbar_surface.blit(self.slot_surface, (x * self.SLOT_IMAGE_SIZE[0], 0))

                # Item
                item = self.player.hotbar.get_slot(x).item
                if item.thing_id is not None:
                    item_def: ItemDef = self.scene.thing_registry.get_item_def(item.thing_id)
                    item_surface = pygame.transform.scale(item_def.sprite.build_surface(), (self.SLOT_IMAGE_SIZE[0]*0.6, self.SLOT_IMAGE_SIZE[1]*0.6))
                    self.hotbar_surface.blit(item_surface, (x * self.SLOT_IMAGE_SIZE[0] + self.SLOT_IMAGE_SIZE[0]*0.2, self.SLOT_IMAGE_SIZE[1]*0.2))

                    l = len(str(item.amount))
                    for i in range(l):
                        s = self.number_surfaces.get(int(str(item.amount)[i]))
                        self.hotbar_surface.blit(s, (1 + (x * self.SLOT_IMAGE_SIZE[0] + i * s.get_width() + s.get_width() * 0.3), self.SLOT_IMAGE_SIZE[1] - s.get_height() - s.get_height() * 0.5))
                    
                # Selected Frame
                if x == current_selected_slot_index:
                    self.hotbar_surface.blit(self.frame_surface, (x * self.SLOT_IMAGE_SIZE[0]+1,1))
            
            self.sprite_renderer.surface = self.hotbar_surface

            self.previous_slots = current_slots
            self.previous_selected_slot_index = current_selected_slot_index
        
        return super().update()

    def _reset_hotbar_surface(self):
        self.hotbar_surface.fill((0,0,0,0))

        
class Toast(Gameobject):
    pass

class MessageWindow(Gameobject):
    pass

class Inventory(Gameobject):
    pass

class PauseMenu(Gameobject):
    pass

class SettingMenu(Gameobject):
    pass


class PositionDisplay(Text):
    def __init__(self, engine, scene, kwargs):
        super().__init__(engine, scene, kwargs)

    def update(self):
        player = self.scene.get_gameobject("Player")
        player_transform: RectTransform = player.get_component("Transform")

        self.set_text(f"{player_transform.position.x}|{player_transform.position.y}")

        return super().update()

class ChunkPositionDisplay(Text):

    def update(self):
        world = self.scene.get_gameobject("World")
        player_chunk_position = world._get_current_player_chunk_position()

        self.set_text(f"{player_chunk_position[0]}|{player_chunk_position[1]}")
        
        return super().update()