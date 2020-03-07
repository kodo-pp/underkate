class Weapon:
    def __init__(self, name: str, pretty_name: str, inline_name: str):
        self.name = name
        self.pretty_name = pretty_name
        self.inline_name = inline_name


    def __str__(self) -> str:
        return self.pretty_name
