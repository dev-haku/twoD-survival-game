from __future__ import annotations
from dataclasses import dataclass
import pygame

from game.package import (
    Gameobject,
    Component,
    Transform,
    SpriteRenderer, 
    Collider,
)

from game.assets.data.thing_id import ThingID
from game.assets.data.thing_defs import THING_DEFS, validate_item_id, ActionType

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from game.app.gameobjects.world import World


class Player(Gameobject):

    def __init__(self, engine, scene, kwargs):
        super().__init__(engine, scene, kwargs)

        position: tuple[float,float] = kwargs["position"]
        layer: int = kwargs["layer"]
        
        transform = self.add_component(Transform)
        sprite_renderer = self.add_component(SpriteRenderer)
        collider: Collider = self.add_component(Collider)
        
        transform.position = position
        transform.scale = (1,1)
        transform.layer = layer

        surface = pygame.Surface((16,16))
        surface.fill((255,255,255))
        sprite_renderer.set_surface(surface)
        
        collider.add_hitbox((0,0), (16,16), (255,0,0,100))

        self.add_component(Controller)

        self.move_speed = 15
        self.direction = 0

        self.inventory = Inventory()
        self.inventory.add_item(ThingID.WOOD_SWORD)
        self.selected_hotbar_slot_index = 0

    

class Controller(Component):

    def __init__(self, engine, scene, parent, kwargs):
        super().__init__(engine, scene, parent, kwargs)

        self.dt = self.engine.delta_time
        self.keys = self.engine.input_status.keys

        self.parent :Player

        self.parent_transform: Transform = self.parent.get_component("Transform")
        self.parent_collider: Collider = self.parent.get_component("Collider")

        self.last_pos = self.parent_transform.position.xy

        self.block: bool = False
    
    def update(self):
        
        w, h = self.parent.get_component("SpriteRenderer").get_surface().get_size()
        sx, sy = self.parent.get_component("Transform").scale
        scaled_size = (
            w * sx,
            h * sy
        )

        a = {
            "w" : 1,
            "d" : 0,
            "s" : 3,
            "a" : 2,
        }

        b = {
            0 : (scaled_size[0], 0),
            1 : (0, -scaled_size[1]),
            2 : (-scaled_size[0], 0),
            3 : (0, scaled_size[1]),
        }

        m = {
            "w" : (0,-(scaled_size[1] / 2) * self.parent.move_speed * self.dt),
            "s" : (0,(scaled_size[1] / 2) * self.parent.move_speed * self.dt),
            "a" : (-(scaled_size[0] / 2) *self.parent.move_speed * self.dt, 0),
            "d" : ((scaled_size[0] / 2) *self.parent.move_speed * self.dt, 0)
        }

        if self.parent_collider.is_colliding():
            self.parent_transform.position.xy = self.last_pos
        else:
            self.last_pos = self.parent_transform.position.xy

        for key in m:
            if self.keys.get(key, False):
                x, y = m.get(key)
                self.parent_transform.position.x += x
                self.parent_transform.position.y += y

                self.parent.direction = a.get(key)

        if self.keys.get("space", False) and self.block == False:
            self.block = True
            
            selected_hotbar_slot = self.parent.inventory.slots[self.parent.selected_hotbar_slot_index]
            action = THING_DEFS.get(selected_hotbar_slot.get_thing_id()).item_def.action
            if action.type == ActionType.ATTACK:
                offset_pos = b.get(self.parent.direction)
                pos = (
                    self.parent_transform.position.x + offset_pos[0],
                    self.parent_transform.position.y + offset_pos[1]
                )
                slash = self.parent.parent.generate_entity(ThingID.SLASH, pos, self.parent_transform.layer)
                slash.set_rotation_angle(self.parent.direction*90)

        elif self.keys.get("space", False) == False:
            self.block = False
            


        self.parent_transform.position.xy = round(self.parent_transform.position.xy)

        camera = self.engine.current_scene.get_gameobject("Camera")
        camera_transform = camera.get_component("Transform")
        camera_transform.position = (
            self.parent_transform.position.x + scaled_size[0] //2,
            self.parent_transform.position.y + scaled_size[1] //2
            )

        return super().update()


@dataclass
class ItemSlot:
    _thing_id :ThingID | None = None
    _amount :int = 0
    _max_amount :int = 0

    def set(self, thing_id: ThingID, amount :int):
        self._thing_id = validate_item_id(thing_id)
        self._amount = amount
        self._max_amount = THING_DEFS.get(self._thing_id).item_def.stats.max_amount

    def get_thing_id(self) -> ThingID:
        return self._thing_id

    def clear(self):
        self._thing_id = None
        self._amount = 0
        self._max_amount = 0

    def increment_amount(self):
        self._amount += 1

    def decrement_amount(self):
        self._amount -= 1

    def can_increase_amount(self, amount) -> bool:
        return amount + self._amount < self._max_amount

    def is_empty(self) -> bool:
        return self._thing_id is None and self._amount <= 0

    def is_full(self) -> bool:
        return self._thing_id is not None and self._amount >= self._max_amount
            
    
class Inventory:

    MAX_SLOTS = 8 * 4

    def __init__(self):
        self._slots: list[ItemSlot] = [ItemSlot() for _ in range(self.MAX_SLOTS)]

    @property
    def slots(self):
        return self._slots

    def add_item(self, thing_id: ThingID) -> bool:
        # 1. 同じアイテムで、まだ上限に達していないスロットに足す
        for slot in self._slots:
            if slot.get_thing_id() is thing_id and not slot.is_full():
                slot.increment_amount()
                return True

        # 2. 空きスロットに新しくセットする
        for slot in self._slots:
            if slot.is_empty():
                slot.set(thing_id, 1)
                return True

        # 3. 入る場所がない
        return False