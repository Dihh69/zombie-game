# CONTEXT.md

## Game contract

**Stack:** Python 3.14, `pygame-ce`, initialized with `uv init`. Entry
point: `src/main.py`. Run with `uv run python -m src.main` (or adjust to
the repository's chosen package layout). Assets live under root
`assets/`; paths must be resolved from the project root, never the
current working directory. Missing assets must degrade gracefully to
coded placeholders.

**Game:** A visually expressive, local two-player Harry-Potter-inspired
stickman arena fighter. The left player spawns on the left and the right
player on the right. Both can run, jump, wall-jump, and use platforms to
move around the arena. Magical/weapon items fall from the sky; players
compete to collect them and fire them at the opponent. The first player
whose health reaches zero loses. Keep modules independent: each teammate
implements only their assigned file and must preserve the signatures
below.

### Game flow and presentation

-   **Menu:** atmospheric title screen, animated/aesthetic background,
    prominent Start button. Clicking Start enters the intro sequence.
-   **Intro camera:** pan/focus on the left player for a couple of
    seconds, then the right player for a couple of seconds, with a brief
    pause at each focus; then smoothly reveal the full arena and begin
    normal play. Intro timing must not block the game loop.
-   **Play:** platforms, two players, item spawner, projectiles, health
    bars, impact effects, and screen shake. Update simulation with `dt`
    in seconds; render separately.
-   **Combat:** collect an item by touching it. A player can hold one
    active item; collecting another replaces the current one (the
    previous item is dropped or discarded consistently). Attack input
    fires/uses the held item. Face direction determines firing
    direction. Hits reduce the opponent's health; never damage the
    owner. Bombs explode on contact with a player, platform, or either
    screen edge.
-   **Items:** `Bomb`, `Wand`, `Robe`, `Machine Gun`, `Pistol`.
    Suggested roles: Bomb = arcing explosive projectile with trail and
    radial damage; Wand = quick magical bolt; Robe = temporary defensive
    shield/damage reduction; Machine Gun = rapid, low-damage shots;
    Pistol = slower, stronger shots. Keep item-specific behavior behind
    a common item/weapon interface.
-   **VFX:** bomb has a persistent, visually rich particle/spark trail;
    detonation emits a layered explosion using `pygame.draw.polygon`
    (irregular shards/spikes), rings, sparks, and particles. Add impact
    flashes and screen shake. Effects must be time-based and cleaned up
    when expired; use deterministic lightweight procedural drawing
    rather than requiring extra image assets.
-   **Controls (defaults; keep centralized/configurable):** Left player:
    `A/D` move, `W` jump, `S` or `F` use/attack. Right player: arrow
    keys move, `UP` jump, `DOWN` or `RSHIFT` use/attack. `ESC` returns
    to menu. Prevent key-repeat from causing repeated jump events;
    support holding attack for automatic weapons.
-   **Assets:** expected examples include
    `assets/animations/player/idle/1.png` and sibling animation folders.
    Asset loading should support animation directories with numbered
    frames, cache loaded images, scale to the intended sprite size, and
    fall back to a drawn stickman if a folder/file is absent.
-   **Rules:** health starts at `100` per player; health is clamped to
    `[0, 100]`. At zero, freeze combat and show winner/restart/menu UI.
    Keep UI readable during shake (either draw HUD after applying world
    shake or render HUD on a separate unshaken layer).
-   **Shared conventions:** coordinates are world-space unless
    explicitly named screen-space. `dt` is seconds.
    Rectangles/collisions use `pygame.Rect` where practical. Game
    objects must not call `pygame.display.flip()` or own the main loop.
    The main loop processes events once, updates once, renders once.
    Avoid circular imports; use the interfaces below. Use type hints and
    concise docstrings.

## `src/game` API contract

This is the planned API surface. Implementations may add private
helpers, but must not rename/remove public names or change signatures
without team agreement.

### `src/game/__init__.py`

Package marker; re-export nothing initially.

### `src/game/settings.py`

Shared constants and configuration. - Constants: `SCREEN_WIDTH: int`,
`SCREEN_HEIGHT: int`, `FPS: int`, `TITLE: str`, `GROUND_Y: int`,
`PLAYER_MAX_HEALTH: int`, `ITEM_SPAWN_INTERVAL: float`,
`INTRO_FOCUS_SECONDS: float`, `ASSET_DIR: pathlib.Path`. - `Controls`
--- `__init__(self, left: dict[str, int], right: dict[str, int])`;
fields `left`, `right`. - `GameConfig` --- `__init__(self)`, fields for
screen size, FPS, gravity, movement speeds, jump strength, player
health, spawn interval, and intro durations. Defaults are defined here,
not duplicated in modules.

### `src/game/assets.py`

Asset lookup, caching, and animation loading. - `AssetManager` ---
`__init__(self, asset_dir: pathlib.Path)`. -
`image(self, relative_path: str, size: tuple[int, int] | None = None) -> pygame.Surface` -
`frames(self, relative_dir: str, size: tuple[int, int] | None = None) -> list[pygame.Surface]` -
`sound(self, relative_path: str) -> pygame.mixer.Sound | None` -
`clear(self) -> None` - Missing assets return a safe placeholder/empty
frame list; callers must not crash.

### `src/game/player.py`

Player physics, movement, animation, health, and inventory. - `Player`
---
`__init__(self, player_id: int, spawn: tuple[float, float], controls: dict[str, int], assets: AssetManager, config: GameConfig)`. -
`handle_event(self, event: pygame.event.Event) -> None` -
`handle_input(self, keys: pygame.key.ScancodeWrapper, dt: float) -> None` -
`update(self, dt: float, platforms: list[pygame.Rect], world_bounds: pygame.Rect) -> None` -
`draw(self, surface: pygame.Surface, camera: "Camera") -> None` -
`take_damage(self, amount: float, knockback: tuple[float, float] = (0, 0)) -> None` -
`heal(self, amount: float) -> None` -
`equip(self, item: "Item | None") -> None` -
`attack(self, projectiles: list["Projectile"], effects: "EffectManager") -> None` -
`alive(self) -> bool` - `bounds(self) -> pygame.Rect` -
`center(self) -> tuple[float, float]` - `facing: int` (`-1` left, `1`
right); `health`, `velocity`, `held_item`, `on_ground`, `player_id` are
public state. - Player owns movement/animation state, not global
collision resolution, spawning, camera, or the game loop. Wall-jump is
triggered when airborne and touching a vertical platform wall; reset
jump availability on landing.

### `src/game/platforms.py`

Arena geometry and platform drawing/collision surfaces. - `Platform` ---
`__init__(self, rect: pygame.Rect, style: str = "stone")`; fields
`rect`, `style`. -
`Platform.draw(self, surface: pygame.Surface, camera: "Camera") -> None` -
`create_arena(self) -> list[Platform]` -
`platform_rects(self, platforms: list[Platform]) -> list[pygame.Rect]` -
Platforms are static; collision/physics is handled by `Player`.

### `src/game/items.py`

Collectible items and their held/used behavior. - `ItemType` enum:
`BOMB`, `WAND`, `ROBE`, `MACHINE_GUN`, `PISTOL`. - `Item` ---
`__init__(self, item_type: ItemType, position: tuple[float, float])`;
fields `item_type`, `position`, `velocity`, `bounds`, `active`. -
`Item.update(self, dt: float, platforms: list[pygame.Rect], world_bounds: pygame.Rect) -> None` -
`Item.draw(self, surface: pygame.Surface, camera: "Camera") -> None` -
`Item.collect(self, player: Player) -> None` -
`Item.use(self, player: Player, projectiles: list[Projectile], effects: EffectManager) -> None` -
`ItemSpawner` --- `__init__(self, config: GameConfig)`. -
`ItemSpawner.update(self, dt: float, world_bounds: pygame.Rect) -> list[Item]`
(returns newly spawned items). -
`ItemSpawner.draw(self, surface: pygame.Surface, camera: "Camera") -> None` -
Spawn positions/types are randomized but bounded; cap simultaneous
pickups to avoid clutter.

### `src/game/projectiles.py`

Projectiles, weapon shots, collision, bomb trails, explosions. -
`Projectile` ---
`__init__(self, owner_id: int, position: tuple[float, float], velocity: tuple[float, float], damage: float, kind: str, radius: int = 6)`. -
`update(self, dt: float, platforms: list[pygame.Rect], world_bounds: pygame.Rect, players: list[Player], effects: EffectManager) -> None` -
`draw(self, surface: pygame.Surface, camera: "Camera") -> None` -
`detonate(self, position: tuple[float, float], effects: EffectManager, players: list[Player]) -> None` -
`expired(self) -> bool` - `ProjectileManager` --- `__init__(self)`. -
`spawn(self, projectile: Projectile) -> None` -
`update(self, dt: float, platforms: list[pygame.Rect], world_bounds: pygame.Rect, players: list[Player], effects: EffectManager) -> None` -
`draw(self, surface: pygame.Surface, camera: "Camera") -> None` -
`remove_expired(self) -> None` - Bomb trail particles are emitted during
updates. On impact with a player, platform, or screen edge, detonate
once, damage nearby non-owner players, emit polygon shards/rings/sparks,
and request camera shake. Non-bomb projectiles expire on collision or
world exit.

### `src/game/effects.py`

Reusable particles, flashes, explosions, and screen shake requests. -
`Particle` ---
`__init__(self, position: tuple[float, float], velocity: tuple[float, float], lifetime: float, color: tuple[int, int, int], radius: float, kind: str = "circle")`. -
`update(self, dt: float) -> None` -
`draw(self, surface: pygame.Surface, camera: "Camera") -> None` -
`EffectManager` --- `__init__(self)`. -
`burst(self, position: tuple[float, float], count: int, palette: list[tuple[int, int, int]], strength: float = 1.0) -> None` -
`explosion(self, position: tuple[float, float], radius: float, palette: list[tuple[int, int, int]]) -> None` -
`request_shake(self, intensity: float, duration: float) -> None` -
`update(self, dt: float) -> None` -
`draw(self, surface: pygame.Surface, camera: "Camera") -> None` -
`shake_offset(self) -> tuple[int, int]` - `clear(self) -> None` - Use
polygons for jagged explosion silhouettes and fragments; clamp shake and
decay it smoothly.

### `src/game/camera.py`

World-to-screen transform and cinematic intro pan. - `Camera` ---
`__init__(self, screen_size: tuple[int, int], world_bounds: pygame.Rect)`. -
`focus(self, target: tuple[float, float], duration: float = 0.8) -> None` -
`start_intro(self, left_target: tuple[float, float], right_target: tuple[float, float]) -> None` -
`update(self, dt: float) -> None` -
`apply(self, position: tuple[float, float]) -> tuple[int, int]` -
`apply_rect(self, rect: pygame.Rect) -> pygame.Rect` -
`world_rect(self) -> pygame.Rect` - `intro_finished(self) -> bool` -
Intro is a non-blocking state sequence: left focus, pause, right focus,
pause, then arena-wide view. Clamp camera to world bounds and
interpolate smoothly.

### `src/game/ui.py`

Menu, HUD, and end-of-round UI. - `UI` ---
`__init__(self, config: GameConfig)`. -
`handle_event(self, event: pygame.event.Event) -> str | None` (returns
`"start"`, `"restart"`, `"menu"`, or `None`). -
`draw_menu(self, surface: pygame.Surface, dt: float) -> None` -
`draw_hud(self, surface: pygame.Surface, left: Player, right: Player) -> None` -
`draw_result(self, surface: pygame.Surface, winner: Player) -> None` -
`draw_button(self, surface: pygame.Surface, rect: pygame.Rect, text: str, hovered: bool = False) -> None` -
UI is screen-space and remains stable during world camera shake. Menu
should feel magical (animated stars/particles, layered colors, glow-like
button treatment) using procedural drawing if art is unavailable.

### `src/game/world.py`

Owns the play-state composition and update/render order. - `World` ---
`__init__(self, config: GameConfig, assets: AssetManager)`. -
`reset(self) -> None` -
`handle_event(self, event: pygame.event.Event) -> None` -
`update(self, dt: float) -> None` -
`draw(self, surface: pygame.Surface) -> None` -
`finished(self) -> bool` - `winner(self) -> Player | None` - `World`
creates players, platforms, spawner, camera, projectile manager, and
effects; coordinates pickup collection and projectile hits. It does not
own the application event loop.

### `src/game/game.py`

Top-level game state machine and application loop. - `Game` ---
`__init__(self)`. - `run(self) -> None` -
`handle_event(self, event: pygame.event.Event) -> None` -
`update(self, dt: float) -> None` - `draw(self) -> None` -
`change_state(self, state: str) -> None` - `quit(self) -> None` -
States: `"menu"`, `"intro"`, `"playing"`, `"game_over"`, `"quit"`.
Initialize pygame/display/font; cap frame rate; compute `dt`; process
events; update; draw; flip display. Start enters intro, intro completion
enters playing, zero health enters game over, restart resets world.

### `src/main.py`

-   `main() -> None`: instantiate `Game`, call `run()`.
-   Guard execution with `if __name__ == "__main__": main()`.

## Integration rules

1.  Public signatures above are the shared contract. If a method needs
    extra information, agree first; do not silently change its
    signature.
2.  Prefer passing dependencies explicitly (`config`, `assets`,
    `effects`, players/platforms) over importing the `Game` singleton.
3.  Use `pygame.Vector2` internally for velocity if useful, but keep the
    declared public tuple interfaces.
4.  Collision order: update players/platform collisions → update pickups
    and collect → update projectiles and apply damage → update
    effects/camera → check winner.
5.  Rendering order: background → platforms → pickups → projectiles →
    players → world effects → screen-space HUD/UI. Apply camera
    transform and shake to world objects only.
6.  `Player.attack()` delegates to the currently held item's `use()`
    behavior. Robe is a defensive item and applies a timed status rather
    than creating a projectile.
7.  Keep each file self-contained within its API boundary. Import types
    with `TYPE_CHECKING` where necessary to avoid circular imports.
