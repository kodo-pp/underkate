from underkate.load_text import load_text
from underkate.scriptlib.common import display_text
from underkate.state import get_state


def find_free_cell(inventory):
    if len(inventory) != 8:
        raise ValueError(f'Invalid size of inventory: {len(inventory)}')
    for i, cell in enumerate(inventory):
        if cell is None:
            return i
    return None


async def buy_item(item: dict, price: int):
    state = get_state()
    if state['player_money'] < price:
        await display_text(load_text('helper/not_enough_money'))
        return
    inventory = state['player_inventory']
    cell_index = find_free_cell(inventory)
    if cell_index is None:
        await display_text(load_text('helper/inventory_full'))
        return
    await display_text(load_text('helper/item_bought', fmt={'item': item['pretty_name2']}))
    inventory[cell_index] = item
    state['player_money'] -= price
