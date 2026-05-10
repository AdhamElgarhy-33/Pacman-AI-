"""
settings.py
-----------
All game constants live here so they are easy to tweak.
Member 1 (Game Engine) owns this file.
"""

# ---- Tile / window sizes ----
TILE_SIZE = 25
COLS = 24
ROWS = 13
HUD_HEIGHT = 40                       # top bar showing level + score
WIDTH = COLS * TILE_SIZE              # 600 px
HEIGHT = ROWS * TILE_SIZE + HUD_HEIGHT  # 365 px
FPS = 60

# ---- Colors (R, G, B) ----
BLACK          = (0, 0, 0)
WHITE          = (255, 255, 255)
YELLOW         = (255, 215, 0)
RED            = (231, 41, 55)
PINK           = (255, 132, 188)
ORANGE         = (255, 140, 35)
BLUE           = (33, 33, 222)
WALL_OUTLINE   = (60, 60, 240)
GRAY           = (50, 50, 60)
GREEN          = (50, 220, 90)
PATH_HIGHLIGHT = (90, 200, 255)
HUD_BG         = (20, 20, 30)

# ---- Speeds (pixels per frame at 60 FPS) ----
PLAYER_SPEED   = 3
GHOST_SPEED_L1 = 1     # weak ghost on level 1 (BFS demo)
GHOST_SPEED_L2 = 2     # A* ghost
GHOST_SPEED_L3 = 2     # Minimax ghost

# ---- AI ----
MAX_LEVELS     = 3
MINIMAX_DEPTH  = 4     # 4 plies = 2 ghost moves + 2 pacman moves looked ahead

# ---- Spawn tiles (row, col) ----
PACMAN_SPAWN = (9, 12)
GHOST_SPAWN  = (3, 12)
