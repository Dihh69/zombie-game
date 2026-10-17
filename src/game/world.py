"""Game world simulation: orchestrates players, arena, spawner, projectiles, effects, and camera."""

from __future__ import annotations
import math
from typing import TYPE_CHECKING
import pygame

from src.game.camera import Camera
from src.game.checkpoint import CheckpointManager
from src.game.effects import EffectManager
from src.game.platforms import create_arena, platform_rects, Platform
from src.game.player import Player

if TYPE_CHECKING:
    from src.game.assets import AssetManager
    from src.game.settings import GameConfig


class World:
    """Orchestrates all game entities, physics simulation, collisions, and world rendering."""

    def __init__(self, config: GameConfig, assets: AssetManager) -> None:
        self.config: GameConfig = config
        self.assets: AssetManager = assets

        # Arena world bounds (spacious arena for cinematic panning)
        self.world_bounds: pygame.Rect = pygame.Rect(0, 0, 1600, 860)

        self.camera: Camera = Camera(config.screen_size, self.world_bounds)
        self.effects: EffectManager = EffectManager()
        self.checkpoint_manager: CheckpointManager = CheckpointManager(config)
        self.platforms: list[Platform] = create_arena(self.world_bounds)

        self.players: list[Player] = []
        self.player: Player
        self.left_player: Player
        self.right_player: Player

        self.reset()

    def reset(self) -> None:
        """Reset match state, spawn single hero, and initiate cinematic intro camera."""
        self.effects.clear()
        self.checkpoint_manager.reset()
        self.platforms = create_arena(self.world_bounds)

        # Spawn single Hero on arena ground
        floor_y = float(self.world_bounds.bottom - 90)
        spawn_pos = (float(self.world_bounds.centerx), floor_y)
        p1 = Player(
            player_id=1,
            spawn=spawn_pos,
            controls=self.config.controls.left,
            assets=self.assets,
            config=self.config,
        )
        p1.on_ground = True

        self.player = p1
        self.players = [p1]
        self.left_player = p1
        self.right_player = p1

        # Start cinematic intro focusing on the hero
        self.camera.start_intro(p1.center())

    def handle_event(self, event: pygame.event.Event) -> None:
        """Route input events to players."""
        for p in self.players:
            p.handle_event(event)

    def update(self, dt: float) -> None:
        """Advance world simulation adhering to integration collision order."""
        plat_boxes = platform_rects(self.platforms)
        keys = pygame.key.get_pressed()

        # Input handling for players
        for p in self.players:
            p.handle_input(keys, dt)

            # Check continuous attack hold
            att_key = p.controls.get("attack", -1)
            att_alt = p.controls.get("attack_alt", -1)
            is_attacking = p._attack_held or (att_key != -1 and keys[att_key]) or (att_alt != -1 and keys[att_alt])
            if is_attacking:
                opponents = [other for other in self.players if other is not p]
                p.attack(targets=opponents, effects=self.effects)

        # 1. Update players and platform collisions (passing platforms to detect one-way platforms)
        for p in self.players:
            p.update(dt, self.platforms, self.world_bounds)

        # 2. Update effects and camera
        self.effects.update(dt)
        self.camera.set_shake(self.effects.shake_offset())
        self.camera.update(dt)

    def draw(self, surface: pygame.Surface) -> None:
        """Render world objects adhering to integration rendering order."""
        # 1. Background (Atmospheric magical starry sky & distant battlements)
        self._draw_background(surface)

        # 2. Platforms
        for plat in self.platforms:
            plat.draw(surface, self.camera)

        # 3. Players
        for p in self.players:
            p.draw(surface, self.camera)

        # 4. World visual effects
        self.effects.draw(surface, self.camera)

    def _draw_background(self, surface: pygame.Surface) -> None:
        """Render procedural background with layered battlements and stars."""
        # Deep night gradient fill
        surface.fill((12, 16, 26))

        # Distant stars (parallax)
        cam_tl = self.camera.top_left
        for i in range(50):
            star_wx = (i * 97) % self.world_bounds.width
            star_wy = (i * 53) % (self.world_bounds.height - 200)
            sx = int((star_wx - self.camera.center.x) * 0.4 + self.config.screen_width / 2) % self.config.screen_width
            sy = int((star_wy - self.camera.center.y) * 0.4 + self.config.screen_height / 2) % self.config.screen_height
            brightness = 140 + (i * 17) % 115
            pygame.draw.circle(surface, (brightness, brightness, min(255, brightness + 20)), (sx, sy), 2)

        # Distant silhouette towers / battlements
        tower_color = (20, 24, 38)
        tower_spacing = 280
        z = self.camera.zoom
        for x in range(0, self.world_bounds.width + 100, tower_spacing):
            tw_rect = pygame.Rect(x, self.world_bounds.bottom - 420, 150, 420)
            s_rect = self.camera.apply_rect(tw_rect)
            if s_rect.colliderect(surface.get_rect()):
                pygame.draw.rect(surface, tower_color, s_rect)
                emb_w = max(8, int(20 * z))
                emb_h = max(5, int(14 * z))
                step = max(14, int(35 * z))
                for bx in range(s_rect.left, s_rect.right, step):
                    pygame.draw.rect(surface, (14, 18, 28), (bx, s_rect.top - emb_h, emb_w, emb_h))

    def finished(self) -> bool:
        """Check if round has concluded due to hero defeat or timeout."""
        return not self.player.alive()

    def winner(self) -> Player | None:
        """Retrieve the player entity if surviving."""
        return self.player if self.player.alive() else None
