from underkate.items.food import Food
from underkate.items.item import Item
from underkate.items.weapon import Weapon

from typing import Dict


def get_item_by_name(item_name: str) -> Item:
    print(item_name)
    mapping: Dict[str, Item] = {
        'candy': Food(
            pretty_name = 'Colorful candy',
            inline_name = 'a colorful candy',
            restores = 11,
        ),
        'logic': Weapon(
            name = 'logic',
            pretty_name = 'Use logic',
            inline_name = 'logic',
        ),
    }
    return mapping[item_name]
