from underkate.fight.enemy_battle import load_enemy_battle_by_name
from underkate.load_text import load_text
from underkate.scriptlib.common import display_text
from underkate.scriptlib.fight import fight


async def main(**kwargs):
    await display_text(load_text('overworld/lyceum_1_sportick/sportick'))
    await fight(load_enemy_battle_by_name('sportick'))
