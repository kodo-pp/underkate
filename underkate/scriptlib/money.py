from underkate.load_text import load_text
from underkate.scriptlib.common import display_text
from underkate.state import get_state


async def pay(coins: int):
    get_state()['player_money'] += coins
    await display_text(load_text('helper/got_money', fmt={'coins': str(coins)}))
