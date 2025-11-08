import os
import sys

import main


if __name__ == "__main__":
    os.environ['SDL_VIDEO_CENTERED'] = '1'

    game = main.Game()
    game.run()
