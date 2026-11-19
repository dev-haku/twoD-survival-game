from __future__ import annotations
from dataclasses import dataclass
import pygame

from ...package import (
    Gameobject,
    Component,
    Transform,
    SpriteRenderer, 
    Collider,
)

from ..defs.thing_id import ThingID
from ..defs.schema import ActionType, Effect

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..scenes.game_scene import GameScene
    from ..defs.thing_registry import ThingRegistry


class Player(Gameobject):

    SCALE = 1

    def __init__(self, engine, scene, kwargs):
        super().__init__(engine, scene, kwargs)

        self.scene: GameScene

        position: tuple[float,float] = kwargs["position"]
        layer: int = kwargs["layer"]

        surf = pygame.Surface((16,16))
        surf.fill((255,255,255))
        
        self.transform: Transform = self.add_component(Transform)
        self.sprite_renderer: SpriteRenderer = self.add_component(SpriteRenderer, surface=surf)
        self.collider: Collider = self.add_component(Collider)
        self.add_component(Controller)
        
        self.transform.position = position
        self.transform.scale = (self.SCALE, self.SCALE)
        self.transform.layer = layer

        self.collider.add_hitbox((0,0), self.sprite_renderer.surface.get_size())

        
        self.move_speed = kwargs["move_speed"]
        self.direction = 0
        self.inventory = Inventory(scene.thing_registry)
        self.hotbar = Hotbar(self.inventory)


    def update(self):

        for gameobject in self.collider.get_colliding_gameobjects():
            if gameobject.__class__.__name__ == "PickupItem":
                self.inventory.add_item(gameobject.thing_id)
                gameobject.destroy()  

        scaled_size = self.sprite_renderer.scaled_size
        camera = self.engine.current_scene.get_gameobject("Camera")
        camera_transform = camera.get_component("Transform")
        camera_transform.position = (
            self.transform.position.x + scaled_size[0] * 0.5,
            self.transform.position.y + scaled_size[1] * 0.5
        )
        
        return super().update()

    def action(self):

        selected_hotbar_slot = self.hotbar.selected_slot
        if selected_hotbar_slot.is_empty():
            self._attack((Effect.damage(1),))
            return


        action = self.scene.thing_registry.get_item_def(selected_hotbar_slot.item.thing_id).action
        if action is not None and action == ActionType.ATTACK:
            self._attack(effects= action.effects)
            return

    def _attack(self, effects: tuple[Effect]):

        world = self.scene.get_gameobject("World")

        scaled_size = self.sprite_renderer.scaled_size

        b = {
            0 : (scaled_size[0], 0),
            1 : (0, -scaled_size[1]),
            2 : (-scaled_size[0], 0),
            3 : (0, scaled_size[1]),
        }

        offset_pos = b.get(self.direction)
        pos = (
            self.transform.position.x + offset_pos[0],
            self.transform.position.y + offset_pos[1]
            )
        slash = world.generate_entity(ThingID.SLASH_EFFECT, pos, self.transform.layer)
        slash.set_rotation_angle(self.direction * 90)

        colliding_gameobjects = self._overlap_box_at(
            pos[0], pos[1],
            *self.sprite_renderer.surface.get_size()
        )

        for gameobject in colliding_gameobjects:
            if hasattr(gameobject, "attacked"):
                gameobject.attacked(effects)


    def _overlap_box_at(self, x, y, width, height) -> list[Gameobject]:
        
        self_rect = pygame.Rect(x, y, width, height)

        colliding_gameobjects = []
        for target_gameobject in self.scene.gameobjects:
            target_transform: Transform = target_gameobject.get_component("Transform")
            target_collider: Collider = target_gameobject.get_component("Collider")

            if target_transform is None or target_collider is None:
                continue

            if not target_transform.active or not target_collider.active:
                continue

            target_rects = [
                pygame.Rect(
                    target_transform.position.x + (hitbox.offset_position[0] * target_transform.scale.x),
                    target_transform.position.y + (hitbox.offset_position[1] * target_transform.scale.y),
                    hitbox.size[0] * target_transform.scale.x,
                    hitbox.size[1] * target_transform.scale.y
                ) 
                for hitbox in target_collider.hitboxes
            ]

            if self_rect.collidelist(target_rects) != -1:
                colliding_gameobjects.append(target_gameobject)

        return colliding_gameobjects

    

