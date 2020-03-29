from underkate.scriptlib.common import display_text
from underkate.load_text import load_text


async def main(**kwargs):
    await display_text(load_text('overworld/lyceum_1_sportick/sportick'))
