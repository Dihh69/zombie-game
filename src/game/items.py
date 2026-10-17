"""Collectible items, weapons, and sky item spawner."""

from __future__ import annotations
from enum import Enum
import math
import random
from typing import TYPE_CHECKING
import pygame

from src.game.projectiles import Projectile

if TYPE_CHECKING:
    from src.game.camera import Camera
    from src.game.effects import EffectManager
    from src.game.player import Player
    from src.game.settings import GameConfig


class ItemType(Enum):
    """Available item types in the magical arena."""

    BOMB = "bomb"
    WAND = "wand"
    ROBE = "robe"
    MACHINE_GUN = "machine_gun"
    PISTOL = "pistol"


class Item:
    """Collectible item that can be picked up and used by players."""

    def __init__(self, item_type: ItemType, position: tuple[float, float]) -> None:
        self.item_type: ItemType = item_type
        self.position: pygame.Vector2 = pygame.Vector2(position[0], position[1])
        self.velocity: pygame.Vector2 = pygame.Vector2(0.0, 120.0)
        self.active: bool = True
        self.on_ground: bool = False
        self._bob_timer: float = random.uniform(0.0, 6.28)

        # Ammo and cooldown settings per item type
        self.cooldown: float = 0.0
        if item_type == ItemType.BOMB:
            self.max_ammo: int = 3
            self.fire_rate: float = 0.75
        elif item_type == ItemType.WAND:
            self.max_ammo: int = 12
            self.fire_rate: float = 0.22
        elif item_type == ItemType.ROBE:
            self.max_ammo: int = 1
            self.fire_rate: float = 1.0
        elif item_type == ItemType.MACHINE_GUN:
            self.max_ammo: int = 30
            self.fire_rate: float = 0.10
        elif item_type == ItemType.PISTOL:
            self.max_ammo: int = 7
            self.fire_rate: float = 0.40
        else:
            self.max_ammo = 5
            self.fire_rate = 0.30

        self.ammo: int = self.max_ammo

    @property
    def bounds(self) -> pygame.Rect:
        """Collision rectangle in world space."""
        return pygame.Rect(int(self.position.x - 18), int(self.position.y - 18), 36, 36)

    def update(
        self,
        dt: float,
        platforms: list[pygame.Rect],
        world_bounds: pygame.Rect,
    ) -> None:
        """Update falling physics, platform landing, and floating bob animation."""
        if not self.active:
            # Update cooldown when held
            if self.cooldown > 0:
                self.cooldown = max(0.0, self.cooldown - dt)
            return

        self._bob_timer += dt

        if not self.on_ground:
            self.velocity.y += 650.0 * dt
            self.position.y += self.velocity.y * dt
            self.position.x += self.velocity.x * dt

            item_box = self.bounds
            for plat in platforms:
                if item_box.colliderect(plat) and self.velocity.y > 0:
                    if self.position.y - self.velocity.y * dt <= plat.top + 8:
                        self.position.y = plat.top - 18
                        self.velocity.y = 0.0
                        self.velocity.x = 0.0
                        self.on_ground = True
                        break

            # Clamp to world floor
            if self.position.y >= world_bounds.bottom - 40:
                self.position.y = world_bounds.bottom - 40
                self.velocity.y = 0.0
                self.on_ground = True

    def collect(self, player: Player) -> None:
        """Collect item and equip to the player."""
        self.active = False
        player.equip(self)

    def use(
        self,
        player: Player,
        projectiles: list[Projectile],
        effects: EffectManager,
    ) -> None:
        """Activate the held item's weapon or defensive behavior."""
        if self.cooldown > 0 or self.ammo <= 0:
            return

        facing = player.facing
        px, py = player.center()
        muzzle_x = px + facing * 24.0
        muzzle_y = py - 4.0

        speed_mult = max(0.1, getattr(player, "attack_speed_multiplier", 1.0))
        damage_mult = getattr(player, "attack_damage_multiplier", 1.0)
        eff_cooldown = self.fire_rate / speed_mult

        if self.item_type == ItemType.BOMB:
            # Arcing explosive bomb
            bomb_vx = facing * 420.0 + player.velocity.x * 0.25
            bomb_vy = -340.0
            proj = Projectile(
                owner_id=player.player_id,
                position=(muzzle_x, muzzle_y),
                velocity=(bomb_vx, bomb_vy),
                damage=55.0 * damage_mult,
                kind="bomb",
                radius=10,
            )
            projectiles.append(proj)
            effects.burst((muzzle_x, muzzle_y), count=6, palette=[(255, 180, 50), (255, 100, 20)])
            effects.request_shake(intensity=4.0, duration=0.15)
            self.cooldown = eff_cooldown
            self.ammo -= 1

        elif self.item_type == ItemType.WAND:
            # Fast magical bolt
            bolt_vx = facing * 780.0
            bolt_vy = random.uniform(-15.0, 15.0)
            proj = Projectile(
                owner_id=player.player_id,
                position=(muzzle_x, muzzle_y),
                velocity=(bolt_vx, bolt_vy),
                damage=18.0 * damage_mult,
                kind="wand",
                radius=7,
            )
            projectiles.append(proj)
            effects.burst((muzzle_x, muzzle_y), count=8, palette=[(100, 240, 255), (240, 100, 255)])
            self.cooldown = eff_cooldown
            self.ammo -= 1

        elif self.item_type == ItemType.ROBE:
            # Defensive magic shield
            player.activate_shield(duration=6.5)
            effects.burst((px, py), count=25, palette=[(100, 200, 255), (200, 240, 255), (80, 140, 255)], strength=1.2)
            self.cooldown = eff_cooldown
            self.ammo -= 1

        elif self.item_type == ItemType.MACHINE_GUN:
            # Rapid spray
            spread = random.uniform(-40.0, 40.0)
            proj = Projectile(
                owner_id=player.player_id,
                position=(muzzle_x, muzzle_y),
                velocity=(facing * 880.0, spread),
                damage=7.0 * damage_mult,
                kind="machine_gun",
                radius=4,
            )
            projectiles.append(proj)
            effects.burst((muzzle_x, muzzle_y), count=4, palette=[(255, 230, 100), (255, 160, 40)], strength=0.5)
            effects.request_shake(intensity=2.0, duration=0.08)
            self.cooldown = eff_cooldown
            self.ammo -= 1

        elif self.item_type == ItemType.PISTOL:
            # Solid heavy shot
            proj = Projectile(
                owner_id=player.player_id,
                position=(muzzle_x, muzzle_y),
                velocity=(facing * 720.0, 0.0),
                damage=26.0 * damage_mult,
                kind="pistol",
                radius=6,
            )
            projectiles.append(proj)
            effects.burst((muzzle_x, muzzle_y), count=10, palette=[(255, 200, 80), (255, 80, 40)], strength=0.8)
            effects.request_shake(intensity=4.5, duration=0.12)
            self.cooldown = eff_cooldown
            self.ammo -= 1

        if self.ammo <= 0:
            player.equip(None)

    def draw(self, surface: pygame.Surface, camera: Camera) -> None:
        """Render collectible item in the arena using clean procedural geometric shapes."""
        if not self.active:
            return

        z = camera.zoom
        bob = math.sin(self._bob_timer * 3.5) * (4.0 * z) if self.on_ground else 0.0
        draw_pos = (self.position.x, self.position.y)
        screen_pos = camera.apply(draw_pos)
        sx = screen_pos[0]
        sy = int(screen_pos[1] + bob)

        box_size = max(18, int(36 * z))
        half_box = box_size // 2

        container_rect = pygame.Rect(sx - half_box, sy - half_box, box_size, box_size)
        if not container_rect.colliderect(surface.get_rect()):
            return

        # Background square container
        bg_surf = pygame.Surface((box_size, box_size), pygame.SRCALPHA)
        pygame.draw.rect(bg_surf, (20, 24, 38, 210), (0, 0, box_size, box_size), border_radius=max(2, int(6 * z)))
        pygame.draw.rect(bg_surf, (240, 200, 60, 240), (0, 0, box_size, box_size), width=max(1, int(2 * z)), border_radius=max(2, int(6 * z)))
        surface.blit(bg_surf, (sx - half_box, sy - half_box))

        # Item-specific procedural icons scaled
        if self.item_type == ItemType.BOMB:
            br = max(3, int(8 * z))
            pygame.draw.circle(surface, (30, 30, 35), (sx, sy + int(2 * z)), br)
            pygame.draw.circle(surface, (10, 10, 12), (sx, sy + int(2 * z)), br, width=max(1, int(2 * z)))
            pygame.draw.circle(surface, (255, 140, 30), (sx + int(4 * z), sy - int(8 * z)), max(1, int(3 * z)))
            pygame.draw.line(surface, (150, 110, 70), (sx + int(2 * z), sy - int(4 * z)), (sx + int(4 * z), sy - int(7 * z)), width=max(1, int(2 * z)))

        elif self.item_type == ItemType.WAND:
            wl = int(8 * z)
            pygame.draw.line(surface, (120, 80, 40), (sx - wl, sy + wl), (sx + wl, sy - wl), width=max(1, int(3 * z)))
            pygame.draw.circle(surface, (100, 230, 255), (sx + wl + 1, sy - wl - 1), max(1, int(4 * z)))
            pygame.draw.circle(surface, (255, 255, 255), (sx + wl + 1, sy - wl - 1), max(1, int(2 * z)))

        elif self.item_type == ItemType.ROBE:
            sp = int(9 * z)
            shield_pts = [
                (sx, sy - sp),
                (sx + sp, sy - sp // 2),
                (sx + int(sp * 0.8), sy + int(sp * 0.8)),
                (sx, sy + sp),
                (sx - int(sp * 0.8), sy + int(sp * 0.8)),
                (sx - sp, sy - sp // 2),
            ]
            pygame.draw.polygon(surface, (60, 140, 255), shield_pts)
            pygame.draw.polygon(surface, (220, 240, 255), shield_pts, width=max(1, int(2 * z)))

        elif self.item_type == ItemType.MACHINE_GUN:
            gw, gh = int(18 * z), int(8 * z)
            pygame.draw.rect(surface, (70, 75, 85), (sx - gw // 2, sy - gh // 2, gw, gh), border_radius=2)
            pygame.draw.rect(surface, (200, 180, 50), (sx + gw // 2 - int(6 * z), sy - gh // 2 - int(2 * z), int(6 * z), int(4 * z)))

        elif self.item_type == ItemType.PISTOL:
            gw, gh = int(14 * z), int(6 * z)
            pygame.draw.rect(surface, (60, 60, 70), (sx - gw // 2, sy - gh // 2, gw, gh), border_radius=1)
            pygame.draw.rect(surface, (220, 70, 50), (sx + gw // 2 - int(4 * z), sy - gh // 2, int(4 * z), int(4 * z)))


class ItemSpawner:
    """Spawns magical items falling from the sky at randomized intervals."""

    def __init__(self, config: GameConfig) -> None:
        self.config: GameConfig = config
        self.spawn_interval: float = config.spawn_interval
        self.timer: float = 2.0  # initial spawn after 2 seconds
        self.max_ground_items: int = 4
        self.active_items: list[Item] = []

    def update(self, dt: float, world_bounds: pygame.Rect) -> list[Item]:
        """Update timer and generate newly spawned items when appropriate."""
        newly_spawned: list[Item] = []
        self.timer -= dt

        # Prune inactive items from tracker
        self.active_items = [it for it in self.active_items if it.active]

        if self.timer <= 0:
            self.timer = self.spawn_interval + random.uniform(-1.0, 1.2)
            if len(self.active_items) < self.max_ground_items:
                # Random type
                chosen_type = random.choice(list(ItemType))
                # Bounded horizontal position
                margin = 120
                spawn_x = random.uniform(world_bounds.left + margin, world_bounds.right - margin)
                spawn_y = world_bounds.top + 30.0

                item = Item(chosen_type, (spawn_x, spawn_y))
                self.active_items.append(item)
                newly_spawned.append(item)

        return newly_spawned

    def draw(self, surface: pygame.Surface, camera: Camera) -> None:
        """Spawner visual indicators (if any)."""
        pass
