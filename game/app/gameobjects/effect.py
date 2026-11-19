from __future__ import annotations

from ...package import (
    Gameobject,
    Transform,
    SpriteRenderer,
    Timer,
)

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..defs.thing_id import ThingID
    from ..defs.schema import EntityDef


class Effect(Gameobject):

    SCALE = 1
        
    def __init__(self, engine, scene, kwargs):
        super().__init__(engine, scene, kwargs)
        
        transform: Transform = self.add_component(Transform)
        transform.position = kwargs["position"]
        transform.scale = (self.SCALE,self.SCALE)
        transform.layer = kwargs["layer"]

        self.thing_id: ThingID = kwargs["thing_id"]
        entity_def :EntityDef = self.scene.thing_registry.get_entity_def(self.thing_id)

        self.sprite_renderer: SpriteRenderer = self.add_component(SpriteRenderer, surface=  entity_def.sprite.build_surface())


class Slash(Effect):

    SCALE = 1
        
    def __init__(self, engine, scene, kwargs):
        super().__init__(engine, scene, kwargs)

        timer: Timer = self.add_component(Timer)
        timer.add_timer(self.destroy, 0.1)

    def set_rotation_angle(self, value):
        self.sprite_renderer.set_rotation_angle(value)


class Damage(Effect):

    SCALE = 1
        
    def __init__(self, engine, scene, kwargs):
        super().__init__(engine, scene, kwargs)

        timer: Timer = self.add_component(Timer)
        timer.add_timer(self.destroy, 0.5)