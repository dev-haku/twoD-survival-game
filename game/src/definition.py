from src.app.scenes.title_scene import TitleScene
from src.app.scenes.game_scene import GameScene
from src.app.game_settings import GameSettings


scenes = [
    TitleScene,
    GameScene,
]

initial_scene_index = 0

global_values = {
    "settings" : GameSettings()
}

debug = {
    "show_colliders" : False,
    "print_key_events" : False
}