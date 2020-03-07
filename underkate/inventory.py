from underkate.items.item import Item
from underkate.items.names import get_item_by_name
from underkate.state import get_state

from typing import List, Optional, Generator


Inventory = List[Optional[str]]


def get_inventory() -> Inventory:
    return get_state()['player_inventory']


def find_free_cell(inventory: Inventory) -> Optional[int]:
    if len(inventory) != 8:
        raise ValueError(f'Invalid size of inventory: {len(inventory)}')
    for i, cell in enumerate(inventory):
        if cell is None:
            return i
    return None


def enumerate_items(inventory: Inventory) -> Generator[Item, None, None]:
    for cell in inventory:
        if cell is None:
            continue
        yield get_item_by_name(cell)
