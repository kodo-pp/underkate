from underkate.global_game import get_game
from underkate.load_text import load_text
from underkate.scriptlib.common import display_text


async def main(**kwargs):
    await display_text(load_text('overworld/lyceum_5_assembly_hall/1'))
    await display_text(load_text('overworld/lyceum_5_assembly_hall/2'))
    await display_text(load_text('overworld/lyceum_5_assembly_hall/3'))
