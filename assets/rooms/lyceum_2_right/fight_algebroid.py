from underkate.fight.enemy_battle import load_enemy_battle_by_name
from underkate.scriptlib.fight import fight


async def fight_algebroid(*args, **kwargs):
    await fight(load_enemy_battle_by_name('algebroid'))
