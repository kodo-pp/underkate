from underkate.animated_texture import load_animated_texture
from underkate.fight.enemy_battle import load_enemy_battle_by_name
from underkate.global_game import get_game
from underkate.load_text import load_text
from underkate.scriptlib.common import display_text, sleep
from underkate.scriptlib.fight import fight
from underkate.state import get_state
from underkate.textured_walking_sprite import TexturedWalkingSprite


async def maybe_remove_cariel():
    if get_state()['cariel'] == 'killed':
        room.state['cariel_sprite'].kill()


async def branch_pacifist():
    await display_text(load_text('overworld/lyceum_3_cariel/pacifist'))
    await fight(load_enemy_battle_by_name('cariel'), on_before_finish=maybe_remove_cariel)


async def branch_neutral():
    await display_text(load_text('overworld/lyceum_3_cariel/neutral'))
    await fight(load_enemy_battle_by_name('cariel'), on_before_finish=maybe_remove_cariel)


async def branch_genocide():
    await display_text(load_text('overworld/lyceum_3_cariel/genocide'))
    await fight(load_enemy_battle_by_name('cariel_genocide'), on_before_finish=maybe_remove_cariel)


def respawn_cariel(root, room):
    cariel = TexturedWalkingSprite(
        pos = room.named_objects['cariel'].pos,
        left = load_animated_texture(root / 'cariel' / 'left', scale=2),
        right = load_animated_texture(root / 'cariel' / 'right', scale=2),
        front = load_animated_texture(root / 'cariel' / 'front', scale=2),
        back = load_animated_texture(root / 'cariel' / 'back', scale=2),
        speed = 180,
    )
    room.spawn(cariel)
    room.named_objects['cariel'].kill()
    room.state['cariel_sprite'] = cariel
    return cariel


async def main(*, root, **kwargs):
    overworld = get_game().overworld
    room = overworld.room
    overworld.freeze()

    cariel = respawn_cariel(root, room)
    cariel.direction = 'down'

    await room.player.walk_x(-50)
    await sleep(0.8)
    await cariel.walk_y(room.player.pos.y - cariel.pos.y)
    cariel.direction = 'right'
    await sleep(0.8)

    state = get_state()
    if state['genocide_route_possible']:
        await branch_genocide()
    elif state['pacifist_route_possible']:
        await branch_pacifist()
    else:
        await branch_neutral()

    overworld.unfreeze()
