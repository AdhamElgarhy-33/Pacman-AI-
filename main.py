"""
main.py
-------
Entry point of the Pac-Man AI project.

Run from VS Code's terminal:
    pip install pygame
    python main.py

Controls:
    Arrow keys  - move Pac-Man
    ENTER/SPACE - start the game / advance to the next level / restart
    Window X    - quit
"""

from game import Game


def main():
    Game().run()


if __name__ == "__main__":
    main()
