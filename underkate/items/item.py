from typing import Protocol


class Item(Protocol):
    def __str__(self) -> str:
        ...
    pretty_name: str
    inline_name: str
