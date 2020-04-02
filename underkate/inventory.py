from underkate.items.item import Item
from underkate.items.names import get_item_by_name
from underkate.state import get_state

from typing import List, Generator


Inventory = List[str]


def get_inventory() -> Inventory:
    return get_state()['player_inventory']


def enumerate_items(inventory: Inventory) -> Generator[Item, None, None]:
    for cell in inventory:
        yield get_item_by_name(cell)


def give(inventory: Inventory, item: str) -> None:
    inventory.append(item)


def remove_from_slot(inventory: Inventory, slot_index: int) -> None:
    del inventory[slot_index]
