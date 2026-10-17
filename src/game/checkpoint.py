"""Checkpoint system and shop menu for upgrading player abilities."""

from __future__ import annotations
from enum import Enum
import math
from typing import TYPE_CHECKING
import pygame

if TYPE_CHECKING:
    from src.game.player import Player
    from src.game.settings import GameConfig


class UpgradeType(Enum):
    """Available player upgrade choices at each checkpoint."""

    ATTACK_SPEED = "attack_speed"
    ATTACK_DAMAGE = "attack_damage"


class ShopMenu:
    """Screen-space interactive shop menu presented at checkpoints."""

    def __init__(self, config: GameConfig) -> None:
        self.config: GameConfig = config
        self.sw: int = config.screen_width
        self.sh: int = config.screen_height

        pygame.font.init()
        font_name = "georgia" if "georgia" in pygame.font.get_fonts() else None
        self.title_font = pygame.font.SysFont(font_name, 44, bold=True)
        self.sub_font = pygame.font.SysFont(font_name, 22, bold=True)
        self.card_title_font = pygame.font.SysFont(font_name, 24, bold=True)
        self.badge_font = pygame.font.SysFont(font_name, 16, bold=True)
        self.body_font = pygame.font.SysFont(font_name, 16)
        self.stat_font = pygame.font.SysFont(font_name, 18, bold=True)
        self.button_font = pygame.font.SysFont(font_name, 19, bold=True)
        self.footer_font = pygame.font.SysFont(font_name, 15)

        # Card geometries
        card_w, card_h = 420, 390
        gap = 48
        total_w = card_w * 2 + gap
        start_x = (self.sw - total_w) // 2
        card_y = 200

        self.speed_card_rect = pygame.Rect(start_x, card_y, card_w, card_h)
        self.damage_card_rect = pygame.Rect(start_x + card_w + gap, card_y, card_w, card_h)

        # Button sub-rectangles inside cards
        btn_w, btn_h = 320, 48
        self.speed_btn_rect = pygame.Rect(
            self.speed_card_rect.centerx - btn_w // 2,
            self.speed_card_rect.bottom - 66,
            btn_w,
            btn_h,
        )
        self.damage_btn_rect = pygame.Rect(
            self.damage_card_rect.centerx - btn_w // 2,
            self.damage_card_rect.bottom - 66,
            btn_w,
            btn_h,
        )

        self.selected_index: int = 0  # 0: speed, 1: damage
        self.hovered_index: int | None = None
        self.anim_time: float = 0.0

        # State tracking for display
        self.checkpoint_num: int = 1
        self.max_checkpoints: int = 3
        self.current_speed: float = 1.0
        self.current_damage: float = 1.0

    def open(
        self,
        checkpoint_num: int,
        max_checkpoints: int,
        current_speed: float,
        current_damage: float,
    ) -> None:
        """Activate the shop display with fresh player state."""
        self.checkpoint_num = checkpoint_num
        self.max_checkpoints = max_checkpoints
        self.current_speed = current_speed
        self.current_damage = current_damage
        self.selected_index = 0
        self.hovered_index = None
        self.anim_time = 0.0

    def handle_event(self, event: pygame.event.Event) -> UpgradeType | None:
        """Handle keyboard navigation and mouse interactions."""
        if event.type == pygame.MOUSEMOTION:
            mx, my = event.pos
            if self.speed_card_rect.collidepoint(mx, my):
                self.hovered_index = 0
                self.selected_index = 0
            elif self.damage_card_rect.collidepoint(mx, my):
                self.hovered_index = 1
                self.selected_index = 1
            else:
                self.hovered_index = None

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            if self.speed_card_rect.collidepoint(mx, my):
                return UpgradeType.ATTACK_SPEED
            elif self.damage_card_rect.collidepoint(mx, my):
                return UpgradeType.ATTACK_DAMAGE

        elif event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_1, pygame.K_KP1):
                return UpgradeType.ATTACK_SPEED
            elif event.key in (pygame.K_2, pygame.K_KP2):
                return UpgradeType.ATTACK_DAMAGE
            elif event.key in (pygame.K_LEFT, pygame.K_a):
                self.selected_index = 0
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self.selected_index = 1
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                if self.selected_index == 0:
                    return UpgradeType.ATTACK_SPEED
                elif self.selected_index == 1:
                    return UpgradeType.ATTACK_DAMAGE

        return None

    def update(self, dt: float) -> None:
        """Advance procedural animations."""
        self.anim_time += dt

    def draw(self, surface: pygame.Surface, player: Player) -> None:
        """Render atmospheric checkpoint modal and the two upgrade cards."""
        # 1. Dark semi-transparent backdrop
        overlay = pygame.Surface((self.sw, self.sh), pygame.SRCALPHA)
        overlay.fill((8, 12, 20, 225))
        surface.blit(overlay, (0, 0))

        # 2. Header banner & title
        pulse = (math.sin(self.anim_time * 3.0) + 1.0) * 0.5
        title_y = 54

        title_surf = self.title_font.render("CHECKPOINT REACHED!", True, (255, 225, 90))
        t_rect = title_surf.get_rect(center=(self.sw // 2, title_y))
        surface.blit(title_surf, t_rect)

        # Replenished timer highlight badge
        sub_text = (
            f"Checkpoint {self.checkpoint_num} of {self.max_checkpoints}  •  "
            "Timer Fully Replenished!"
        )
        glow_color = (
            int(100 + 40 * pulse),
            int(235 + 20 * pulse),
            int(160 + 40 * pulse),
        )
        sub_surf = self.sub_font.render(sub_text, True, glow_color)
        s_rect = sub_surf.get_rect(center=(self.sw // 2, title_y + 44))
        surface.blit(sub_surf, s_rect)

        hint_text = "Select an upgrade to strengthen your hero for the upcoming horde:"
        hint_surf = self.body_font.render(hint_text, True, (200, 210, 225))
        h_rect = hint_surf.get_rect(center=(self.sw // 2, title_y + 78))
        surface.blit(hint_surf, h_rect)

        # 3. Draw Upgrade Card 1: Attack Speed
        speed_selected = (self.selected_index == 0)
        self._draw_speed_card(surface, self.speed_card_rect, self.speed_btn_rect, speed_selected, player)

        # 4. Draw Upgrade Card 2: Attack Damage
        damage_selected = (self.selected_index == 1)
        self._draw_damage_card(surface, self.damage_card_rect, self.damage_btn_rect, damage_selected, player)

        # 5. Footer navigation controls
        footer_text = "Click to select, or press [1] / [2], or use Arrow Keys + [ENTER / SPACE]"
        f_surf = self.footer_font.render(footer_text, True, (160, 175, 195))
        f_rect = f_surf.get_rect(center=(self.sw // 2, self.sh - 40))
        surface.blit(f_surf, f_rect)

    def _draw_speed_card(
        self,
        surface: pygame.Surface,
        rect: pygame.Rect,
        btn_rect: pygame.Rect,
        is_selected: bool,
        player: Player,
    ) -> None:
        """Render the Attack Speed upgrade card."""
        # Colors
        accent_color = (80, 220, 255)
        border_color = (120, 240, 255) if is_selected else (50, 110, 150)
        bg_color = (22, 34, 52) if is_selected else (16, 24, 38)

        # Card base
        card_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(card_surf, bg_color, (0, 0, rect.width, rect.height), border_radius=12)
        if is_selected:
            # Highlight glow border
            pygame.draw.rect(card_surf, (80, 220, 255, 60), (0, 0, rect.width, rect.height), width=6, border_radius=12)
        pygame.draw.rect(card_surf, border_color, (0, 0, rect.width, rect.height), width=2, border_radius=12)
        surface.blit(card_surf, rect.topleft)

        # Top decorative icon: Fast Energy Lightning
        icon_cx = rect.centerx
        icon_cy = rect.top + 60
        pygame.draw.circle(surface, (20, 45, 65), (icon_cx, icon_cy), 32)
        pygame.draw.circle(surface, accent_color, (icon_cx, icon_cy), 32, width=2)

        # Lightning bolt shape
        bolt_points = [
            (icon_cx + 4, icon_cy - 18),
            (icon_cx - 10, icon_cy + 2),
            (icon_cx + 2, icon_cy + 2),
            (icon_cx - 4, icon_cy + 18),
            (icon_cx + 12, icon_cy - 2),
            (icon_cx, icon_cy - 2),
        ]
        pygame.draw.polygon(surface, (120, 245, 255), bolt_points)
        pygame.draw.polygon(surface, (255, 255, 255), bolt_points, width=1)

        # Card Title
        title = self.card_title_font.render("INCREASE ATTACK SPEED", True, (245, 250, 255))
        surface.blit(title, title.get_rect(center=(icon_cx, rect.top + 120)))

        # Badge tag
        badge_rect = pygame.Rect(icon_cx - 90, rect.top + 144, 180, 26)
        pygame.draw.rect(surface, (25, 75, 105), badge_rect, border_radius=13)
        pygame.draw.rect(surface, accent_color, badge_rect, width=1, border_radius=13)
        badge_text = self.badge_font.render("+25% ATTACK SPEED", True, accent_color)
        surface.blit(badge_text, badge_text.get_rect(center=badge_rect.center))

        # Description
        desc_1 = self.body_font.render("Reduces weapon and attack cooldowns.", True, (190, 205, 225))
        desc_2 = self.body_font.render("Strike rapidly to chain hits and restore timer!", True, (160, 180, 205))
        surface.blit(desc_1, desc_1.get_rect(center=(icon_cx, rect.top + 195)))
        surface.blit(desc_2, desc_2.get_rect(center=(icon_cx, rect.top + 220)))

        # Stat Preview
        cur_sp = getattr(player, "attack_speed_multiplier", self.current_speed)
        next_sp = cur_sp + 0.25
        stat_text = f"Speed Multiplier: {cur_sp:.2f}x  ->  {next_sp:.2f}x"
        stat_surf = self.stat_font.render(stat_text, True, (255, 230, 110))
        surface.blit(stat_surf, stat_surf.get_rect(center=(icon_cx, rect.top + 265)))

        # Action Button
        btn_bg = (50, 120, 170) if is_selected else (28, 48, 70)
        btn_border = (120, 240, 255) if is_selected else (70, 110, 140)
        btn_txt_col = (255, 255, 255) if is_selected else (210, 225, 240)
        pygame.draw.rect(surface, btn_bg, btn_rect, border_radius=8)
        pygame.draw.rect(surface, btn_border, btn_rect, width=2, border_radius=8)
        btn_surf = self.button_font.render("[ 1 ] SELECT ATTACK SPEED", True, btn_txt_col)
        surface.blit(btn_surf, btn_surf.get_rect(center=btn_rect.center))

    def _draw_damage_card(
        self,
        surface: pygame.Surface,
        rect: pygame.Rect,
        btn_rect: pygame.Rect,
        is_selected: bool,
        player: Player,
    ) -> None:
        """Render the Attack Damage upgrade card."""
        # Colors
        accent_color = (255, 120, 60)
        border_color = (255, 170, 90) if is_selected else (140, 65, 45)
        bg_color = (52, 28, 24) if is_selected else (38, 20, 18)

        # Card base
        card_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(card_surf, bg_color, (0, 0, rect.width, rect.height), border_radius=12)
        if is_selected:
            pygame.draw.rect(card_surf, (255, 120, 60, 60), (0, 0, rect.width, rect.height), width=6, border_radius=12)
        pygame.draw.rect(card_surf, border_color, (0, 0, rect.width, rect.height), width=2, border_radius=12)
        surface.blit(card_surf, rect.topleft)

        # Top decorative icon: Spiked Broadsword
        icon_cx = rect.centerx
        icon_cy = rect.top + 60
        pygame.draw.circle(surface, (65, 30, 22), (icon_cx, icon_cy), 32)
        pygame.draw.circle(surface, accent_color, (icon_cx, icon_cy), 32, width=2)

        # Crossed sword / fiery blade procedural shape
        blade_points = [
            (icon_cx, icon_cy - 20),
            (icon_cx + 7, icon_cy + 4),
            (icon_cx - 7, icon_cy + 4),
        ]
        pygame.draw.polygon(surface, (255, 180, 80), blade_points)
        pygame.draw.polygon(surface, (255, 240, 200), blade_points, width=1)
        # Crossguard and handle
        pygame.draw.line(surface, (240, 140, 50), (icon_cx - 12, icon_cy + 5), (icon_cx + 12, icon_cy + 5), width=3)
        pygame.draw.line(surface, (150, 90, 50), (icon_cx, icon_cy + 5), (icon_cx, icon_cy + 17), width=3)
        pygame.draw.circle(surface, (240, 140, 50), (icon_cx, icon_cy + 18), 3)

        # Card Title
        title = self.card_title_font.render("INCREASE ATTACK DAMAGE", True, (255, 245, 245))
        surface.blit(title, title.get_rect(center=(icon_cx, rect.top + 120)))

        # Badge tag
        badge_rect = pygame.Rect(icon_cx - 95, rect.top + 144, 190, 26)
        pygame.draw.rect(surface, (95, 38, 28), badge_rect, border_radius=13)
        pygame.draw.rect(surface, accent_color, badge_rect, width=1, border_radius=13)
        badge_text = self.badge_font.render("+30% ATTACK DAMAGE", True, accent_color)
        surface.blit(badge_text, badge_text.get_rect(center=badge_rect.center))

        # Description
        desc_1 = self.body_font.render("Boosts damage dealt by all strikes & weapons.", True, (225, 200, 195))
        desc_2 = self.body_font.render("Eliminate aggressive zombies with fewer hits!", True, (205, 175, 170))
        surface.blit(desc_1, desc_1.get_rect(center=(icon_cx, rect.top + 195)))
        surface.blit(desc_2, desc_2.get_rect(center=(icon_cx, rect.top + 220)))

        # Stat Preview
        cur_dmg = getattr(player, "attack_damage_multiplier", self.current_damage)
        next_dmg = cur_dmg + 0.30
        stat_text = f"Damage Multiplier: {cur_dmg:.2f}x  ->  {next_dmg:.2f}x"
        stat_surf = self.stat_font.render(stat_text, True, (255, 230, 110))
        surface.blit(stat_surf, stat_surf.get_rect(center=(icon_cx, rect.top + 265)))

        # Action Button
        btn_bg = (170, 60, 40) if is_selected else (65, 28, 24)
        btn_border = (255, 160, 100) if is_selected else (130, 60, 50)
        btn_txt_col = (255, 255, 255) if is_selected else (240, 215, 210)
        pygame.draw.rect(surface, btn_bg, btn_rect, border_radius=8)
        pygame.draw.rect(surface, btn_border, btn_rect, width=2, border_radius=8)
        btn_surf = self.button_font.render("[ 2 ] SELECT ATTACK DAMAGE", True, btn_txt_col)
        surface.blit(btn_surf, btn_surf.get_rect(center=btn_rect.center))


class CheckpointManager:
    """Manages wave progression, checkpoint triggers, shop opening, and boss readiness."""

    def __init__(
        self,
        config: GameConfig,
        waves_per_checkpoint: int = 5,
        max_checkpoints: int = 3,
    ) -> None:
        self.config: GameConfig = config
        self.waves_per_checkpoint: int = waves_per_checkpoint
        self.max_checkpoints: int = max_checkpoints

        self.current_wave: int = 1
        self.checkpoints_reached: int = 0
        self.is_shop_open: bool = False
        self.is_boss_ready: bool = False
        self.last_upgrade_selected: UpgradeType | None = None

        self.shop: ShopMenu = ShopMenu(config)

    def reset(self) -> None:
        """Reset wave and checkpoint progression for a new run."""
        self.current_wave = 1
        self.checkpoints_reached = 0
        self.is_shop_open = False
        self.is_boss_ready = False
        self.last_upgrade_selected = None

    def complete_wave(self, player: Player) -> bool:
        """Record completion of a wave. Triggers checkpoint every 5 waves."""
        # Check if current wave finishes a 5-wave set
        reached_checkpoint = (
            self.current_wave > 0
            and self.current_wave % self.waves_per_checkpoint == 0
            and self.checkpoints_reached < self.max_checkpoints
        )

        self.current_wave += 1

        if reached_checkpoint:
            self.trigger_checkpoint(player)
            return True

        return False

    def trigger_checkpoint(self, player: Player) -> None:
        """Trigger checkpoint: replenish timer fully and open shop menu."""
        self.checkpoints_reached += 1

        # 1. Fully replenish timer
        if hasattr(player, "replenish_timer"):
            player.replenish_timer()

        # 2. Check if boss fight should begin after 3 checkpoints
        if self.checkpoints_reached >= self.max_checkpoints:
            self.is_boss_ready = True

        # 3. Open shop menu
        speed_mult = getattr(player, "attack_speed_multiplier", 1.0)
        damage_mult = getattr(player, "attack_damage_multiplier", 1.0)
        self.shop.open(
            checkpoint_num=self.checkpoints_reached,
            max_checkpoints=self.max_checkpoints,
            current_speed=speed_mult,
            current_damage=damage_mult,
        )
        self.is_shop_open = True

    def handle_event(self, event: pygame.event.Event, player: Player) -> UpgradeType | None:
        """Route event to shop menu when open, applying selected upgrade."""
        if not self.is_shop_open:
            return None

        chosen_upgrade = self.shop.handle_event(event)
        if chosen_upgrade is not None:
            self.apply_upgrade(player, chosen_upgrade)
            self.is_shop_open = False
            self.last_upgrade_selected = chosen_upgrade
            return chosen_upgrade

        return None

    def apply_upgrade(self, player: Player, upgrade: UpgradeType) -> None:
        """Apply chosen upgrade effect to the player."""
        if upgrade == UpgradeType.ATTACK_SPEED:
            if hasattr(player, "upgrade_attack_speed"):
                player.upgrade_attack_speed(0.25)
            else:
                player.attack_speed_multiplier = getattr(player, "attack_speed_multiplier", 1.0) + 0.25

        elif upgrade == UpgradeType.ATTACK_DAMAGE:
            if hasattr(player, "upgrade_attack_damage"):
                player.upgrade_attack_damage(0.30)
            else:
                player.attack_damage_multiplier = getattr(player, "attack_damage_multiplier", 1.0) + 0.30

    def update(self, dt: float) -> None:
        """Update shop animations when active."""
        if self.is_shop_open:
            self.shop.update(dt)

    def draw(self, surface: pygame.Surface, player: Player) -> None:
        """Render shop menu overlay onto the game surface."""
        if self.is_shop_open:
            self.shop.draw(surface, player)
