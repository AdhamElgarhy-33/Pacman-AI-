"""
game.py
-------
The Game class. Owns the main loop, drawing, input, level state and the
dispatch to BFS / A* / Minimax depending on the level.

Member 1 (Game Engine) owns this file.
"""

import sys
import pygame

from settings import (
    TILE_SIZE, COLS, ROWS, WIDTH, HEIGHT, HUD_HEIGHT, FPS,
    BLACK, WHITE, YELLOW, RED, PINK, ORANGE, BLUE, WALL_OUTLINE,
    GRAY, GREEN, PATH_HIGHLIGHT, HUD_BG,
    PLAYER_SPEED, GHOST_SPEED_L1, GHOST_SPEED_L2, GHOST_SPEED_L3,
    MAX_LEVELS, MINIMAX_DEPTH, PACMAN_SPAWN, GHOST_SPAWN
)
from maze import parse_maze
from entities import PacMan, Ghost
from algorithms.bfs import bfs, find_nearest_food_path, get_neighbors
from algorithms.astar import astar
from algorithms.minimax import minimax_best_move


# ---------- helpers ----------

def step_along_path(path):
    """Given a path that starts at the entity's current tile, return the
    next tile to move to (or None if the path is empty / has 1 element)."""
    if path is None or len(path) < 2:
        return None
    return path[1]


# ---------- main class ----------

