from ..gameobjects import tile, prop, effect

from .thing_id import ThingID
from .schema import (
    ThingDef,
    EntityDef, EntityStats, EntityState, drop_items, DropItem,
    ItemDef, ItemStats, MaxStackAmount, Action, Effect
)
from .sprite import (
    Sprite, SHEETPATHS, SheetType
)


TILE_SIZE = 16
ITEM_SIZE = 10


THING_DEFS: dict[ThingID, ThingDef] = {
    ThingID.WATER_TILE : ThingDef(
        entity_def= EntityDef(
            gameobject_class=tile.Tile, 
            sprite=Sprite(SHEETPATHS[SheetType.TILE], 16*2, 0, 16, 16)
        )
    ),
    ThingID.STONE_TILE : ThingDef(
        entity_def= EntityDef(
            gameobject_class=tile.Tile, 
            sprite=Sprite(SHEETPATHS[SheetType.TILE], 16*1, 0, 16, 16)
        )
    ),
    ThingID.SAND_TILE : ThingDef(
        entity_def= EntityDef(
            gameobject_class=tile.Tile, 
            sprite=Sprite(SHEETPATHS[SheetType.TILE], 16*3, 0, 16, 16)
        )
    ),
    ThingID.STEPPE_TILE : ThingDef(
        entity_def= EntityDef(
            gameobject_class=tile.Tile, 
            sprite=Sprite(SHEETPATHS[SheetType.TILE], 16*4, 0, 16, 16)
        )
    ),
    ThingID.TUNDRA_TILE : ThingDef(
        entity_def= EntityDef(
            gameobject_class=tile.Tile, 
            sprite=Sprite(SHEETPATHS[SheetType.TILE], 16*6, 0, 16, 16)

        )
    ),
    ThingID.GRASS_TILE : ThingDef(
        entity_def= EntityDef(
            gameobject_class=tile.Tile, 
            sprite=Sprite(SHEETPATHS[SheetType.TILE], 0, 0, 16, 16),
        )
    ),

    ThingID.TREE : ThingDef(
        entity_def= EntityDef(
            gameobject_class=prop.Tree, 
            sprite=Sprite(SHEETPATHS[SheetType.PROP], 0, 0, 16, 16),
            state=EntityState(
                is_attackable=True, 
                is_flammable=True
            ),
            stats=EntityStats(
                max_health=10, 
                drop_items=drop_items(
                    DropItem(thing_id=ThingID.WOOD, max_drop_count=8, drop_rate=1.0),
                    DropItem(thing_id=ThingID.APPLE, max_drop_count=3, drop_rate=0.1),
                )
            )
        )
    ),

    ThingID.ROCK : ThingDef(
        entity_def= EntityDef(
            gameobject_class=prop.Rock, 
            sprite=Sprite(SHEETPATHS[SheetType.PROP], 16, 0, 16, 16),
            state=EntityState(
                is_attackable=True, 
                is_flammable=False
            ),
            stats=EntityStats(
                max_health=10, 
                drop_items=drop_items(
                    DropItem(thing_id=ThingID.STONE, max_drop_count=8, drop_rate=1.0),
                )
            )
        )
    ),

    ThingID.FIRE : ThingDef(
        entity_def= EntityDef(
            gameobject_class= prop.Fire,
            sprite= Sprite(SHEETPATHS[SheetType.PROP], 16, 16*3, 16, 16)
        )
    ),


    ThingID.SLASH_EFFECT : ThingDef(
        entity_def= EntityDef(
            gameobject_class= effect.Slash,
            sprite= Sprite(SHEETPATHS[SheetType.PROP], 0, 16*3, 16, 16)
        )
    ),

    ThingID.DAMAGE_EFFECT : ThingDef(
        entity_def= EntityDef(
            gameobject_class= effect.Damage,
            sprite= Sprite(SHEETPATHS[SheetType.EFFECT], 0, 0, 16, 16)
        )
    ),


    ThingID.APPLE : ThingDef(
        item_def= ItemDef(
            sprite=Sprite(SHEETPATHS[SheetType.ITEM], 0, 0, 10,10),
            stats=ItemStats(MaxStackAmount.LARGE),
            action= Action.eat(Effect.health(1))
        )
    ),

    ThingID.WOOD : ThingDef(
        item_def= ItemDef(
            sprite=Sprite(SHEETPATHS[SheetType.ITEM], 0, 10, 10, 10),
            stats=ItemStats(MaxStackAmount.LARGE)
        )
    ),

    ThingID.STONE : ThingDef(
        item_def= ItemDef(
            sprite=Sprite(SHEETPATHS[SheetType.ITEM], 10, 10, 10, 10),
            stats=ItemStats(MaxStackAmount.LARGE)
        )
    ),
    
    ThingID.WOOD_SWORD : ThingDef(
        item_def= ItemDef(
            sprite=Sprite(SHEETPATHS[SheetType.ITEM], 0, 20, 10, 10),
            stats=ItemStats(MaxStackAmount.SINGLE),
            action= Action.attack(Effect.damage(1))
        )
    ),

}


def validate_thing_defs() -> None:
    for thing_id, thing_def in THING_DEFS.items():
        if thing_def.entity_def is None:
            continue
        for d in thing_def.entity_def.stats.drop_items:
            target = THING_DEFS.get(d.thing_id)
            if target is None:
                raise ValueError(f"{thing_id!r}: ドロップ先 {d.thing_id!r} が THING_DEFS に存在しません")
            if target.item_def is None:
                raise ValueError(f"{thing_id!r}: {d.thing_id!r} はitemのthingIDではありません")

validate_thing_defs()

def validate_item_id(target_thing_id) -> ThingID:
    result = THING_DEFS.get(target_thing_id)
    if result is None:
        raise ValueError(f"{target_thing_id.thing_id!r} はitemのthingIDではありません")

    return target_thing_id

class ThingRegistry:
    def __init__(self, thing_defs: dict[ThingID, ThingDef]):
        self._thing_defs = thing_defs
        self._validate()

    def get_def(self, thing_id: ThingID) -> ThingDef:
        thing_def = self._thing_defs.get(thing_id)
        if thing_def is None:
            raise ValueError(f"{thing_id!r} はthingのThingIDではありません")
        return thing_def

    def get_entity_def(self, thing_id: ThingID) -> EntityDef:
        entity_def = self.get_def(thing_id).entity_def
        if entity_def is None:
            raise ValueError(f"{thing_id!r} はentityのThingIDではありません")
        return entity_def

    def get_item_def(self, thing_id: ThingID) -> ItemDef:
        item_def = self.get_def(thing_id).item_def
        if item_def is None:
            raise ValueError(f"{thing_id!r} はitemのThingIDではありません")
        return item_def

    def _validate(self):
        missing = set(ThingID) - set(self._thing_defs)
        for m in missing:
            print(f"未定義のエンティティ : {m!r}")