"""User interface: atmospheric title menu, screen-space HUD, and result screen."""

from __future__ import annotations
import math
import random
from typing import TYPE_CHECKING
import pygame

if TYPE_CHECKING:
    from src.game.player import Player
    from src.game.settings import GameConfig


class UI:
    """Screen-space UI manager for menus, HUD bars, and round victory results."""

    def __init__(self, config: GameConfig) -> None:
        self.config: GameConfig = config
        self.sw: int = config.screen_width
        self.sh: int = config.screen_height

        # Initialize fonts safely
        pygame.font.init()
        font_name = "georgia" if "georgia" in pygame.font.get_fonts() else None
        self.title_font = pygame.font.SysFont(font_name, 56, bold=True)
        self.header_font = pygame.font.SysFont(font_name, 32, bold=True)
        self.button_font = pygame.font.SysFont(font_name, 24, bold=True)
        self.hud_font = pygame.font.SysFont(font_name, 18, bold=True)
        self.small_font = pygame.font.SysFont(font_name, 14)

        # Button rects
        btn_w, btn_h = 240, 54
        self.start_btn: pygame.Rect = pygame.Rect((self.sw - btn_w) // 2, self.sh - 140, btn_w, btn_h)
        self.restart_btn: pygame.Rect = pygame.Rect(self.sw // 2 - 220, self.sh // 2 + 70, 200, 50)
        self.menu_btn: pygame.Rect = pygame.Rect(self.sw // 2 + 20, self.sh // 2 + 70, 200, 50)
        self.test_checkpoint_btn: pygame.Rect = pygame.Rect(self.sw - 270, 18, 240, 42)

        # Menu procedural starfield / floating dust
        self._menu_time: float = 0.0
        self._stars: list[dict[str, float]] = [
            {
                "x": random.uniform(0, self.sw),
                "y": random.uniform(0, self.sh),
                "speed": random.uniform(15.0, 45.0),
                "size": random.uniform(1.5, 3.5),
                "phase": random.uniform(0, 6.28),
            }
            for _ in range(65)
        ]

    def handle_event(self, event: pygame.event.Event) -> str | None:
        """Process UI interactions and return action string or None."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            if self.start_btn.collidepoint(mx, my):
                return "start"
            if self.restart_btn.collidepoint(mx, my):
                return "restart"
            if self.menu_btn.collidepoint(mx, my):
                return "menu"
            if self.test_checkpoint_btn.collidepoint(mx, my):
                return "skip_checkpoint"

        elif event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                return "start"
            elif event.key == pygame.K_r:
                return "restart"
            elif event.key == pygame.K_ESCAPE:
                return "menu"
            elif event.key in (pygame.K_c, pygame.K_t):
                return "skip_checkpoint"

        return None

    def draw_button(
        self,
        surface: pygame.Surface,
        rect: pygame.Rect,
        text: str,
        hovered: bool = False,
    ) -> None:
        """Render a button using procedural gold bevels and magical corners."""
        # Colors
        if hovered:
            bg_color = (48, 38, 70)
            border_color = (255, 230, 90)
            text_color = (255, 255, 220)
        else:
            bg_color = (26, 22, 38)
            border_color = (210, 175, 60)
            text_color = (240, 230, 200)

        # Base button rect
        pygame.draw.rect(surface, bg_color, rect, border_radius=6)
        pygame.draw.rect(surface, border_color, rect, width=2, border_radius=6)

        # Four decorative gold squares in corners
        sq = 4
        pygame.draw.rect(surface, border_color, (rect.left + 3, rect.top + 3, sq, sq))
        pygame.draw.rect(surface, border_color, (rect.right - 3 - sq, rect.top + 3, sq, sq))
        pygame.draw.rect(surface, border_color, (rect.left + 3, rect.bottom - 3 - sq, sq, sq))
        pygame.draw.rect(surface, border_color, (rect.right - 3 - sq, rect.bottom - 3 - sq, sq, sq))

        # Centered text
        txt_surf = self.button_font.render(text, True, text_color)
        t_rect = txt_surf.get_rect(center=rect.center)
        surface.blit(txt_surf, t_rect)

    def draw_menu(self, surface: pygame.Surface, dt: float) -> None:
        """Render atmospheric title menu with animated floating particles and control cards."""
        self._menu_time += dt

        # Deep magical gradient background
        surface.fill((11, 14, 25))

        # Floating procedural stars
        for st in self._stars:
            st["y"] -= st["speed"] * dt
            if st["y"] < 0:
                st["y"] = self.sh
                st["x"] = random.uniform(0, self.sw)

            alpha_sin = math.sin(self._menu_time * 2.0 + st["phase"]) * 0.4 + 0.6
            star_color = (
                int(220 * alpha_sin),
                int(210 * alpha_sin),
                int(255 * alpha_sin),
            )
            pygame.draw.circle(surface, star_color, (int(st["x"]), int(st["y"])), max(1, int(st["size"])))

        # Title banner
        title_y = 110 + int(math.sin(self._menu_time * 1.5) * 6.0)
        # Shadow
        shadow_surf = self.title_font.render(self.config.title, True, (20, 10, 30))
        surface.blit(shadow_surf, shadow_surf.get_rect(center=(self.sw // 2 + 3, title_y + 3)))

        # Glowing gold title text
        glow_color = (255, 215, 60)
        title_surf = self.title_font.render(self.config.title, True, glow_color)
        surface.blit(title_surf, title_surf.get_rect(center=(self.sw // 2, title_y)))

        # Subtitle
        sub_surf = self.hud_font.render("Fast-Paced Local 2-Player Stickman Arena", True, (180, 195, 225))
        surface.blit(sub_surf, sub_surf.get_rect(center=(self.sw // 2, title_y + 55)))

        # Controls Cards (Player 1 left, Player 2 right)
        card_w, card_h = 320, 220
        card_y = self.sh // 2 - 50

        # --- Left Player Card (Gryffindor) ---
        p1_rect = pygame.Rect(self.sw // 2 - card_w - 40, card_y, card_w, card_h)
        pygame.draw.rect(surface, (30, 20, 28, 220), p1_rect, border_radius=8)
        pygame.draw.rect(surface, (196, 30, 58), p1_rect, width=2, border_radius=8)

        p1_title = self.header_font.render("PLAYER 1 (Crimson)", True, (255, 215, 80))
        surface.blit(p1_title, (p1_rect.x + 20, p1_rect.y + 18))

        lines_p1 = [
            "Move:  A  /  D",
            "Jump / Wall-Jump:  W",
            "Attack / Use Item:  S or F",
            "Hold attack for Auto Weapons",
        ]
        for i, line in enumerate(lines_p1):
            txt = self.hud_font.render(line, True, (230, 230, 235))
            surface.blit(txt, (p1_rect.x + 20, p1_rect.y + 70 + i * 32))

        # --- Right Player Card (Slytherin) ---
        p2_rect = pygame.Rect(self.sw // 2 + 40, card_y, card_w, card_h)
        pygame.draw.rect(surface, (18, 30, 26, 220), p2_rect, border_radius=8)
        pygame.draw.rect(surface, (27, 100, 75), p2_rect, width=2, border_radius=8)

        p2_title = self.header_font.render("PLAYER 2 (Emerald)", True, (160, 240, 200))
        surface.blit(p2_title, (p2_rect.x + 20, p2_rect.y + 18))

        lines_p2 = [
            "Move:  LEFT  /  RIGHT",
            "Jump / Wall-Jump:  UP",
            "Attack / Use Item:  DOWN or RSHIFT",
            "Hold attack for Auto Weapons",
        ]
        for i, line in enumerate(lines_p2):
            txt = self.hud_font.render(line, True, (230, 230, 235))
            surface.blit(txt, (p2_rect.x + 20, p2_rect.y + 70 + i * 32))

        # Start Button
        mx, my = pygame.mouse.get_pos()
        hovered = self.start_btn.collidepoint(mx, my)
        self.draw_button(surface, self.start_btn, "START DUEL (Enter)", hovered=hovered)

    def draw_hud(
        self,
        surface: pygame.Surface,
        left: Player,
        right: Player | None = None,
        checkpoint_manager: any = None,
    ) -> None:
        """Render single-player HUD bars, timer status, and interactive checkpoint skip button."""
        bar_w = 340
        bar_h = 24
        margin = 32

        # ================= HERO HEALTH =================
        p1_name = self.hud_font.render("HERO", True, (255, 215, 80))
        surface.blit(p1_name, (margin, margin - 22))

        # Health Bar Background
        p1_bg_rect = pygame.Rect(margin, margin, bar_w, bar_h)
        pygame.draw.rect(surface, (25, 20, 25), p1_bg_rect, border_radius=4)

        # Health Bar Fill
        p1_ratio = max(0.0, min(1.0, left.health / float(self.config.player_health)))
        if p1_ratio > 0:
            p1_fill_rect = pygame.Rect(margin, margin, int(bar_w * p1_ratio), bar_h)
            fill_color = (196, 30, 58) if p1_ratio > 0.25 else (220, 40, 20)
            pygame.draw.rect(surface, fill_color, p1_fill_rect, border_radius=4)

        # Health Bar Border
        pygame.draw.rect(surface, (220, 190, 80), p1_bg_rect, width=2, border_radius=4)

        # Health Numbers
        hp_str = f"{int(left.health)} / {self.config.player_health} HP"
        hp_surf = self.small_font.render(hp_str, True, (255, 255, 255))
        surface.blit(hp_surf, (margin + 8, margin + 4))

        # ================= TIMER & COMBAT STATS =================
        box_rect = pygame.Rect(margin, margin + bar_h + 8, 300, 34)
        pygame.draw.rect(surface, (18, 22, 32), box_rect, border_radius=6)
        pygame.draw.rect(surface, (80, 100, 130), box_rect, width=1, border_radius=6)

        timer_val = max(0.0, getattr(left, "timer", 60.0))
        spd_val = getattr(left, "attack_speed_multiplier", 1.0)
        dmg_val = getattr(left, "attack_damage_multiplier", 1.0)
        stats_str = f"TIME: {timer_val:.1f}s   SPD: {spd_val:.2f}x   DMG: {dmg_val:.2f}x"
        it_surf = self.hud_font.render(stats_str, True, (245, 220, 110))
        surface.blit(it_surf, (box_rect.x + 10, box_rect.y + 7))

        # ================= TEST CHECKPOINT BUTTON (Top-Right) =================
        mx, my = pygame.mouse.get_pos()
        btn_hovered = self.test_checkpoint_btn.collidepoint(mx, my)
        btn_bg = (55, 42, 22) if btn_hovered else (32, 26, 18)
        btn_border = (255, 220, 90) if btn_hovered else (200, 165, 60)
        btn_txt_col = (255, 255, 220) if btn_hovered else (235, 215, 170)

        pygame.draw.rect(surface, btn_bg, self.test_checkpoint_btn, border_radius=8)
        pygame.draw.rect(surface, btn_border, self.test_checkpoint_btn, width=2, border_radius=8)
        btn_text = "⚡ SKIP TO CHECKPOINT [C]"
        btn_surf = self.hud_font.render(btn_text, True, btn_txt_col)
        surface.blit(btn_surf, btn_surf.get_rect(center=self.test_checkpoint_btn.center))

        # Checkpoint / Wave Tracker text below button
        chk_count = getattr(checkpoint_manager, "checkpoints_reached", 0) if checkpoint_manager else 0
        wave_num = getattr(checkpoint_manager, "current_wave", 1) if checkpoint_manager else 1
        tracker_str = f"CHECKPOINTS: {chk_count}/3   |   WAVE: {wave_num}"
        tracker_surf = self.small_font.render(tracker_str, True, (180, 210, 240))
        surface.blit(tracker_surf, (self.sw - 270, 68))

    def draw_result(self, surface: pygame.Surface, winner: Player | None = None) -> None:
        """Render victory or defeat result screen overlay."""
        # Dim backdrop
        dim_surf = pygame.Surface((self.sw, self.sh), pygame.SRCALPHA)
        dim_surf.fill((10, 12, 18, 200))
        surface.blit(dim_surf, (0, 0))

        # Result card
        card_w, card_h = 560, 300
        card_rect = pygame.Rect((self.sw - card_w) // 2, (self.sh - card_h) // 2 - 30, card_w, card_h)
        pygame.draw.rect(surface, (24, 26, 38), card_rect, border_radius=10)

        is_win = (winner is not None and winner.alive())
        border_col = (255, 215, 60) if is_win else (220, 50, 40)
        pygame.draw.rect(surface, border_col, card_rect, width=3, border_radius=10)

        # Title
        title_text = "VICTORY!" if is_win else "GAME OVER"
        title_col = (255, 230, 120) if is_win else (240, 70, 60)
        vic_surf = self.title_font.render(title_text, True, title_col)
        surface.blit(vic_surf, vic_surf.get_rect(center=(self.sw // 2, card_rect.y + 55)))

        # Subtitle
        sub_label = "You survived the zombie onslaught!" if is_win else "You were overrun by the horde..."
        sub_surf = self.header_font.render(sub_label, True, (220, 225, 235))
        surface.blit(sub_surf, sub_surf.get_rect(center=(self.sw // 2, card_rect.y + 120)))

        # Buttons
        mx, my = pygame.mouse.get_pos()
        r_hover = self.restart_btn.collidepoint(mx, my)
        m_hover = self.menu_btn.collidepoint(mx, my)

        self.draw_button(surface, self.restart_btn, "RESTART (R)", hovered=r_hover)
        self.draw_button(surface, self.menu_btn, "MAIN MENU (Esc)", hovered=m_hover)
