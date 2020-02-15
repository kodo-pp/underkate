from underkate.overworld.mode import Overworld
from underkate.state import get_state, set_state
from underkate.vector import Vector

import json
from pathlib import Path
from typing import TYPE_CHECKING

from loguru import logger

if TYPE_CHECKING:
    from underkate.game import Game


SAVE_PATH = Path.home() / '.underkate' / 'save_file.json'


def save(game: 'Game'):
    SAVE_PATH.parent.mkdir(parents=True, exist_ok=True)

    data: dict = {}
    data['overworld'] = game.overworld.to_dict()
    data['state'] = get_state()
    data['pi_approx'] = 3.1415926535
    logger.info('Saving file {}', SAVE_PATH)
    with SAVE_PATH.open('w') as f:
        json.dump(data, f)


def load(game: 'Game'):
    logger.info('Loading file {}', SAVE_PATH)
    try:
        with SAVE_PATH.open('r') as f:
            data = json.load(f)
        set_state(data['state'])
        game.overworld = Overworld(game, data['overworld']['room'], Vector(*data['overworld']['player_pos']))
    except FileNotFoundError:
        logger.info('File does not exist, loading an empty save')
    except json.decoder.JSONDecodeError:
        logger.error('Save file is corrupt. Loading an empty save, but not overwriting the old file')
    game.current_game_mode = game.overworld


def delete():
    SAVE_PATH.unlink(missing_ok=True)
