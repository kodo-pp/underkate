from underkate.fight.enemy_battle import load_enemy_battle_by_name
from underkate.global_game import get_game
from underkate.load_text import load_text
from underkate.scriptlib.common import display_text
from underkate.scriptlib.fight import fight
from underkate.state import get_state


async def remove_sportick():
    room = get_game().overworld.room
    room.named_objects['sportick'].kill()
    del room.named_objects['sportick']


async def main(**kwargs):
    get_game().overworld.freeze()
    await display_text(load_text('overworld/lyceum_1_sportick/sportick'))
    await fight(load_enemy_battle_by_name('sportick'), on_before_finish=remove_sportick)
    get_state()['sportick_fought'] = True
    get_state()['lyceum_staircase_unlocked'] = True
    get_game().overworld.unfreeze()
