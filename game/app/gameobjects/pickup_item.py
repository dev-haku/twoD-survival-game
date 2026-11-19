from __future__ import annotations
import random

from ...package import (
    Gameobject,
    Transform,
    SimpleSpriteRenderer,
    Collider,
)

from ..defs.thing_id import ThingID

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..defs.schema import ItemDef


class PickupItem(Gameobject):
    
    SCALE = 1

    def __init__(self, engine, scene, kwargs) -> None:
        super().__init__(engine, scene, kwargs)

        self.transform: Transform = self.add_component(Transform)
        self.transform.position = kwargs["position"]
        self.transform.scale = (self.SCALE, self.SCALE)
        self.transform.layer = kwargs["layer"]

        self.thing_id: ThingID = kwargs["thing_id"]
        self.item_def: ItemDef = kwargs["item_def"]
        
        self.simple_sprite_renderer = self.add_component(
            component_class= SimpleSpriteRenderer, 
            surface= self.item_def.sprite.build_surface()
        )

        self.collider: Collider = self.add_component(Collider)
        self.collider.add_hitbox((0,0),(10,10))