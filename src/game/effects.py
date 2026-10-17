"""Visual effects system: particles, polygon explosions, and screen shake."""

from __future__ import annotations
import math
import random
from typing import TYPE_CHECKING
import pygame

if TYPE_CHECKING:
    from src.game.camera import Camera


class Particle:
    """Individual visual particle with procedural rendering."""

    def __init__(
        self,
        position: tuple[float, float],
        velocity: tuple[float, float],
        lifetime: float,
        color: tuple[int, int, int],
        radius: float,
        kind: str = "circle",
    ) -> None:
        self.position: pygame.Vector2 = pygame.Vector2(position[0], position[1])
        self.velocity: pygame.Vector2 = pygame.Vector2(velocity[0], velocity[1])
        self.lifetime: float = lifetime
        self.max_lifetime: float = max(0.01, lifetime)
        self.color: tuple[int, int, int] = color
        self.radius: float = radius
        self.initial_radius: float = radius
        self.kind: str = kind
        self.angle: float = random.uniform(0, 2 * math.pi)
        self.rot_speed: float = random.uniform(-8.0, 8.0)

    def update(self, dt: float) -> None:
        """Update particle motion, lifetime, and size decay."""
        self.lifetime -= dt
        self.position += self.velocity * dt
        self.angle += self.rot_speed * dt

        # Slight air friction
        self.velocity *= math.pow(0.85, dt * 60)

        # Kind-specific behaviors
        if self.kind == "smoke":
            self.velocity.y -= 15.0 * dt  # gently float upward
        elif self.kind in ("shard", "spark"):
            self.velocity.y += 180.0 * dt  # light gravity for debris

    def draw(self, surface: pygame.Surface, camera: Camera) -> None:
        """Draw particle to surface applying camera transformation and zoom scale."""
        if self.lifetime <= 0:
            return

        progress = max(0.0, min(1.0, self.lifetime / self.max_lifetime))
        screen_pos = camera.apply((self.position.x, self.position.y))
        z = camera.zoom

        # Skip if completely outside view
        if not (-60 <= screen_pos[0] <= camera.screen_width + 60 and -60 <= screen_pos[1] <= camera.screen_height + 60):
            return

        alpha = int(255 * progress)
        current_radius = max(1.0, self.initial_radius * progress * z)

        if self.kind == "ring":
            # Expanding shockwave ring
            ring_r = int(self.initial_radius * (1.0 + (1.0 - progress) * 2.5) * z)
            if ring_r > 0:
                ring_surf = pygame.Surface((ring_r * 2 + 4, ring_r * 2 + 4), pygame.SRCALPHA)
                ring_color = (*self.color, min(255, int(alpha * 1.2)))
                width = max(1, int(3 * progress * z))
                pygame.draw.circle(ring_surf, ring_color, (ring_r + 2, ring_r + 2), ring_r, width=width)
                surface.blit(ring_surf, (screen_pos[0] - ring_r - 2, screen_pos[1] - ring_r - 2))

        elif self.kind == "shard":
            # Jagged triangular/polygon shard
            shard_surf = pygame.Surface((int(current_radius * 4 + 4), int(current_radius * 4 + 4)), pygame.SRCALPHA)
            c = shard_surf.get_rect().center
            r = current_radius
            pts = [
                (c[0] + r * math.cos(self.angle), c[1] + r * math.sin(self.angle)),
                (c[0] + (r * 0.5) * math.cos(self.angle + 2.1), c[1] + (r * 0.5) * math.sin(self.angle + 2.1)),
                (c[0] + (r * 1.4) * math.cos(self.angle + 3.8), c[1] + (r * 1.4) * math.sin(self.angle + 3.8)),
            ]
            shard_color = (*self.color, alpha)
            pygame.draw.polygon(shard_surf, shard_color, pts)
            surface.blit(shard_surf, (screen_pos[0] - c[0], screen_pos[1] - c[1]))

        elif self.kind == "square":
            # Procedural square spark
            size = max(2, int(current_radius * 2))
            sq_surf = pygame.Surface((size, size), pygame.SRCALPHA)
            sq_surf.fill((*self.color, alpha))
            surface.blit(sq_surf, (screen_pos[0] - size // 2, screen_pos[1] - size // 2))

        elif self.kind == "spark":
            # Directional spark line
            speed = self.velocity.length()
            if speed > 10.0:
                dir_vec = self.velocity.normalize()
                tail_len = min(22.0 * z, speed * 0.05 * progress * z)
                tail_pos = screen_pos[0] - dir_vec.x * tail_len, screen_pos[1] - dir_vec.y * tail_len
                pygame.draw.line(surface, self.color, screen_pos, (int(tail_pos[0]), int(tail_pos[1])), width=max(1, int(current_radius)))
            else:
                pygame.draw.circle(surface, self.color, screen_pos, int(current_radius))

        else:
            # Circle
            if current_radius <= 2:
                pygame.draw.circle(surface, self.color, screen_pos, int(current_radius))
            else:
                circ_surf = pygame.Surface((int(current_radius * 2 + 2), int(current_radius * 2 + 2)), pygame.SRCALPHA)
                pygame.draw.circle(circ_surf, (*self.color, alpha), (int(current_radius + 1), int(current_radius + 1)), int(current_radius))
                surface.blit(circ_surf, (screen_pos[0] - int(current_radius + 1), screen_pos[1] - int(current_radius + 1)))


class EffectManager:
    """Manages particles, procedural layered explosions, and screen shake."""

    def __init__(self) -> None:
        self.particles: list[Particle] = []
        self._shake_intensity: float = 0.0
        self._shake_duration: float = 0.0
        self._shake_timer: float = 0.0

    def burst(
        self,
        position: tuple[float, float],
        count: int,
        palette: list[tuple[int, int, int]],
        strength: float = 1.0,
    ) -> None:
        """Emit a burst of radial sparks and colored particles."""
        if not palette:
            palette = [(255, 200, 50), (255, 100, 20), (255, 255, 200)]

        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(60.0, 280.0) * strength
            vel = (speed * math.cos(angle), speed * math.sin(angle))
            color = random.choice(palette)
            lifetime = random.uniform(0.2, 0.6) * strength
            radius = random.uniform(2.0, 5.0) * strength
            kind = random.choice(["circle", "spark", "square"])
            self.particles.append(Particle(position, vel, lifetime, color, radius, kind=kind))

    def explosion(
        self,
        position: tuple[float, float],
        radius: float,
        palette: list[tuple[int, int, int]],
    ) -> None:
        """Create a multi-layered procedural explosion with polygon spikes, shockwave rings, and sparks."""
        if not palette:
            palette = [(255, 240, 150), (255, 140, 30), (220, 40, 20), (80, 80, 80)]

        # 1. Shockwave rings
        self.particles.append(
            Particle(position, (0, 0), lifetime=0.35, color=palette[0], radius=radius * 0.6, kind="ring")
        )
        self.particles.append(
            Particle(position, (0, 0), lifetime=0.45, color=palette[1], radius=radius * 0.9, kind="ring")
        )

        # 2. Jagged polygon shards (fragments)
        for _ in range(12):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(140.0, 380.0) * (radius / 50.0)
            vel = (speed * math.cos(angle), speed * math.sin(angle) - 80.0)
            color = random.choice(palette)
            lifetime = random.uniform(0.35, 0.7)
            shard_r = random.uniform(4.0, 9.0)
            self.particles.append(Particle(position, vel, lifetime, color, shard_r, kind="shard"))

        # 3. Blazing core sparks
        for _ in range(24):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(80.0, 420.0) * (radius / 50.0)
            vel = (speed * math.cos(angle), speed * math.sin(angle))
            color = random.choice(palette[:3])
            lifetime = random.uniform(0.25, 0.55)
            self.particles.append(Particle(position, vel, lifetime, color, random.uniform(2.5, 6.0), kind="spark"))

        # 4. Dense smoke cloud
        for _ in range(10):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(20.0, 90.0)
            vel = (speed * math.cos(angle), speed * math.sin(angle) - 30.0)
            smoke_color = random.choice([(50, 50, 50), (70, 70, 80), (100, 90, 90)])
            lifetime = random.uniform(0.5, 0.9)
            self.particles.append(Particle(position, vel, lifetime, smoke_color, random.uniform(6.0, 14.0), kind="smoke"))

        # Request camera shake
        shake_power = min(22.0, radius * 0.25)
        self.request_shake(intensity=shake_power, duration=0.4)

    def request_shake(self, intensity: float, duration: float) -> None:
        """Request screen shake with clamped intensity and duration."""
        self._shake_intensity = max(self._shake_intensity, min(30.0, intensity))
        self._shake_duration = max(self._shake_duration, duration)
        self._shake_timer = self._shake_duration

    def update(self, dt: float) -> None:
        """Update all active particles and decay screen shake."""
        # Screen shake decay
        if self._shake_timer > 0:
            self._shake_timer -= dt
            if self._shake_timer <= 0:
                self._shake_timer = 0.0
                self._shake_intensity = 0.0
                self._shake_duration = 0.0

        # Update particles
        alive_particles: list[Particle] = []
        for p in self.particles:
            p.update(dt)
            if p.lifetime > 0:
                alive_particles.append(p)
        self.particles = alive_particles

    def draw(self, surface: pygame.Surface, camera: Camera) -> None:
        """Draw all active particles."""
        for p in self.particles:
            p.draw(surface, camera)

    def shake_offset(self) -> tuple[int, int]:
        """Compute the current screen shake offset (dx, dy)."""
        if self._shake_timer <= 0 or self._shake_duration <= 0:
            return (0, 0)
        progress = self._shake_timer / self._shake_duration
        current_amp = self._shake_intensity * progress
        ox = int(random.uniform(-current_amp, current_amp))
        oy = int(random.uniform(-current_amp, current_amp))
        return (ox, oy)

    def clear(self) -> None:
        """Clear all active particles and reset shake."""
        self.particles.clear()
        self._shake_intensity = 0.0
        self._shake_duration = 0.0
        self._shake_timer = 0.0
