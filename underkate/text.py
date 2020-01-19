from underkate.animated_sprite import AnimatedSprite
from underkate.event_manager import get_event_manager, Subscriber
from underkate.font import Font, load_font
from underkate.global_game import get_game
from underkate.pending_callback_queue import get_pending_callback_queue
from underkate.sprite import Sprite

import json
from pathlib import Path
from typing import List, Callable, Union

import pygame as pg  # type: ignore


SerializedData = Union[str, bytes]


class TextPage(AnimatedSprite):
    def __init__(
        self,
        text: str,
        font: Font,
        delay: float = 0.05,
        skippable: bool = True,
    ):
        super().__init__()
        self.text = text
        self.font = font
        self.delay = delay
        self.skippable = skippable
        self._force_finished = False


    @staticmethod
    def from_dict(d: dict) -> 'TextPage':
        schema = [
            # KEY, TYPE, DEFAULT
            ('text', str, None),
            ('font_name', str, 'default'),
            ('delay', float, 0.05),
            ('skippable', bool, True),
        ]

        values: dict = {}

        for key, required_type, default in schema:
            if key in d and not isinstance(d[key], required_type):
                # Key is present but the value is of a wrong type
                raise TypeError('Failed to deserialize TextPage: invalid data types')
            if key in d:
                values[key] = d[key]
            else:
                values[key] = default

        font = load_font(Path('.') / 'assets' / 'fonts' / values['font_name'])
        return TextPage(values['text'], font=font, delay=values['delay'], skippable=values['skippable'])


    def to_dict(self) -> dict:
        return {
            'text': self.text,
            'font_name': self.font.name,
            'delay': self.delay,
            'skippable': self.skippable,
        }


    def update(self, time_delta: float):
        pass


    def get_current_position(self):
        if self._force_finished:
            return len(self.text)
        elapsed_time = self.get_elapsed_time()
        return int(elapsed_time / self.delay)


    def draw_frame(self, surface: pg.Surface, elapsed_time: float):
        surface.fill((60, 60, 60, 255))
        surface_width, surface_height = surface.get_size()
        glyph_width, glyph_height = self.font.glyph_size
        num_cols = surface_width // glyph_width
        num_rows = surface_height // glyph_height

        index = 0
        x, y = 0, 0
        current_position = self.get_current_position()
        limit = min(current_position, len(self.text))
        while y < num_rows and index < limit:
            while x < num_cols and index < limit:
                char = self.text[index]
                index += 1
                if char == '\n':
                    break
                glyph_name = self.font.get_glyph_name(char)
                source_rect = self.font.get_glyph_rectangle(glyph_name)
                destination_rect = pg.Rect(x * glyph_width, y * glyph_height, glyph_width, glyph_height)
                surface.blit(self.font.image, destination_rect, source_rect)
                x += 1
            x = 0
            y += 1


    def try_force_finish(self):
        if self.skippable:
            self._force_finished = True


    def has_animation_finished(self) -> bool:
        return self.get_current_position() >= len(self.text)


class DisplayedText(Sprite):
    def __init__(self, pages: List[TextPage], game, on_finish: Callable = lambda: None):
        # TODO: get rid of `game` as an argument (and property) and use get_game() instead
        self.pages = pages
        self.page_index = -1
        self.game = game
        self._is_alive = True
        self.on_finish_callback = on_finish


    @staticmethod
    def loads(serialized_data: SerializedData) -> 'DisplayedText':
        data = json.loads(serialized_data)
        return DisplayedText(
            pages = [TextPage.from_dict(d) for d in data['pages']],
            game = get_game(),
        )


    def dumps(self) -> SerializedData:
        return json.dumps({
            'pages': [
                page.to_dict()
                for page in self.pages
            ],
        })


    def draw(self, surface: pg.Surface):
        if self.page_index >= len(self.pages):
            return
        width, height = surface.get_size()
        rect = pg.Rect(0, 3 * height // 4, width, height // 4)
        sub = surface.subsurface(rect)
        self.pages[self.page_index].draw(sub)


    def next(self):
        self.page_index += 1
        if self.page_index >= len(self.pages):
            self.finalize()
            return
        self.pages[self.page_index].start_animation()


    def on_confirm(self, event, arg):
        if not self.is_alive():
            return
        if self.pages[self.page_index].has_animation_finished():
            self.next()
        get_event_manager().subscribe('key:confirm', Subscriber(self.on_confirm))


    def on_cancel(self, event, arg):
        if not self.is_alive():
            return
        self.pages[self.page_index].try_force_finish()
        get_event_manager().subscribe('key:cancel', Subscriber(self.on_cancel))


    def initialize(self):
        self.game.player.disable_controls()
        get_event_manager().subscribe('key:confirm', Subscriber(self.on_confirm))
        get_event_manager().subscribe('key:cancel', Subscriber(self.on_cancel))
        self.next()


    def is_alive(self):
        return self._is_alive


    def finalize(self):
        self.game.player.restore_controls()
        self._is_alive = False
        self.on_finish_callback()


    def is_osd(self):
        return True


    def update(self, time_delta: float):
        pass
