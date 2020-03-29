from underkate.global_game import get_game
from underkate.load_text import load_text
from underkate.scriptlib.common import display_text, sleep
from underkate.state import get_state
from underkate.texture import load_texture
from underkate.textured_sprite import TexturedSprite
from underkate.vector import Vector


async def main(*, root, **kwargs):
    overworld = get_game().overworld
    overworld.freeze()
    elevator_open_texture = load_texture(root / 'elevator_open.png')
    elevator_open_sprite = TexturedSprite(pos=Vector(619, 126), texture=elevator_open_texture)
    overworld.room.spawn(elevator_open_sprite)
    await sleep(1)
    await display_text(load_text('overworld/lyceum_5_right/elevator_enter'))
    get_state()['lyceum_elevator_used'] = True
    overworld.load_room('lyceum_1_right')
    overworld.unfreeze()
