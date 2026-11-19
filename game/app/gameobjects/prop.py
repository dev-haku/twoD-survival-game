from __future__ import annotations
import random

from ...package import (
    Gameobject,
    Transform,
    SimpleSpriteRenderer,
    Collider,
)

from ..defs.thing_id import ThingID
from ..defs.schema import EffectType

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..defs.schema import EntityDef, Effect, EffectType

class Prop(Gameobject):

    SCALE = 1
        
    def __init__(self, engine, scene, kwargs) -> None:
        super().__init__(engine, scene, kwargs)

        self.transform: Transform = self.add_component(Transform)
        self.transform.position = kwargs["position"]
        self.transform.scale = (self.SCALE,self.SCALE)
        self.transform.layer = kwargs["layer"]

        self.thing_id: ThingID = kwargs["thing_id"]
        self.entity_def: EntityDef = kwargs["entity_def"]
        
        self.simple_sprite_renderer :SimpleSpriteRenderer = self.add_component(
            component_class= SimpleSpriteRenderer, 
            surface= self.entity_def.sprite.build_surface()
        )

        self.collider: Collider = self.add_component(Collider)
        self.collider.add_hitbox((0,0),(16,16))

        self.max_health = self.entity_def.stats.max_health
        self.health = self.max_health

        self.drop_items = self.entity_def.stats.drop_items

    def attacked(self, effects: tuple[Effect]):

        effect_gameobject = self.parent.generate_entity(ThingID.DAMAGE_EFFECT, self.transform.position.xy, self.transform.layer + 1)
        effect_gameobject.get_component("Transform").scale = self.transform.scale

        for e in effects:
            if e.type == EffectType.DAMAGE:
                self.health -= e.amount
    
    def _drop_items(self):
        for item in self.drop_items:
            for _ in range(item.max_drop_count):
                if random.random() <= item.drop_rate:
                    position = self.transform.position
                    scaled_size = self.simple_sprite_renderer.scaled_size
                    pos = (
                        random.uniform(position.x, position.x + scaled_size[0]),
                        random.uniform(position.y, position.y + scaled_size[1])
                    )
                    self.parent.generate_pickup_item(item.thing_id, pos)

    def update(self):
        if self.health <= 0:
            self._drop_items()
            self.destroy()

        return super().update()


class Tree(Prop):

    SCALE = 3
        
    def __init__(self, engine, scene, kwargs):
        super().__init__(engine, scene, kwargs)

        collider: Collider = self.get_component("Collider")
        collider.clear_all_hitboxes()
        collider.add_hitbox((5,10),(6,6))

class Rock(Prop):

    SCALE = 3
        
    def __init__(self, engine, scene, kwargs):
        super().__init__(engine, scene, kwargs)
        
        collider: Collider = self.get_component("Collider")
        collider.clear_all_hitboxes()
        collider.add_hitbox((0,6),(16,10))



class Fire(Prop):

    SCALE = 3
        
    def __init__(self, engine, scene, kwargs):
        super().__init__(engine, scene, kwargs)