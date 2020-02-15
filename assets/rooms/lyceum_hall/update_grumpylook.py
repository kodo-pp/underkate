from underkate.global_game import get_game
from underkate.state import get_state


async def main(*args, **kwargs):
    if get_state().get('grumpylook_met', False):
        return
    game = get_game()
    room = game.overworld.room
    grumpy = room.named_objects.get('grumpylook')
    if grumpy is None:
        return
    grumpy.pos.y = min(474.0, room.player.pos.y)
