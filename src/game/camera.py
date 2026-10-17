"""Camera system with world-to-screen projection, screen shake, and cinematic intro zoom."""

import math
import pygame


class Camera:
    """Manages world view translation, bounds clamping, screen shake, and cinematic zoom intro."""

    def __init__(self, screen_size: tuple[int, int], world_bounds: pygame.Rect) -> None:
        self.screen_width: int = screen_size[0]
        self.screen_height: int = screen_size[1]
        self.world_bounds: pygame.Rect = pygame.Rect(world_bounds)

        # Camera center position and zoom factor
        self.center: pygame.Vector2 = pygame.Vector2(
            self.world_bounds.centerx,
            self.world_bounds.centery,
        )
        self.target: pygame.Vector2 = pygame.Vector2(self.center)
        self.pan_speed: float = 4.5
        self.shake_offset: tuple[int, int] = (0, 0)

        # Zoom state (1.0 = normal 1:1 view, >1.0 = zoomed in closeup)
        self.zoom: float = 1.0
        self.target_zoom: float = 1.0

        # Intro sequence state
        self._intro_active: bool = False
        self._intro_finished: bool = True
        self._intro_phase: int = 0
        self._intro_timer: float = 0.0
        self._left_target: pygame.Vector2 = pygame.Vector2(self.center)
        self._right_target: pygame.Vector2 = pygame.Vector2(self.center)
        self._arena_center: pygame.Vector2 = pygame.Vector2(self.world_bounds.centerx, self.world_bounds.centery)

    def focus(self, target: tuple[float, float], duration: float = 0.8) -> None:
        """Set target center focus point with smooth tracking."""
        self.target = pygame.Vector2(target[0], target[1])
        if duration <= 0:
            self.center = pygame.Vector2(self.target)
        else:
            self.pan_speed = 1.0 / max(0.01, duration)

    def start_intro(self, left_target: tuple[float, float], right_target: tuple[float, float]) -> None:
        """Start the cinematic intro pan with dramatic closeup slow zoom on players."""
        self._left_target = pygame.Vector2(left_target[0], left_target[1])
        self._right_target = pygame.Vector2(right_target[0], right_target[1])
        self._arena_center = pygame.Vector2(self.world_bounds.centerx, self.world_bounds.centery)

        self._intro_active = True
        self._intro_finished = False
        self._intro_phase = 0
        self._intro_timer = 0.0

        # Snap directly to left player and start closeup zoom
        self.center = pygame.Vector2(self._left_target)
        self.target = pygame.Vector2(self._left_target)
        self.zoom = 1.35
        self.target_zoom = 1.75

    def intro_finished(self) -> bool:
        """Check if cinematic intro has completed."""
        return self._intro_finished

    def skip_intro(self) -> None:
        """Instantly skip intro sequence directly to normal gameplay view."""
        self._intro_active = False
        self._intro_finished = True
        self.target = pygame.Vector2(self._arena_center)
        self.center = pygame.Vector2(self._arena_center)
        self.zoom = 1.0
        self.target_zoom = 1.0

    def set_shake(self, offset: tuple[int, int]) -> None:
        """Update current frame shake offset."""
        self.shake_offset = offset

    def update(self, dt: float) -> None:
        """Update camera pan interpolation, slow intro zoom, and bounds clamping."""
        if self._intro_active:
            self._intro_timer += dt

            # Phase 0: Left player closeup focus - slowly zooms in while pausing (2.0s)
            if self._intro_phase == 0:
                self.target = self._left_target
                t = min(1.0, self._intro_timer / 2.0)
                # Slow creeping zoom in on Player 1
                self.zoom = 1.35 + (1.75 - 1.35) * (t * t)
                if self._intro_timer >= 2.0:
                    self._intro_phase = 1
                    self._intro_timer = 0.0
                    self.target = self._right_target

            # Phase 1: Smooth gliding pan across arena to right player (1.4s)
            elif self._intro_phase == 1:
                t = min(1.0, self._intro_timer / 1.4)
                # Smoothstep curve
                t_smooth = t * t * (3.0 - 2.0 * t)
                self.center = self._left_target.lerp(self._right_target, t_smooth)
                # Pull back slightly during pan then re-zoom
                self.zoom = 1.70 - math.sin(t * math.pi) * 0.25
                if self._intro_timer >= 1.4:
                    self._intro_phase = 2
                    self._intro_timer = 0.0
                    self.zoom = 1.45

            # Phase 2: Right player closeup focus - slowly zooms in while pausing (2.0s)
            elif self._intro_phase == 2:
                self.target = self._right_target
                t = min(1.0, self._intro_timer / 2.0)
                # Slow creeping zoom in on Player 2
                self.zoom = 1.45 + (1.78 - 1.45) * (t * t)
                if self._intro_timer >= 2.0:
                    self._intro_phase = 3
                    self._intro_timer = 0.0
                    self.target = self._arena_center

            # Phase 3: Smooth pull back & zoom out to full arena view (1.6s)
            elif self._intro_phase == 3:
                t = min(1.0, self._intro_timer / 1.6)
                t_smooth = t * t * (3.0 - 2.0 * t)
                self.center = self._right_target.lerp(self._arena_center, t_smooth)
                self.zoom = 1.78 + (1.0 - 1.78) * t_smooth
                if self._intro_timer >= 1.6:
                    self._intro_phase = 4
                    self._intro_timer = 0.0
                    self.zoom = 1.0
                    self.target_zoom = 1.0
                    self._intro_active = False
                    self._intro_finished = True

        else:
            # Standard gameplay smooth camera tracking
            rate = min(1.0, dt * self.pan_speed * 2.5)
            self.center = self.center.lerp(self.target, rate)
            # Smooth zoom adjustment
            self.zoom += (self.target_zoom - self.zoom) * min(1.0, dt * 4.0)

        # Clamping camera center so viewport stays inside world bounds
        vis_w = self.screen_width / self.zoom
        vis_h = self.screen_height / self.zoom
        half_w = vis_w / 2.0
        half_h = vis_h / 2.0

        if self.world_bounds.width >= vis_w:
            self.center.x = max(self.world_bounds.left + half_w, min(self.world_bounds.right - half_w, self.center.x))
        else:
            self.center.x = self.world_bounds.centerx

        if self.world_bounds.height >= vis_h:
            self.center.y = max(self.world_bounds.top + half_h, min(self.world_bounds.bottom - half_h, self.center.y))
        else:
            self.center.y = self.world_bounds.centery

    @property
    def top_left(self) -> pygame.Vector2:
        """Top-left corner of the visible viewport in world coordinates."""
        vis_w = self.screen_width / self.zoom
        vis_h = self.screen_height / self.zoom
        return pygame.Vector2(
            self.center.x - vis_w / 2.0,
            self.center.y - vis_h / 2.0,
        )

    def apply(self, position: tuple[float, float]) -> tuple[int, int]:
        """Convert world coordinates (wx, wy) to screen coordinates (sx, sy) with zoom and shake."""
        sx = int((position[0] - self.center.x) * self.zoom + self.screen_width / 2.0 + self.shake_offset[0])
        sy = int((position[1] - self.center.y) * self.zoom + self.screen_height / 2.0 + self.shake_offset[1])
        return (sx, sy)

    def apply_rect(self, rect: pygame.Rect) -> pygame.Rect:
        """Convert a world-space pygame.Rect to screen-space with zoom applied."""
        sx, sy = self.apply((rect.x, rect.y))
        sw = max(1, int(rect.width * self.zoom))
        sh = max(1, int(rect.height * self.zoom))
        return pygame.Rect(sx, sy, sw, sh)

    def world_rect(self) -> pygame.Rect:
        """Currently visible viewport rectangle in world coordinates."""
        tl = self.top_left
        vis_w = int(self.screen_width / self.zoom)
        vis_h = int(self.screen_height / self.zoom)
        return pygame.Rect(int(tl.x), int(tl.y), vis_w, vis_h)
