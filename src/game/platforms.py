"""Arena geometry and platform surfaces."""

from __future__ import annotations
from typing import TYPE_CHECKING
import pygame

if TYPE_CHECKING:
    from src.game.camera import Camera


class Platform:
    """Static arena platform with procedural stone styling and optional one-way pass-through."""

    def __init__(self, rect: pygame.Rect, style: str = "stone", is_one_way: bool = False) -> None:
        self.rect: pygame.Rect = pygame.Rect(rect)
        self.style: str = style
        self.is_one_way: bool = is_one_way

    @staticmethod
    def create_arena(world_bounds: pygame.Rect | None = None) -> list[Platform]:
        """Construct arena platforms."""
        return create_arena(world_bounds)

    @staticmethod
    def platform_rects(platforms: list[Platform]) -> list[pygame.Rect]:
        """Extract rects from platform list."""
        return platform_rects(platforms)

    def draw(self, surface: pygame.Surface, camera: Camera) -> None:
        """Draw the platform with procedural brick and magical highlight effects."""
        screen_rect = camera.apply_rect(self.rect)

        # Skip if entirely offscreen
        if not screen_rect.colliderect(surface.get_rect()):
            return

        if self.style == "wood":
            main_color = (68, 44, 30)
            top_color = (145, 98, 62)
            line_color = (45, 28, 18)
            rune_color = (230, 175, 90)
        else:  # "stone" or default
            main_color = (36, 40, 52)
            top_color = (82, 98, 122)
            line_color = (22, 25, 34)
            rune_color = (90, 195, 240)

        # 1. Base rectangle
        pygame.draw.rect(surface, main_color, screen_rect, border_radius=4)

        # 2. Top landing highlight ledge
        top_h = min(6, max(3, screen_rect.height // 3))
        top_ledge = pygame.Rect(screen_rect.x, screen_rect.y, screen_rect.width, top_h)
        pygame.draw.rect(surface, top_color, top_ledge, border_top_left_radius=4, border_top_right_radius=4)

        # 3. Procedural brick lines using squares/lines
        if screen_rect.height > 16:
            brick_w = 40
            brick_h = 16
            for row, y in enumerate(range(screen_rect.y + top_h, screen_rect.bottom, brick_h)):
                offset = (brick_w // 2) if (row % 2 == 1) else 0
                pygame.draw.line(surface, line_color, (screen_rect.x, y), (screen_rect.right, y), width=1)
                for x in range(screen_rect.x + offset, screen_rect.right, brick_w):
                    pygame.draw.line(surface, line_color, (x, y), (x, min(y + brick_h, screen_rect.bottom)), width=1)

        # 4. Magical trim line on the top landing surface
        pygame.draw.line(
            surface,
            rune_color,
            (screen_rect.x + 4, screen_rect.y + 2),
            (screen_rect.right - 4, screen_rect.y + 2),
            width=2,
        )

        # 5. One-way indicators (subtle glowing brackets under floating platforms)
        if self.is_one_way:
            bracket_color = (rune_color[0] // 2, rune_color[1] // 2, rune_color[2] // 2)
            for bx in range(screen_rect.x + 20, screen_rect.right - 20, 60):
                pygame.draw.lines(
                    surface,
                    bracket_color,
                    False,
                    [(bx, screen_rect.bottom), (bx + 8, screen_rect.bottom + 4), (bx + 16, screen_rect.bottom)],
                    width=2,
                )

        # 6. Outer border
        pygame.draw.rect(surface, (15, 18, 25), screen_rect, width=2, border_radius=4)


def create_arena(world_bounds: pygame.Rect | None = None) -> list[Platform]:
    """Construct the default two-player magical arena geometry with optimized traversal heights."""
    w = world_bounds.width if world_bounds else 1600
    h = world_bounds.height if world_bounds else 860

    platforms: list[Platform] = []

    # Main Ground (solid, full arena base)
    platforms.append(Platform(pygame.Rect(0, h - 90, w, 90), style="stone", is_one_way=False))

    # Floating platforms (all one-way jump-through for effortless platforming)
    # Tier 1: Lower Side Battlements
    platforms.append(Platform(pygame.Rect(140, h - 210, 280, 22), style="stone", is_one_way=True))
    platforms.append(Platform(pygame.Rect(w - 420, h - 210, 280, 22), style="stone", is_one_way=True))

    # Tier 1 Center: Wide Low Plaza
    platforms.append(Platform(pygame.Rect(w // 2 - 220, h - 250, 440, 24), style="stone", is_one_way=True))

    # Tier 2: Mid-Level Stepping Stones
    platforms.append(Platform(pygame.Rect(240, h - 360, 260, 20), style="wood", is_one_way=True))
    platforms.append(Platform(pygame.Rect(w - 500, h - 360, 260, 20), style="wood", is_one_way=True))

    # Tier 3: High Balconies
    platforms.append(Platform(pygame.Rect(100, h - 470, 240, 22), style="stone", is_one_way=True))
    platforms.append(Platform(pygame.Rect(w - 340, h - 470, 240, 22), style="stone", is_one_way=True))

    # Tier 4: Apex Grand Altar (Crown of the arena)
    platforms.append(Platform(pygame.Rect(w // 2 - 180, h - 550, 360, 26), style="stone", is_one_way=True))

    return platforms


def platform_rects(platforms: list[Platform]) -> list[pygame.Rect]:
    """Extract collision bounding boxes from platform list."""
    return [p.rect for p in platforms]
