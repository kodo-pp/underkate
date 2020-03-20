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


DEFAULTS = {
    'itt_test_tutorial': 'unmet',
    'pacifist_route_possible': True,
    'genocide_route_possible': True,
    'grumpylook_met': False,
    'player_inventory': [
        'logic',
    ],
    'player_hp': 20,
    'player_max_hp': 20,
    'player_money': 5,
    'lyceum_staircase_unlocked': False,
    'lyceum_2_right_fights': {
        'algebroid': False,
        'geoma': False,
        'literallia': False,
    },
    'unlocked_ruler': False,
    'took_ruler': False,
    'grumpylook_met_at_floor2': False,
}


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
    state: dict = {}
    state.update(DEFAULTS)
    set_state(state)
    try:
        with SAVE_PATH.open('r') as f:
            data = json.load(f)
        state.update(data['state'])
        set_state(state)
        game.overworld = Overworld(
            game,
            data['overworld']['room'],
            Vector(*data['overworld']['player_pos']),
        )
    except FileNotFoundError:
        logger.info('File does not exist, loading an empty save')
    except json.decoder.JSONDecodeError:
        logger.error(
            'Save file is corrupt. Loading an empty save, but not overwriting the old file'
        )
    game.current_game_mode = game.overworld


def delete():
    SAVE_PATH.unlink(missing_ok=True)
