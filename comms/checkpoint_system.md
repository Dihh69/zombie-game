# Checkpoint System & Shop Menu

**Author / Machine:** Dihh69  
**Feature:** Checkpoint Progression & Ability Upgrade Shop  
**Status:** Implemented & Tested  

---

## 1. Overview
As specified in `AGENTS.md` and user requirements:
- A checkpoint is triggered after every **5 waves** (with 3 zombies per wave).
- After **3 checkpoints**, the game prepares for the final boss fight (`is_boss_ready = True`).
- **Every checkpoint:**
  1. The player's timer is **fully replenished** back to `max_timer` (60.0 units).
  2. The interactive **Shop Menu** opens.
  3. The player chooses one of two upgrades:
     - **Increase Attack Speed**: +25% attack speed (reduces attack & weapon cooldowns).
     - **Increase Attack Damage**: +30% attack damage (boosts damage dealt by attacks & projectiles).
  4. The shop closes and the game seamlessly resumes.

---

## 2. Controls & Interaction in Shop
The shop can be navigated using either keyboard or mouse:
- **Direct Hotkeys:** Press `[1]` to select Attack Speed, or `[2]` to select Attack Damage.
- **Arrow Keys:** Press `Left` / `A` or `Right` / `D` to highlight a card, then press `[ENTER]` or `[SPACE]` to confirm.
- **Mouse:** Hovering over either card highlights it; left-clicking the card or its button confirms the upgrade.
- **Debug Key:** During gameplay, pressing `[C]` immediately triggers a checkpoint and opens the shop for testing.

---

## 3. Public API for Teammates

### `Player` (`src/game/player.py`)
Other modules (e.g. Wave System, Zombie AI, Timer Arc UI) can directly use the following attributes and methods on `Player`:
- `player.timer: float` - Current remaining time units.
- `player.max_timer: float` - Maximum time capacity (default: 60.0).
- `player.replenish_timer() -> None` - Resets `player.timer = player.max_timer`.
- `player.add_time(amount: float) -> None` - Adds or deducts time units clamped between 0 and `max_timer`.
  - Hit zombie: `player.add_time(1.0)`
  - Miss attack: `player.add_time(-1.0)`
  - Hit by zombie: `player.add_time(-5.0)`
  - Kill zombie: `player.add_time(3.0)`
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

### `Game` (`src/game/game.py`)
- State `"checkpoint_shop"` is handled by the state machine to pause normal updates and render the shop overlay on top of the arena.

---

## 4. Modified & Added Files
- `src/game/checkpoint.py` (New): `UpgradeType`, `ShopMenu`, and `CheckpointManager`.
- `src/game/player.py`: Added timer methods, attack speed/damage multipliers, and unarmed cooldown scaling.
- `src/game/items.py`: Weapons scale projectile damage and fire rate cooldown with player multipliers.
- `src/game/world.py`: Instantiates and resets `CheckpointManager`.
- `src/game/game.py`: Added `"checkpoint_shop"` state, event handling, update, and drawing.
