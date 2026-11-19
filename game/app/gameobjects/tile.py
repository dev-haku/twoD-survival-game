from __future__ import annotations

from ...package import (
    Gameobject,
    Transform,
    SimpleSpriteRenderer,
)

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..defs.thing_id import ThingID
    from ..defs.schema import EntityDef

    
class Tile(Gameobject):

    SCALE = 3
        
    def __init__(self, engine, scene, kwargs) -> None:
        super().__init__(engine, scene, kwargs)
        
        transform: Transform = self.add_component(Transform)
        transform.position = kwargs["position"]
        transform.scale = (self.SCALE,self.SCALE)
        transform.layer = kwargs["layer"]

        entity_def: EntityDef = kwargs["entity_def"]

        self.add_component(
            component_class= SimpleSpriteRenderer, 
            surface= entity_def.sprite.build_surface()
        )

    