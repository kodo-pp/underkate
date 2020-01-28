

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
            event, key = await


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
        get_event_manager().subscribe('key:up', Subscriber(lambda *args: self.on_key_up()))


    def on_key_down(self):
        if not self.is_alive():
            return
        self.index = min(self.index + 1, len(self.choices) - 1)
        get_event_manager().subscribe('key:down', Subscriber(lambda *args: self.on_key_down()))


    def is_alive(self):
        return fight_script.current_game_mode is self


    @abstractmethod
    def get_choices(self):
        ...


    def on_choice_made(self, choice):
        get_event_manager().raise_event('choice_made', choice)


