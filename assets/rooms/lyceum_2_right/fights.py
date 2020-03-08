from underkate.fight.enemy_battle import load_enemy_battle_by_name
from underkate.global_game import get_game
from underkate.scriptlib.fight import fight
from underkate.state import get_state


def make_fight(name):
    async def fight_coroutine(*args, **kwargs):
        get_game().overworld.freeze()
        await fight(load_enemy_battle_by_name(name))
        get_state()['lyceum_2_right_fights'][name] = True
        get_game().overworld.unfreeze()

    fight_coroutine.__name__ = f'fight_{name}'
    return fight_coroutine


fight_algebroid = make_fight('algebroid')
fight_geoma = make_fight('geoma')
fight_literallia = make_fight('literallia')
