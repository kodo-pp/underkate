from underkate.fight.enemy_battle import load_enemy_battle_by_name
from underkate.global_game import get_game
from underkate.load_text import load_text
from underkate.scriptlib.common import display_text
from underkate.scriptlib.fight import fight


async def main(**kwargs):
    get_game().overworld.freeze()
    await display_text(load_text('overworld/lyceum_1_sportick/sportick'))
    await fight(load_enemy_battle_by_name('sportick'))
    get_game().overworld.unfreeze()