class Controller(Component):

    def __init__(self, engine, scene, parent, kwargs):
        super().__init__(engine, scene, parent, kwargs)

        self.scene: GameScene
        self.parent :Player

        self.dt = self.engine.delta_time
        self.keys = self.engine.input_status.keys

        self.parent_transform: Transform = self.parent.get_component("Transform")
        self.parent_sprite_renderer: SpriteRenderer = self.parent.get_component("SpriteRenderer")
        self.parent_collider: Collider = self.parent.get_component("Collider")

        self.last_pos = self.parent_transform.position.xy
        self.block: bool = False
    
    def update(self):

        scaled_size = self.parent_sprite_renderer.scaled_size

        a = {
            "w" : 1,
            "d" : 0,
            "s" : 3,
            "a" : 2,
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

        self.parent_transform.position = round(self.parent_transform.position)

        if self.keys.get("space", False) and self.block == False:
            self.block = True
            self.parent.action()

        elif self.keys.get("space", False) == False:
            self.block = False

        for i in range(self.parent.inventory.MAX_SLOTS):
            if self.keys.get(str(i), False):
                self.parent.hotbar.selected_slot_index = i - 1

        return super().update()

class Hotbar:

    MAX_SLOTS = 8

    def __init__(self, inventory):
        self._inventory = inventory
        self._selected_slot_index = 0

    @property
    def selected_slot_index(self) -> int:
        return self._selected_slot_index

    @selected_slot_index.setter
    def selected_slot_index(self, value):
        if value <= self.MAX_SLOTS - 1 and value >= 0:
            self._selected_slot_index = value

    @property
    def selected_slot(self) -> ItemSlot: 
        return self._inventory.slots[self._selected_slot_index]

    def get_slot(self, index) -> ItemSlot:
        return self._inventory.slots[index]

    
class Inventory:

    MAX_SLOTS = 32

    def __init__(self, thing_registry):
        self._slots: list[ItemSlot] = [ItemSlot(thing_registry) for _ in range(self.MAX_SLOTS)]

    @property
    def slots(self):
        return self._slots

    def add_item(self, thing_id: ThingID) -> bool:
        # 1. 同じアイテムで、まだ上限に達していないスロットに足す
        for slot in self._slots:
            if slot.item.thing_id is thing_id and not slot.is_full():
                slot.increment_amount()
                return True

        # 2. 空きスロットに新しくセットする
        for slot in self._slots:
            if slot.is_empty():
                slot.set(thing_id, 1)
                return True

        # 3. 入る場所がない
        return False

    def get_snapshot(self):
        return [(s.item.thing_id, s.item.amount)  for s in self._slots]
    
    
class ItemSlot:
    def __init__(self, thing_registry):
        self._thing_registry: ThingRegistry = thing_registry
        self._item = Item()

    @property
    def item(self):
        return self._item

    def set(self, thing_id: ThingID, amount :int):
        self._item.thing_id = thing_id
        self._item.amount = amount
        self._item.max_stack_amount = self._thing_registry.get_item_def(thing_id).stats.max_stack_amount

    def clear(self):
        self._item.thing_id = None
        self._item.amount = 0
        self._item.max_stack_amount = 0

    def increment_amount(self):
        self._item.amount += 1

    def decrement_amount(self):
        self._item.amount -= 1

    def can_increase_amount(self, amount) -> bool:
        return amount + self._item.amount < self._item.max_stack_amount

    def is_empty(self) -> bool:
        return self._item.thing_id is None and self._item.amount <= 0

    def is_full(self) -> bool:
        return self._item.thing_id is not None and self._item.amount >= self._item.max_stack_amount


@dataclass
class Item:
    _thing_id :ThingID | None = None
    _amount :int = 0
    _max_amount :int = 0

    @property
    def thing_id(self) -> ThingID:
        return self._thing_id

    @property
    def amount(self) -> amount:
        return self._amount

    @thing_id.setter
    def thing_id(self, value: ThingID):
        self._thing_id = value
    
    @amount.setter
    def amount(self, value: int):
        self._amount = value