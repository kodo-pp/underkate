from underkate.game import Game

import os
from pathlib import Path


def main():
    os.chdir(Path(__file__).parent)
    print(os.getcwd())
    with Game() as game:
        game.run()


if __name__ == '__main__':
    main()
