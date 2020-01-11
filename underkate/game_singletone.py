from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .game import Game


_game: Optional['Game'] = None


def get_game() -> 'Game':
    global _game
    if _game is None:
        raise ValueError('Current game is None')
    return _game


def set_game(game: 'Game'):
    global _game
    _game = game
