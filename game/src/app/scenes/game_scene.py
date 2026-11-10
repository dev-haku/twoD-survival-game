import pygame

from src.package import Scene
from src.app.gameobjects.player import Player
from src.app.gameobjects.world import World
from src.app.gameobjects.ui import (
    PositionDisplay,
    ChunkPositionDisplay,
    HealthGauge,
    Hotbar
)

from src.app.defs.thing_registry import THING_DEFS, ThingRegistry


class GameScene(Scene):

    def __init__(self, engine):
        super().__init__(engine)

        self.thing_registry = ThingRegistry(THING_DEFS)

        camera = self.get_gameobject("Camera")
        camera.anchor = (0.5,0.5)
        camera.zoom = 1

        
        self.add_gameobject(
            gameobject_class= Player, 
            position= (0,0),
            layer= 2
        )

        self.add_gameobject(
            gameobject_class= World,
        )

        self.add_gameobject(
            gameobject_class= PositionDisplay, 
            position= (0.5,0.1), 
            scale=( 0.5,0.5), 
            layer= 1, 
            text= None, 
            size=100, 
            color= (255,255,255), 
            init_active= True
        )

        self.add_gameobject(
            gameobject_class= ChunkPositionDisplay, 
            position= (0.5,0.2), 
            scale= (0.5,0.5), 
            layer= 1, 
            text= None,
            size= 100, 
            color= (255,255,255), 
            init_active= True
        )

        self.add_gameobject(
            gameobject_class= Hotbar,
            position= (0.5,0.9),
            scale= (3,3),
            layer= 1
        )

