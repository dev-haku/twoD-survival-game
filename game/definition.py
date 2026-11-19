from .app.scenes.title_scene import TitleScene
from .app.scenes.game_scene import GameScene


scenes = [
    TitleScene,
    GameScene,
]

initial_scene_index = 0

global_values = {
    "settings" : None
}

debug = {
    "show_colliders" : False,
    "print_key_events" : False
}