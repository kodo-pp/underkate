from underkate.global_game import get_game
from underkate.inventory import give, get_inventory
from underkate.load_text import load_text
from underkate.scriptlib.common import display_text
from underkate.state import get_state


async def main(*a, **k):
    await display_text(load_text('overworld/lyceum_2_geoma/ruler'))
    give(get_inventory(), 'ruler')
    named_objects = get_game().overworld.room.named_objects
    named_objects['ruler'].kill()
    del named_objects['ruler']
    get_state()['took_ruler'] = True
