from underkate.fight.enemy_battle import load_enemy_battle_by_name
from underkate.global_game import get_game
from underkate.load_text import load_text
from underkate.scriptlib.common import display_text
from underkate.scriptlib.fight import fight


async def main(**kwargs):
    get_game().overworld.freeze()
    await display_text(load_text('overworld/lyceum_5_assembly_hall/1'))
    await fight(load_enemy_battle_by_name('globby'))
    await display_text(load_text('overworld/lyceum_5_assembly_hall/2'))
    await fight(load_enemy_battle_by_name('algebroid'))
    await fight(load_enemy_battle_by_name('geoma'))
    await display_text(load_text('overworld/lyceum_5_assembly_hall/3'))
    await fight(load_enemy_battle_by_name('crier'))
    get_game().overworld.unfreeze()
