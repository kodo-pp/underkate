from underkate.final_screen.mode import FinalScreenMode
from underkate.global_game import get_game
from underkate.room_transition import RoomTransitionFadeIn
from underkate.scriptlib.animation import play_animation


async def main(**kwargs):
    get_game().overworld.freeze()
    await play_animation(RoomTransitionFadeIn(size=(800, 600), length=3.0))
    get_game().current_game_mode = FinalScreenMode(get_game())
