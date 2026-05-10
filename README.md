# Pac-Man AI Project

A Pac-Man clone with three levels, each powered by a different AI algorithm.

| Level | Algorithm | Author |
|-------|-----------|--------|
| 1 | Breadth-First Search (BFS) | Member 2 |
| 2 | A* Search | Member 3 |
| 3 | Minimax + Alpha-Beta Pruning | Member 4 |

GUI and game engine: Member 1.

---

## How to run in VS Code

1. Open the `pacman_project` folder in VS Code (`File > Open Folder...`).
2. Open the integrated terminal (``Ctrl+` ``).
3. Install the only dependency:

   ```bash
   pip install pygame
   ```

4. Run the game:

   ```bash
   python main.py
   ```

   On macOS/Linux you may need `python3 main.py`.

5. Controls:
   - **Arrow keys** — move Pac-Man
   - **ENTER / SPACE** — start the game, advance to the next level, restart
   - Close the window to quit

---

## File map

```
pacman_project/
├── main.py              entry point
├── game.py              main loop, drawing, level dispatch (Member 1)
├── settings.py          all constants (Member 1)
├── maze.py              maze layout + parser (Member 1)
├── entities.py          PacMan and Ghost classes (Member 1)
└── algorithms/
    ├── __init__.py
    ├── bfs.py           Breadth-First Search (Member 2 — original code)
    ├── astar.py         A* Search          (Member 3 — original code)
    └── minimax.py       Minimax + α-β      (Member 4)
```

The `bfs.py` and `astar.py` files contain the original code from Member 2
and Member 3 unchanged, with clear comment markers showing where their
code starts and ends. The game engine simply imports `bfs(...)` and
`astar(...)` and calls them — exactly as in the integration plan.
