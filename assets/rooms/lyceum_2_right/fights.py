from underkate.fight.enemy_battle import load_enemy_battle_by_name
from underkate.global_game import get_game
from underkate.scriptlib.fight import fight


async def fight_algebroid(*args, **kwargs):
    get_game().overworld.freeze()
    await fight(load_enemy_battle_by_name('algebroid'))
    get_game().overworld.unfreeze()
