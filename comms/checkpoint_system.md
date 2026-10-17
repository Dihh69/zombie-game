# Checkpoint System & Pure Melee Combat

**Author / Machine:** Dihh69  
**Feature:** Single-Player Checkpoint Progression, Upgrade Shop, Pure Melee Combat & Arc Timer  
**Status:** Implemented & Tested  

---

## 1. Overview
As specified in `AGENTS.md` and user requirements:
- The game is **Single Player**: only one hero is spawned in the arena, with camera focus and single-player HUD.
- A checkpoint is triggered after every **5 waves** (with 3 zombies per wave).
- After **3 checkpoints**, the game prepares for the final boss fight (`is_boss_ready = True`).
- **Every checkpoint:**
  1. The player's timer is **fully replenished** back to `max_timer` (60.0 units).
  2. The interactive **Shop Menu** opens.
  3. The player chooses one of two upgrades:
     - **Increase Attack Speed**: +25% melee attack speed (reduces melee swing cooldown).
     - **Increase Attack Damage**: +30% melee attack damage (boosts damage dealt by melee strikes).
  4. The shop closes and the game seamlessly resumes.

---

## 2. Timer System & Visual Arc
- **Timer Decay**: In `playing` state, `player.timer` steadily counts down by `dt` every second.
- **Defeat on Timeout**: If `player.timer <= 0.0`, the hero turns into a zombie and the game ends.
- **Arc over the Player (`AGENTS.md`)**:
  - A semicircular gauge arc is rendered directly above the player's head.
  - The arc starts from the right (100% human, yellow) and recedes down to the left (0% zombie, green).
  - The stickman player's body and head dynamically interpolate colors from **Yellow (Human)** to **Green (Zombie)** as time elapses.
- **Time Bonuses / Penalties (`AGENTS.md`)**:
  - Attack & Hit: `+1` unit of time (`player.add_time(1.0)`).
  - Attack & Miss: `-1` unit of time (`player.add_time(-1.0)`).
  - Kill Zombie: `+3` units of time (`player.add_time(3.0)`).
  - Hit by Zombie: `-5` units of time (`player.add_time(-5.0)`).

---

## 3. Pure Melee Combat System (Weapons Removed)
The weapon system from the base game (sky item drops, guns, bombs, wands, robes, and projectiles) has been **completely removed**:
- The game is now **purely melee**.
- Every attack creates a **box attack radius** (`pygame.Rect`) extending forward in the direction the player is facing:
  - Reach: 64 px
  - Height: 58 px
  - Function: `player.get_melee_attack_box() -> pygame.Rect`
- Visuals: Procedural melee fist thrust and dynamic crescent slash arc rendered within the attack box in the facing direction.

---

## 4. On-Screen Test Button & Shortcuts
- An interactive **`[ ⚡ SKIP TO CHECKPOINT ]`** test button is rendered at the top-right of the HUD.
- Clicking the button with the mouse immediately triggers a checkpoint, fully replenishes the timer, and opens the upgrade shop.
- Hotkeys **`[C]`** or **`[T]`** during gameplay also instantly trigger the checkpoint.

---

## 5. Public API for Teammates

### `Player` (`src/game/player.py`)
- `player.timer: float` - Current remaining time units (decays over time).
- `player.max_timer: float` - Maximum time capacity (default: 60.0).
- `player.replenish_timer() -> None` - Resets `player.timer = player.max_timer`.
- `player.add_time(amount: float) -> None` - Adds or deducts time units clamped between 0 and `max_timer`.
- `player.get_melee_attack_box() -> pygame.Rect` - Returns the melee attack box in the direction the player is facing.
- `player.attack(targets=None, effects=None) -> pygame.Rect | None` - Executes a melee strike, applies damage/knockback and time gain/loss if targets are provided, and returns the attack box.
- `player.attack_speed_multiplier: float` - Cooldown reduction factor (starts at 1.0, increases by +0.25 per upgrade).
- `player.attack_damage_multiplier: float` - Damage multiplier (starts at 1.0, increases by +0.30 per upgrade).
- `player.upgrade_attack_speed(boost: float = 0.25) -> None`
- `player.upgrade_attack_damage(boost: float = 0.30) -> None`

### `CheckpointManager` (`src/game/checkpoint.py`)
Accessible via `world.checkpoint_manager`:
- `checkpoint_manager.complete_wave(player: Player) -> bool`
  Call this when a wave is cleared. Automatically triggers a checkpoint every 5 waves.
- `checkpoint_manager.trigger_checkpoint(player: Player) -> None`
  Manually opens a checkpoint, replenishes timer, and shows shop.
- `checkpoint_manager.is_shop_open: bool`
  `True` while the shop modal is active.
- `checkpoint_manager.is_boss_ready: bool`
  Becomes `True` once 3 checkpoints have been completed.
- `checkpoint_manager.checkpoints_reached: int`
  Number of checkpoints reached so far (0 to 3).
- `checkpoint_manager.current_wave: int`
  Current wave number.

---

## 6. Modified & Added Files
- `src/game/checkpoint.py`: `UpgradeType`, `ShopMenu`, and `CheckpointManager`.
- `src/game/player.py`: Single hero attributes, timer decay, Arc gauge rendering, green/yellow transition, melee box attack radius.
- `src/game/world.py`: Single-player spawning, finished/winner conditions, melee combat routing.
- `src/game/ui.py`: Single-player HUD, on-screen `[ ⚡ SKIP TO CHECKPOINT ]` test button, timer & combat stats display.
- `src/game/camera.py`: Single-player cinematic intro zoom and tracking.
- `src/game/game.py`: Single-player loop, test button event handling, and checkpoint shop transitions.
