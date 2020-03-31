from pathlib import Path
from typing import Dict, Tuple, Union, cast

import pygame as pg  # type: ignore
import yaml

from loguru import logger
from memoization import cached  # type: ignore


class Font:
    def __init__(
        self,
        name: str,
        image: pg.Surface,
        glyph_size: Tuple[int, int],
        glyph_positions: Dict[str, Tuple[int, int]],
    ):
        self.name = name
        self.image = image
        self.glyph_size = glyph_size
        self._glyph_positions = glyph_positions


    def get_glyph_name(self, character: str) -> str:
        return self._glyph_name_mapping[character]


    def get_glyph_position(self, glyph_name: str) -> Tuple[int, int]:
        y, x = self._glyph_positions[glyph_name]
        return x, y


    def get_glyph_rectangle(self, glyph_name: str) -> pg.Rect:
        x, y = self.get_glyph_position(glyph_name)
        rect = pg.Rect((x * self.glyph_size[0], y * self.glyph_size[1]), self.glyph_size)
        return rect


    _glyph_name_mapping = {
        ' ': 'space',
        '!': 'exclamation_mark',
        '(': 'left_paren',
        ')': 'right_paren',
        ',': 'comma',
        '-': 'hyphen',
        '.': 'period',
        '/': 'slash',
        ':': 'colon',
        ';': 'semicolon',
        '?': 'question_mark',
        '~': 'tilde',
        "'": 'apostrophe',
        '*': 'asterisk',
        '"': 'quotation_mark',
        '[': 'left_bracket',
        ']': 'right_bracket',
        '=': 'equals_sign',

        '0': 'digit_0',
        '1': 'digit_1',
        '2': 'digit_2',
        '3': 'digit_3',
        '4': 'digit_4',
        '5': 'digit_5',
        '6': 'digit_6',
        '7': 'digit_7',
        '8': 'digit_8',
        '9': 'digit_9',

        'A': 'latin_A',
        'B': 'latin_B',
        'C': 'latin_C',
        'D': 'latin_D',
        'E': 'latin_E',
        'F': 'latin_F',
        'G': 'latin_G',
        'H': 'latin_H',
        'I': 'latin_I',
        'J': 'latin_J',
        'K': 'latin_K',
        'L': 'latin_L',
        'M': 'latin_M',
        'N': 'latin_N',
        'O': 'latin_O',
        'P': 'latin_P',
        'Q': 'latin_Q',
        'R': 'latin_R',
        'S': 'latin_S',
        'T': 'latin_T',
        'U': 'latin_U',
        'V': 'latin_V',
        'W': 'latin_W',
        'X': 'latin_X',
        'Y': 'latin_Y',
        'Z': 'latin_Z',

        'a': 'latin_a',
        'b': 'latin_b',
        'c': 'latin_c',
        'd': 'latin_d',
        'e': 'latin_e',
        'f': 'latin_f',
        'g': 'latin_g',
        'h': 'latin_h',
        'i': 'latin_i',
        'j': 'latin_j',
        'k': 'latin_k',
        'l': 'latin_l',
        'm': 'latin_m',
        'n': 'latin_n',
        'o': 'latin_o',
        'p': 'latin_p',
        'q': 'latin_q',
        'r': 'latin_r',
        's': 'latin_s',
        't': 'latin_t',
        'u': 'latin_u',
        'v': 'latin_v',
        'w': 'latin_w',
        'x': 'latin_x',
        'y': 'latin_y',
        'z': 'latin_z',
    }


def prepare_font_image(image: pg.Surface, scale_factor: int) -> pg.Surface:
    try:
        image.lock()
        for y in range(image.get_height()):
            for x in range(image.get_width()):
                r, g, b, a = image.get_at((x, y))
                if (r, g, b, a) == (0, 0, 0, 255):
                    image.set_at((x, y), (255, 255, 255, 255))
                else:
                    image.set_at((x, y), (0, 0, 0, 0))
    finally:
        image.unlock()
    old_width = image.get_width()
    old_height = image.get_height()
    new_width = old_width * scale_factor
    new_height = old_height * scale_factor
    return pg.transform.scale(image, (new_width, new_height))


def find_font(name: str) -> Path:
    return Path('.') / 'assets' / 'fonts' / name


@cached
def load_font(path: Union[str, Path]):
    logger.info('Loading font: {}', path)

    if isinstance(path, str):
        path = Path(path)

    with open(path / 'font.yml') as f:
        data = yaml.safe_load(f)

    font_name = data['name']
    font_image_path = path / cast(str, data['image'])
    font_image = pg.image.load(str(font_image_path))
    scale_factor = cast(int, data['scale'])
    font_image = prepare_font_image(font_image, scale_factor)

    initial_glyph_width, initial_glyph_height = cast(Tuple[int, int], data['glyph_size'])
    glyph_width = initial_glyph_width * scale_factor
    glyph_height = initial_glyph_height * scale_factor

    # Actually, the type does not match exactly, but I don't give a fuck
    name_to_position_mapping = cast(Dict[str, Tuple[int, int]], data['mappings'])

    return Font(font_name, font_image, (glyph_width, glyph_height), name_to_position_mapping)