class Game:

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Pac-Man AI — BFS / A* / Minimax")
        self.screen = pygame.time.Clock()  # placeholder, overwritten below
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.font_big = pygame.font.SysFont("arial", 28, bold=True)
        self.font = pygame.font.SysFont("arial", 18, bold=True)
        self.font_small = pygame.font.SysFont("arial", 14)

        self.state = "menu"   # "menu", "playing", "gameover", "win", "level_clear"
        self.level = 1
        self.score = 0
        self.lives = 3
        self.message_timer = 0
        self.message = ""

        self._reset_level(self.level)

    # ---------- level setup ----------

    def _reset_level(self, level):
        self.maze, self.food = parse_maze()
        # Remove pellets at spawn tiles so Pac-Man does not "eat himself in".
        self.food.discard(PACMAN_SPAWN)
        self.food.discard(GHOST_SPAWN)

        self.pacman = PacMan(*PACMAN_SPAWN)

        self.ghosts = []
        if level == 1:
            # One slow ghost using BFS.
            self.ghosts.append(
                Ghost(GHOST_SPAWN[0], GHOST_SPAWN[1], RED, GHOST_SPEED_L1)
            )
        elif level == 2:
            # Two A* ghosts.
            self.ghosts.append(
                Ghost(GHOST_SPAWN[0], GHOST_SPAWN[1], RED, GHOST_SPEED_L2)
            )
            self.ghosts.append(
                Ghost(GHOST_SPAWN[0], GHOST_SPAWN[1] - 2, PINK, GHOST_SPEED_L2)
            )
        else:
            # One Minimax ghost (deeper search means it is slower to think,
            # so we do not need to spawn many of them).
            self.ghosts.append(
                Ghost(GHOST_SPAWN[0], GHOST_SPAWN[1], ORANGE, GHOST_SPEED_L3)
            )

        # Highlight buffers (recomputed every few frames)
        self.bfs_highlight = []
        self._ai_tick = 0

    # ---------- main loop ----------

    def run(self):
        while True:
            dt = self.clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    self._handle_keydown(event.key)

            if self.state == "playing":
                self._update_playing()

            self._draw()
            pygame.display.flip()

    # ---------- input ----------

    def _handle_keydown(self, key):
        if self.state in ("menu", "gameover", "win"):
            if key == pygame.K_RETURN or key == pygame.K_SPACE:
                self.state = "playing"
                self.level = 1
                self.score = 0
                self.lives = 3
                self._reset_level(self.level)
            return

        if self.state == "level_clear":
            if key == pygame.K_RETURN or key == pygame.K_SPACE:
                self.level += 1
                if self.level > MAX_LEVELS:
                    self.state = "win"
                else:
                    self._reset_level(self.level)
                    self.state = "playing"
            return

        # Playing: arrow keys queue a direction change for Pac-Man.
        if self.state == "playing":
            if key == pygame.K_LEFT:
                self._queue_player_dir(0, -1)
            elif key == pygame.K_RIGHT:
                self._queue_player_dir(0, 1)
            elif key == pygame.K_UP:
                self._queue_player_dir(-1, 0)
            elif key == pygame.K_DOWN:
                self._queue_player_dir(1, 0)

    def _queue_player_dir(self, dr, dc):
        # Only allow turning when Pac-Man is on a tile centre.
        if self.pacman.at_target():
            self.pacman.set_direction(dr, dc, self.maze)

    # ---------- update step ----------

    def _update_playing(self):
        # Continuous keyboard for fluid movement: when Pac-Man reaches a
        # tile centre, peek at the keys and try to keep going.
        if self.pacman.at_target():
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                self.pacman.set_direction(0, -1, self.maze)
            elif keys[pygame.K_RIGHT]:
                self.pacman.set_direction(0, 1, self.maze)
            elif keys[pygame.K_UP]:
                self.pacman.set_direction(-1, 0, self.maze)
            elif keys[pygame.K_DOWN]:
                self.pacman.set_direction(1, 0, self.maze)

        self.pacman.update()

        # Pellet eating
        tile = (self.pacman.row, self.pacman.col)
        if tile in self.food and self.pacman.at_target():
            self.food.discard(tile)
            self.score += 10

        # Ghost AI runs every few frames (otherwise level 3 stalls).
        self._ai_tick += 1
        if self._ai_tick >= 4:
            self._ai_tick = 0
            self._run_ghost_ai()
            if self.level == 1:
                self._update_bfs_highlight()

        for g in self.ghosts:
            g.update()

        # Collision
        for g in self.ghosts:
            if (g.row, g.col) == (self.pacman.row, self.pacman.col):
                self._on_caught()
                return
            if g.get_rect().colliderect(self.pacman.get_rect()):
                self._on_caught()
                return

        # Level cleared?
        if not self.food:
            self.state = "level_clear"

    def _on_caught(self):
        self.lives -= 1
        if self.lives <= 0:
            self.state = "gameover"
        else:
            # Respawn entities at spawn tiles, keep food and score.
            self.pacman = PacMan(*PACMAN_SPAWN)
            for i, g in enumerate(self.ghosts):
                g.row = g.target_row = GHOST_SPAWN[0]
                g.col = g.target_col = GHOST_SPAWN[1] - 2 * i
                g.pixel_x = g.col * TILE_SIZE
                g.pixel_y = g.row * TILE_SIZE

    # ---------- ghost AI dispatch ----------

    def _run_ghost_ai(self):
        pac = (self.pacman.row, self.pacman.col)

        for ghost in self.ghosts:
            if not ghost.at_target():
                continue  # still gliding to its previous tile

            ghost_pos = (ghost.row, ghost.col)

            if self.level == 1:
                # Member 2's BFS used to track Pac-Man.
                path = bfs(ghost_pos, pac, self.maze)
                nxt = step_along_path(path)
            elif self.level == 2:
                # Member 3's A* used to chase Pac-Man.
                path = astar(ghost_pos, pac, self.maze)
                nxt = step_along_path(path)
            else:
                # Member 4's Minimax + alpha-beta.
                nxt = minimax_best_move(
                    ghost_pos, pac, self.maze, depth=MINIMAX_DEPTH
                )
                if nxt == ghost_pos:
                    nxt = None

            if nxt is not None:
                ghost.set_target_tile(*nxt)

    def _update_bfs_highlight(self):
        """On level 1 we draw the BFS path Pac-Man would take to the
        nearest pellet so the algorithm is visible to the viewer."""
        pac = (self.pacman.row, self.pacman.col)
        path = find_nearest_food_path(pac, self.food, self.maze)
        self.bfs_highlight = path or []

    # ---------- drawing ----------

    def _draw(self):
        self.screen.fill(BLACK)

        if self.state == "menu":
            self._draw_menu()
            return

        self._draw_maze()
        self._draw_food()
        if self.level == 1:
            self._draw_bfs_highlight()
        self.pacman.draw(self.screen, hud_offset=HUD_HEIGHT)
        for g in self.ghosts:
            g.draw(self.screen, hud_offset=HUD_HEIGHT)
        self._draw_hud()

        if self.state == "level_clear":
            self._draw_overlay(
                f"Level {self.level} cleared!",
                "Press ENTER for next level"
            )
        elif self.state == "gameover":
            self._draw_overlay("Game Over",
                               "Press ENTER to play again")
        elif self.state == "win":
            self._draw_overlay("You Win — All 3 Levels Cleared!",
                               "Press ENTER to restart")

    def _draw_maze(self):
        for r in range(ROWS):
            for c in range(COLS):
                if self.maze[r][c] == 1:
                    rect = pygame.Rect(
                        c * TILE_SIZE,
                        r * TILE_SIZE + HUD_HEIGHT,
                        TILE_SIZE,
                        TILE_SIZE
                    )
                    pygame.draw.rect(self.screen, BLUE, rect)
                    pygame.draw.rect(self.screen, WALL_OUTLINE, rect, 1)

    def _draw_food(self):
        for (r, c) in self.food:
            cx = c * TILE_SIZE + TILE_SIZE // 2
            cy = r * TILE_SIZE + TILE_SIZE // 2 + HUD_HEIGHT
            pygame.draw.circle(self.screen, WHITE, (cx, cy), 3)

    def _draw_bfs_highlight(self):
        for (r, c) in self.bfs_highlight:
            cx = c * TILE_SIZE + TILE_SIZE // 2
            cy = r * TILE_SIZE + TILE_SIZE // 2 + HUD_HEIGHT
            pygame.draw.circle(self.screen, PATH_HIGHLIGHT, (cx, cy), 4, 1)

    def _draw_hud(self):
        bar = pygame.Rect(0, 0, WIDTH, HUD_HEIGHT)
        pygame.draw.rect(self.screen, HUD_BG, bar)
        pygame.draw.line(self.screen, GRAY, (0, HUD_HEIGHT),
                         (WIDTH, HUD_HEIGHT), 1)

        algo_name = {1: "BFS", 2: "A*", 3: "Minimax + α-β"}[self.level]
        left = self.font.render(
            f"Level {self.level}  ({algo_name})", True, WHITE
        )
        self.screen.blit(left, (10, 10))

        center = self.font.render(f"Score: {self.score}", True, YELLOW)
        self.screen.blit(center, (WIDTH // 2 - center.get_width() // 2, 10))

        right = self.font.render(f"Lives: {self.lives}", True, GREEN)
        self.screen.blit(right, (WIDTH - right.get_width() - 10, 10))

    def _draw_overlay(self, title, subtitle):
        veil = pygame.Surface((WIDTH, HEIGHT))
        veil.set_alpha(170)
        veil.fill(BLACK)
        self.screen.blit(veil, (0, 0))
        t = self.font_big.render(title, True, YELLOW)
        s = self.font.render(subtitle, True, WHITE)
        self.screen.blit(
            t, (WIDTH // 2 - t.get_width() // 2, HEIGHT // 2 - 30)
        )
        self.screen.blit(
            s, (WIDTH // 2 - s.get_width() // 2, HEIGHT // 2 + 10)
        )

    def _draw_menu(self):
        title = self.font_big.render("Pac-Man — AI Demo", True, YELLOW)
        sub = self.font.render(
            "Level 1: BFS    Level 2: A*    Level 3: Minimax + α-β",
            True, WHITE
        )
        hint = self.font_small.render(
            "Arrow keys to move, ENTER to start",
            True, WHITE
        )
        self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 80))
        self.screen.blit(sub, (WIDTH // 2 - sub.get_width() // 2, 150))
        self.screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, 200))
