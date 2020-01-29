from underkate.font import load_font
from underkate.scriptlib import wait_for_event
from underkate.sprite import Sprite
from underkate.texture import load_texture


class Menu:
    def __init__(self, fight_script):
        self.fight_script = fight_script


    async def choose(self):
        self.index = 0
        self.font = load_font(Path('.') / 'assets' / 'fonts' / 'default')
        self.choices = self.get_choices()
        self.pointer_texture = load_texture(Path('.') / 'assets' / 'fight' / 'pointer.png', scale=2)
        self.fight_script.element = self
        while True:
            _, pygame_event = await wait_for_event('key:any')
            if key == pg.K_UP:
                self.on_key_up()
            if key == pg.K_DOWN:
                self.on_key_down()
            if key in (pg.K_z, pg.K_ENTER, pg.K_SHIFT):
                break
        choice = self.choices[self.index]
        self.fight_script.element = None
        return choice


    def draw(self, destination):
        for i, choice in enumerate(self.choices):
            draw_text(str(choice), font = self.font, x = 200, y = 300 + 40 * i, destination = destination)
        self.pointer_texture.draw(destination, x = 160, y = 300 + 40 * self.index)


    def update(self, time_delta):
        pass


    def on_key_up(self):
        if not self.is_alive():
            return
        self.index = max(self.index - 1, 0)


    def on_key_down(self):
        if not self.is_alive():
            return
        self.index = min(self.index + 1, len(self.choices) - 1)


    def is_alive(self):
        return fight_script.current_game_mode is self


    @abstractmethod
    def get_choices(self):
        ...


class BulletBoard:
    def __init__(self, fight_script):
        self.fight_script = fight_script
        self.board_texture = load_texture(Path('.') / 'assets' / 'textures' / 'bullet_board.png')
        self.brain = load_texture(Path('.') / 'assets' / 'textures' / 'brain.png')
        self.x = 4
        self.y = 4
