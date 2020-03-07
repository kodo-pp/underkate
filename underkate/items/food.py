class Food:
    def __init__(self, pretty_name: str, inline_name: str, restores: int):
        self.pretty_name = pretty_name
        self.inline_name = inline_name
        self.restores = restores


    def __str__(self) -> str:
        return self.pretty_name
