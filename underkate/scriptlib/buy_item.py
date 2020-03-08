from underkate.inventory import give, get_inventory
from underkate.load_text import load_text
from underkate.scriptlib.common import display_text
from underkate.state import get_state
from underkate.items.names import get_item_by_name


async def buy_item(item_name: str, price: int):
    item = get_item_by_name(item_name)
    state = get_state()
    if state['player_money'] < price:
        await display_text(load_text('helper/not_enough_money'))
        return
    inventory = get_inventory()
    # TODO: handle the case of full inventory
    await display_text(load_text('helper/item_bought', fmt={'item': item.inline_name}))
    give(inventory, item_name)
    state['player_money'] -= price
