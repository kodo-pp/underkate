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
        'nonsense': Weapon(
            name = 'nonsense',
            pretty_name = 'Complete nonsense',
            inline_name = 'a nonsense speech',
        ),
        'ruler': Weapon(
            name = 'ruler',
            pretty_name = 'Ruler',
            inline_name = 'a ruler',
        ),
    }
    return mapping[item_name]
