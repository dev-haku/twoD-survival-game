from __future__ import annotations
from dataclasses import dataclass
from enum import StrEnum, IntEnum

from src.package.core.gameobject import Gameobject
from src.app.defs.thing_id import ThingID
from src.app.defs.sprite import Sprite


class EffectType(StrEnum):
    HEALTH = "health"
    DAMAGE = "damage"

@dataclass(frozen=True)
class Effect:
    type: EffectType
    amount: int

    @classmethod
    def damage(cls, amount: int) -> "Effect":
        return cls(EffectType.DAMAGE, amount)

    @classmethod
    def health(cls, amount: int) -> "Effect":
        return cls(EffectType.HEALTH, amount)
    
class ActionType(StrEnum):
    ATTACK = "attack"
    EAT = "eat"

@dataclass(frozen=True)
class Action:
    type: ActionType
    effects: tuple[Effect, ...] = ()

    @classmethod
    def eat(cls, *effects: Effect) -> "Action":
        return cls(ActionType.EAT, effects)

    @classmethod
    def attack(cls, *effects: Effect) -> "Action":
        return cls(ActionType.ATTACK, effects)

class MaxAmount(IntEnum):
    ONE = 1
    MEDIUM = 15
    LARGE = 64

@dataclass(frozen=True)
class ItemStats:
    max_amount :MaxAmount= MaxAmount.ONE.value

@dataclass(frozen=True)
class ItemDef:
    sprite: Sprite
    stats: ItemStats
    action: Action | None = None


@dataclass(frozen=True)
class DropItem:
    thing_id: ThingID
    max_drop_count: int
    drop_rate: float

    def __post_init__(self):
        if not (0.0 <= self.drop_rate <= 1.0):
            raise ValueError(f"drop_rate は 0.0〜1.0 が必要です: {self.drop_rate}")
        if self.max_drop_count < 0:
            raise ValueError(f"max_drop_count は0以上が必要です: {self.max_drop_count}")

def drop_items(*drop_items: DropItem) -> tuple[DropItem]:
    return drop_items

@dataclass(frozen=True)
class EntityStats:
    max_health: int = 0
    drop_items: tuple[DropItem] = drop_items()

@dataclass(frozen=True)
class EntityState:
    is_attackable: bool = False
    is_flammable: bool = False

@dataclass(frozen=True)
class EntityDef:
    gameobject_class: type[Gameobject]
    sprite: Sprite
    stats: EntityStats = EntityStats()
    state: EntityState = EntityState()

    def __post_init__(self):
        if not (isinstance(self.gameobject_class, type) and issubclass(self.gameobject_class, Gameobject)):
            raise TypeError(f"Gameobjectのクラスが必要です: {self.gameobject_class!r}")

        if not isinstance(self.sprite, Sprite):
            raise TypeError(f"Sprite が必要です: {self.sprite!r}")

        if not isinstance(self.stats, EntityStats):
            raise TypeError(f"EntityStats が必要です: {self.entity_stats!r}")

        if not isinstance(self.state, EntityState):
            raise TypeError(f"EntityState が必要です: {self.entity_state!r}")


@dataclass(frozen=True)
class ThingDef:
    entity_def: EntityDef | None = None
    item_def: ItemDef | None = None