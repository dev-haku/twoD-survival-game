from __future__ import annotations

from src.package import (
    Gameobject,
    Transform,
    SpriteRenderer,
    SimpleSpriteRenderer,
    Collider,
    Timer,
)

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from game.src.app import thing_defs


class Prop(Gameobject):

    SCALE = 1
        
    def __init__(self, engine, scene, kwargs) -> None:
        super().__init__(engine, scene, kwargs)
        

        self.thing_id: thing_defs.ThingIDs = kwargs["thing_id"]

        transform: Transform = self.add_component(Transform)
        transform.position = kwargs["position"]
        transform.scale = (self.SCALE,self.SCALE)
        transform.layer = kwargs["layer"]
        
        simple_sprite_renderer = self.add_component(
            component_class= SimpleSpriteRenderer, 
            surface= kwargs["surface"]
        )

        collider: Collider = self.add_component(Collider)
        collider.add_hitbox((0,0),(16,16))


        entity_def: thing_defs.EntityDef = kwargs["entity_def"]
        
        self.max_health = entity_def.stats.max_health
        self.health = self.max_health

        self.drop_items = entity_def.stats.drop_items


    def _attacked(self, damage_amount):
        self.health -= 1
        if self.health <= 0:
            self.destroy()


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

class Slash(Prop):

    SCALE = 1
        
    def __init__(self, engine, scene, kwargs):
        super().__init__(engine, scene, kwargs)

        self.remove_component("SimpleSpriteRenderer")
        self.sprite_renderer: SpriteRenderer = self.add_component(SpriteRenderer, surface=kwargs["surface"])

        timer: Timer = self.add_component(Timer)
        timer.add_timer(self.destroy, 0.1)

        self.collider: Collider = self.get_component("Collider")

    def update(self):
        for go in self.collider.get_colliding_gameobjects():
            if hasattr(go, "attacked"):
                go.attacked()
        
        return super().update()

    def set_rotation_angle(self, value):
        self.sprite_renderer.set_rotation_angle(value)

class Fire(Prop):

    SCALE = 3
        
    def __init__(self, engine, scene, kwargs):
        super().__init__(engine, scene, kwargs)