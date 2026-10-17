"""Shared constants and configuration for the game."""

import pathlib
import pygame

# Constants
SCREEN_WIDTH: int = 1280
SCREEN_HEIGHT: int = 720
FPS: int = 60
TITLE: str = "Wizards Duel: Stickman Arena"
GROUND_Y: int = 650
PLAYER_MAX_HEALTH: int = 100
ITEM_SPAWN_INTERVAL: float = 4.5
INTRO_FOCUS_SECONDS: float = 2.0
ASSET_DIR: pathlib.Path = pathlib.Path(__file__).resolve().parent.parent.parent / "assets"


class Controls:
    """Configurable controls for both players."""

    def __init__(self, left: dict[str, int] | None = None, right: dict[str, int] | None = None) -> None:
        self.left: dict[str, int] = left or {
            "left": pygame.K_a,
            "right": pygame.K_d,
            "jump": pygame.K_w,
            "down": pygame.K_s,
            "attack": pygame.K_f,
            "attack_alt": pygame.K_s,
        }
        self.right: dict[str, int] = right or {
            "left": pygame.K_LEFT,
            "right": pygame.K_RIGHT,
            "jump": pygame.K_UP,
            "down": pygame.K_DOWN,
            "attack": pygame.K_RSHIFT,
            "attack_alt": pygame.K_DOWN,
        }


class GameConfig:
    """Central game configuration."""

    def __init__(self) -> None:
        self.screen_width: int = SCREEN_WIDTH
        self.screen_height: int = SCREEN_HEIGHT
        self.screen_size: tuple[int, int] = (SCREEN_WIDTH, SCREEN_HEIGHT)
        self.fps: int = FPS
        self.gravity: float = 1320.0
        self.movement_speeds: float = 360.0
        self.move_speed: float = self.movement_speeds
        self.jump_strength: float = 650.0
        self.player_health: int = PLAYER_MAX_HEALTH
        self.spawn_interval: float = ITEM_SPAWN_INTERVAL
        self.intro_durations: float = INTRO_FOCUS_SECONDS
        self.ground_y: int = GROUND_Y
        self.title: str = TITLE
        self.asset_dir: pathlib.Path = ASSET_DIR
        self.controls: Controls = Controls()
