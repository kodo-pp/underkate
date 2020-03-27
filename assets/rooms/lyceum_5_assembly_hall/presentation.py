from underkate.fight.enemy_battle import load_enemy_battle_by_name
from underkate.global_game import get_game
from underkate.load_text import load_text
from underkate.scriptlib.common import display_text
from underkate.scriptlib.fight import fight
from underkate.state import get_state
from underkate.texture import load_texture
from underkate.textured_sprite import TexturedSprite
from underkate.vector import Vector


async def spawn_water(root):
    water = TexturedSprite(pos=Vector(769, 262), texture=load_texture(root / 'water.png'))
    get_game().overworld.room.spawn(water)


async def main(*, root, **kwargs):
    get_game().overworld.freeze()
    await display_text(load_text('overworld/lyceum_5_assembly_hall/1'))
    await fight(load_enemy_battle_by_name('globby'))
    await display_text(load_text('overworld/lyceum_5_assembly_hall/2'))
    await fight(load_enemy_battle_by_name('algebroid'))
    await fight(load_enemy_battle_by_name('geoma'))
    await display_text(load_text('overworld/lyceum_5_assembly_hall/3'))
    await fight(load_enemy_battle_by_name('crier'), on_before_finish = lambda: spawn_water(root))
    await display_text(load_text('overworld/lyceum_5_assembly_hall/4'))
    get_state()['lyceum_presentation_watched'] = True
    get_game().overworld.unfreeze()
