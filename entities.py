"""
entities.py
-----------
PacMan and Ghost classes.

Both characters are tile-aligned: they always move from one full tile to a
neighbouring full tile. Between two tiles their pixel position is interpolated
so the movement looks smooth, but every AI decision is taken at tile centres.
This keeps the AI simple (it works on (row, col) integers) while the visual
output stays smooth at 60 FPS.

Member 1 (Game Engine) owns this file.
"""

import pygame
from settings import (
    TILE_SIZE, YELLOW, PLAYER_SPEED
)


class Entity:
    """
    Base class shared by Pac-Man and the ghosts.
    Stores both:
        - logical tile position : self.row, self.col   (used by the AI)
        - pixel position        : self.pixel_x, self.pixel_y (used by drawing)
    """

    def __init__(self, row, col, color, speed):
        self.row = row
        self.col = col
        self.target_row = row
        self.target_col = col
        self.pixel_x = col * TILE_SIZE
        self.pixel_y = row * TILE_SIZE
        self.color = color
        self.speed = speed

    # ---------- helpers used by the game loop ----------

    def at_target(self):
        """True when the entity is exactly on its target tile (centre of tile)."""
        return (self.pixel_x == self.target_col * TILE_SIZE and
                self.pixel_y == self.target_row * TILE_SIZE)

    def set_direction(self, dr, dc, maze):
        """
        Try to set a movement of (dr, dc) tiles. Returns True if the
        target tile is open. Used by the player keyboard input.
        """
        new_r = self.row + dr
        new_c = self.col + dc
        if 0 <= new_r < len(maze) and 0 <= new_c < len(maze[0]):
            if maze[new_r][new_c] == 0:
                self.target_row = new_r
                self.target_col = new_c
                return True
        return False

    def set_target_tile(self, row, col):
        """Force a specific neighbouring tile as the next target. Used by AI."""
        self.target_row = row
        self.target_col = col

    def update(self):
        """Move pixel position toward target tile by `self.speed` pixels."""
        target_x = self.target_col * TILE_SIZE
        target_y = self.target_row * TILE_SIZE

        if self.pixel_x < target_x:
            self.pixel_x = min(self.pixel_x + self.speed, target_x)
        elif self.pixel_x > target_x:
            self.pixel_x = max(self.pixel_x - self.speed, target_x)

        if self.pixel_y < target_y:
            self.pixel_y = min(self.pixel_y + self.speed, target_y)
        elif self.pixel_y > target_y:
            self.pixel_y = max(self.pixel_y - self.speed, target_y)

        if self.at_target():
            self.row = self.target_row
            self.col = self.target_col

    def get_rect(self, hud_offset=0):
        return pygame.Rect(self.pixel_x, self.pixel_y + hud_offset,
                           TILE_SIZE, TILE_SIZE)


class PacMan(Entity):
    """Yellow circle controlled by the player with the arrow keys."""

    def __init__(self, row, col):
        super().__init__(row, col, YELLOW, PLAYER_SPEED)
        # Direction the mouth points (used for the open-mouth animation).
        self.facing = (0, 1)  # (dr, dc) – default looking right
        self.anim_tick = 0

    def set_direction(self, dr, dc, maze):
        moved = super().set_direction(dr, dc, maze)
        if moved:
            self.facing = (dr, dc)
        return moved

    def update(self):
        super().update()
        self.anim_tick = (self.anim_tick + 1) % 30

    def draw(self, screen, hud_offset=0):
        cx = int(self.pixel_x + TILE_SIZE / 2)
        cy = int(self.pixel_y + hud_offset + TILE_SIZE / 2)
        radius = TILE_SIZE // 2 - 2

        # Mouth opens and closes based on anim_tick (0..29)
        mouth = abs(15 - self.anim_tick) / 15  # 0..1
        # angle of half-mouth in degrees (0 = closed, 35 = wide open)
        half_angle = int(5 + 30 * mouth)

        # Direction the mouth points
        dr, dc = self.facing
        if (dr, dc) == (0, 1):    base = 0      # right
        elif (dr, dc) == (0, -1): base = 180    # left
        elif (dr, dc) == (-1, 0): base = 90     # up
        else:                     base = 270    # down

        import math
        # Build the polygon: centre + arc points, skipping the mouth wedge
        points = [(cx, cy)]
        start = base + half_angle
        end = base + 360 - half_angle
        steps = 24
        for i in range(steps + 1):
            ang = math.radians(start + (end - start) * i / steps)
            points.append((cx + radius * math.cos(ang),
                           cy - radius * math.sin(ang)))
        pygame.draw.polygon(screen, self.color, points)


class Ghost(Entity):
    """Coloured ghost. AI logic lives outside this class (in game.py)."""

    def __init__(self, row, col, color, speed):
        super().__init__(row, col, color, speed)

    def draw(self, screen, hud_offset=0):
        cx = int(self.pixel_x + TILE_SIZE / 2)
        cy = int(self.pixel_y + hud_offset + TILE_SIZE / 2)
        r = TILE_SIZE // 2 - 2

        # Ghost body: a circle on top, rectangle below, three-bump skirt
        pygame.draw.circle(screen, self.color, (cx, cy - 2), r)
        body_rect = pygame.Rect(cx - r, cy - 2, 2 * r, r + 2)
        pygame.draw.rect(screen, self.color, body_rect)

        # Skirt (three small triangles at the bottom)
        bump_w = (2 * r) // 3
        for i in range(3):
            x0 = cx - r + i * bump_w
            x1 = x0 + bump_w
            xm = (x0 + x1) // 2
            y_top = cy + r - 1
            y_bot = cy + r + 3
            pygame.draw.polygon(
                screen, self.color,
                [(x0, y_top), (x1, y_top), (xm, y_bot)]
            )

        # Eyes
        pygame.draw.circle(screen, (255, 255, 255), (cx - 4, cy - 3), 3)
        pygame.draw.circle(screen, (255, 255, 255), (cx + 4, cy - 3), 3)
        pygame.draw.circle(screen, (0, 0, 80), (cx - 4, cy - 3), 1)
        pygame.draw.circle(screen, (0, 0, 80), (cx + 4, cy - 3), 1)
