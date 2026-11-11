import pygame
from constants import WINDOW_WIDTH, WINDOW_HEIGHT, TITLE
from menu import Menu
from game import Game
from level_creator import LevelCreator
from sound import SoundManager


def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption(TITLE)
    sounds = SoundManager()

    while True:
        menu = Menu(screen, sounds)
        choice = menu.run()

        if choice is None or choice == "quit":
            break
        elif choice == "creator":
            creator = LevelCreator(screen, sounds)
            creator.run()
        elif choice.startswith("level:"):
            level_name = choice[len("level:") :]
            game = Game(screen, sounds)
            result = game.play_level(level_name)
            if result == "quit":
                break

    pygame.quit()


if __name__ == "__main__":
    main()
