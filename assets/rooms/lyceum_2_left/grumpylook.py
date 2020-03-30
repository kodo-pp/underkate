from underkate.animated_texture import AnimatedTexture
from underkate.global_game import get_game
from underkate.load_text import load_text
from underkate.script import RoomScript
from underkate.scriptlib.common import display_text, sleep
from underkate.scriptlib.gather import gather
from underkate.state import get_state
from underkate.texture import load_texture
from underkate.textured_walking_sprite import TexturedWalkingSprite


async def main(root, **kwargs):
    overworld = get_game().overworld
    overworld.freeze()

    await display_text(load_text('overworld/lyceum_2_left/grumpylook'))

    room = overworld.room

    grumpylook_object = room.named_objects['grumpylook']
    pos = grumpylook_object.pos
    grumpylook_object.kill()
    del grumpylook_object

    player = room.player
    texture = AnimatedTexture([load_texture(root / 'grumpylook' / 'overworld.png')], fps=1)
    grumpylook = TexturedWalkingSprite(
        pos = pos,
        left = texture,
        right = texture,
        front = texture,
        back = texture,
        speed = player.speed,
    )
    room.spawn(grumpylook)

    await gather(grumpylook.walk_x(-240), player.walk_x(-240))
    get_state()['grumpylook_met_at_floor2'] = True
    overworld.load_room('lyceum_5_left')
    overworld.unfreeze()
