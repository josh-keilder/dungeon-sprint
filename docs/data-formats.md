# Data formats

**`lights`** (`floor_data["lights"]`, kept as `floor.lights`): a list of `(name, position)` pairs, one per animated light tile. `name` is the animation name (`"torch"`, `"side_torch"`, `"candlestick_1"`, `"candlestick_2"`), which is also the key into `LIGHT_TYPES`; `position` is the flame's position in world pixels (`flame_position`: the tile's center plus the type's offset, mirrored for right-wall side torches). Floor 1 has 21: 11 torches, 6 side torches and 4 candlesticks.

**`light_blockers`** (`floor.light_blockers`): `((columns, rows), bytes)`, one byte per map tile, row by row (`row × columns + column`), 1 where light can't pass (a wall or closed door), else 0. Floor 1: 72×51 tiles, 2574 blockers (2570 walls and 4 door tiles).

**`PLAYER_DATA`** (`game/data/player_data.py`), read once by `Player.__init__` the way `ENEMY_TYPES` is read by `Enemy`; the keys that mean the same thing have the same names in both. Besides `base_stats` (below) it holds `invulnerability_duration` (1.0 s of i-frames after a hit), `blink_interval` (0.1 s per blink on and off while invulnerable), `knockback_speed` (160 px/s away from the enemy that hit), `knockback_decay_rate` (16; the slide is about speed ÷ decay = 10 px), `inventory_slot_count` (20) and `equipment_slot_names` (`head`, `chest`, `boots`, `ability`, in the order the inventory screen draws them). `Player` copies `base_stats` with `dict(...)`, so nothing a player does can change the shared data.

**Player `base_stats`** (`PLAYER_DATA["base_stats"]`). These are the values before equipment:

| Stat | Value | Used for |
| --- | --- | --- |
| `defense` | 0 | Not used yet |
| `max_speed` | 70 | Target speed in `steer` (pixels/second) |
| `health` | 25 | Max health (kept low for now while values are being worked out) |
| `roll_speed` | 200 | Extra speed during a roll |
| `acceleration_rate` | 20 | How fast the player reaches `max_speed` while holding a direction (95 % in about 0.15 s) |
| `deceleration_rate` | 60 | How fast the player stops with no input (to a full stop in about 0.07 s) |
| `grip` | 50 | How fast sideways and reversing velocity is removed (sideways drift gone in about 0.09 s) |

Roll timing is in `game/rules/roll.py`: `ROLL_DURATION` 0.4 s, `ROLL_COOLDOWN` 1.0 s (the cooldown starts when the roll starts), and `ROLL_EASE_OUT_START` 0.7 (the push starts fading after 70 % of the roll).

**`roll` dict** (player): `{"direction", "active_timer", "cooldown_timer"}`. `direction` is the move direction copied when the roll started. `active_timer` holds the seconds left in the current roll, and `cooldown_timer` the seconds before the next roll can start. Both are timers from `new_timer()`. There is no separate "active" flag: `is_rolling(roll)` is true while `active_timer` is running, and all code asks it that way.

**Timers** (`engine/core/timer.py`). Every countdown in the game is a `{"time_left": seconds, "duration": seconds}` dict made with `new_timer()`, including the enemies' flee and return countdowns. `start_timer(timer, duration)` sets both, so the timer remembers how long it was started for and `fraction_left(timer)` and `time_elapsed(timer)` need nothing else, `advance_timer(timer, dt)` subtracts `dt` each frame, and `is_running(timer)` is true while it is `> 0`. `time_left(timer)` returns the seconds left, never below 0, for code that needs the number itself, such as the roll ease-out and the player's blink. The value keeps counting below 0, which is harmless because every check goes through `is_running` or `time_left`. Only `timer.py` reads the `"time_left"` key directly, so the key could change again without touching anything else (it was renamed from `"timer"`, since a timer with a "timer" key read oddly and `time_left()` already returns it). The roll's `active_timer` and `cooldown_timer` are timers too. The one exception is animation, which is a different kind of timer that counts *up* to advance frames.

**`invulnerability` dict** (player and enemies): a timer holding the seconds of invulnerability left. The player's window is its `invulnerability_duration` (1.0 s, `PLAYER_DATA`), and each enemy's is its own `invulnerability_duration` from `ENEMY_TYPES`. The player's `blink_interval` is 0.1 s, and `ROLL_DAMAGE_PER_SPEED` is 0.15 (`game/rules/combat.py`), so an enemy with 100 health dies after about 3 rolls.

**`heal_cooldown` dict** (player): a timer holding the seconds left before another potion can be used. `use_small_health_potion` refuses while `is_running(heal_cooldown)`. `HEAL_COOLDOWN` is 3.0 s (`game/rules/consumables.py`). The cooldown only starts when a potion is actually used, so a refused Q press (full health or no potion) doesn't start it.

**Equipment bonuses.** `compute_stats` copies `base_stats` and adds each equipped item's `bonuses` to stats with the same name. Bonus names that aren't in `base_stats` are ignored. Speed boots give `{"max_speed": 10, "acceleration_rate": 7, "defense": 3, "health": 10}`.

**`ENEMY_TYPES`** (`game/data/enemy_type_data.py`). The key must match the map spawn name after `Enemy_`:

```python
"Skull": {
    "max_health": 100,
    "attack_damage": 5,        # damage dealt to the player on contact
    "behavior": "fly",         # "fly" or "wander_chase"
    "speed": 50,
    "texture_data": skull_texture_data,
    "start_animation": "skull_idle",
    "knockback_multiplier": 1.2,   # how easily it is shoved by a roll hit
    "knockback_decay_rate": 10,    # how fast the shove fades (higher is shorter)
    "blink_interval": 0.1,         # seconds per blink on/off after a hit
    "invulnerability_duration": 1.0,  # seconds of i-frames after a hit
    "loot_table": SKULL_LOOT,     # what it can drop when it dies
    "body": (0, 0, 16, 16),        # x, y, width, height of the body inside the frame
    "touch_damage": True,          # hurts the player on contact
    "animation_prefix": None,      # one animation, no states
    "attack": None,                # no swing
    "hit_particles": SKULL_SPARKS, # burst along the knockback when a roll hits it
    "stagger_duration": 0.0,       # its knockback is long enough on its own
},
"Skeleton": {
    "max_health": 100,
    "attack_damage": 6,            # damage of one landed swing
    "behavior": "wander_chase",
    "speed": 40,
    "texture_data": skeleton_texture_data,
    "start_animation": "skeleton_idle_right",
    "knockback_multiplier": 0.7,
    "knockback_decay_rate": 16,
    "blink_interval": None,        # no blink: it plays its hurt animation instead
    "invulnerability_duration": 1.0,
    "loot_table": SKELETON_LOOT,
    "body": (8, 13, 14, 16),       # the body inside its 32x32 frame
    "touch_damage": False,         # only its swing hurts
    "animation_prefix": "skeleton",  # animations named skeleton_<action>_<facing>
    "attack": {
        "range": 20,               # px: starts a swing when the player is this close
        "frame_rate": 10,          # attack frames per second: frames 0-5 wind up in 0.6 s
        "strike_frames": (6, 7),   # the frames that hurt: where the slash is drawn
        "reach": 18,               # px the strike hitbox extends in front of the body
        "cooldown": 1.0,           # s after a swing before the next one
        "line_up_gap": 16,         # px beside the player it walks to before swinging
        "level_tolerance": 6,      # px of height difference it still swings at
    },
    "hit_particles": BONE_CHIPS,
    "stagger_duration": 0.75,      # s without walking or swinging after a hit
},
```

- **`attack_damage`** means what hurts: the touch for a `touch_damage` type, one landed swing for a type with an `attack`.
- **`body`** is the box that moves, collides, gets separated and blocks the player, given inside the art frame, so art can be bigger than the body (the Skeleton's 32×32 frame has a lot of empty space around a 14×16 body).
- **`animation_prefix`** turns on animation states: the texture data must then have `<prefix>_idle_right`, `_move_right`, `_hurt_right` and `_death_right` (and `_attack_right` for a type with an `attack`). `None` keeps the single `start_animation`.
- **`blink_interval`** `None` turns the hit blink off, for types whose hurt animation already shows the hit.
- **`attack`** `None` means no swing; a dict turns on the telegraphed swing ([One frame](frame.md), step 4). Its swing only reaches sideways, so the enemy walks to a spot `line_up_gap` beside the player and only swings when the player is within `level_tolerance` of its height.
- **`hit_particles`** is a particle preset (below) burst when a roll hits it.
- **`stagger_duration`** is how long it stands still after a roll hit, at least as long as its knockback lasts. 0 means only the knockback.

**Particle presets** (`game/data/particle_presets.py`), handed to the engine's `emit_burst`. Ranges are `(lowest, highest)`, picked at random per particle:

```python
CRATE_DEBRIS = {
    "count": 8,                    # particles per burst
    "colors": (PALETTE_LEATHER, PALETTE_TORCH, PALETTE_CLAY),   # one picked per particle
    "speed": (40, 100),            # px per second
    "lifetime": (0.25, 0.45),      # seconds
    "size": (2, 3),                # px, square
    "drag": 6,                     # how fast they slow down; higher stops sooner
    "spread": 360,                 # degrees around the direction; 360 = all around
}
```

`BONE_CHIPS` (6 bone-colored chips, spread 120°) and `SKULL_SPARKS` (7 icy sparks, spread 140°) are sprayed along a roll hit's knockback, so the burst flies away from the player.

Every key is required. `Enemy.__init__` reads them with `type_data["..."]`, so a missing key raises `KeyError` naming it when the floor loads, instead of silently using a default.

`knockback_multiplier` scales the player's hit strength: 1.0 is normal, above 1 is light (pushed further), below 1 is heavy, and 0 can't be moved at all. The Skull is 1.2 and the Skeleton 0.7, so the same roll slides a Skull about 38 px and a Skeleton about 14 px.

**Blink** (`engine/graphics/blink.py`). `is_blink_hidden(invulnerability, blink_interval)` is the shared rule: while the timer is running, `int(time_left / blink_interval)` counts up once per interval, and every odd count is hidden. The rule is shared, but each entity owns its interval: the player's `blink_interval` (`PLAYER_DATA`) and each enemy's (`ENEMY_TYPES`).

```
blink_phase = int(time_left(invulnerability) ÷ blink_interval)    (counts up once per interval)
hidden      = timer is running  and  blink_phase is odd
```

**Texture data** (`*_texture_data.py`). One entry per animation:

```python
"player_walk_right": {
    "size": (64, 64),          # width and height of one frame
    "position": (0, 0),        # only the second number is used: the row on the sheet
    "frames": 6,               # how many frames, read left to right
    "file_path": "Assets/Player/Walk/Proto_Walk_Right.png",
},
```

`load_animations(texture_data, crop_size=None)` returns `{animation_name: [frames]}`:
- It slices each sheet into frames (`slice_frames`).
- If `crop_size` is given, it crops each frame from the center (`crop_center`).
- For every `*_right` animation it adds a mirrored `*_left` (`add_flipped_left`), unless a `*_left` already exists.

Results are cached by the set of animation names plus `crop_size`. Two texture dicts with identical names would share one cache entry, so give each animation a unique name. Images are cached by path in `load_image`.

**Health dict** (`engine/gameplay/health.py`). `{"current": hp, "maximum": hp}`, made with `new_health(maximum)`, which starts full. `take_damage` and `heal` keep `current` between 0 and `maximum`; `set_max_health(health, new_max)` changes `maximum` and clamps `current` (used when gear changes the player's health stat). An enemy's health comes from its type's `"max_health"` stat in `ENEMY_TYPES`: that key names the stat, while the dict itself uses `"current"` and `"maximum"`.

**Animation dict** (`engine/graphics/animation.py`). `{"frames", "current", "index", "timer", "speed"}`. `speed` is frames per second: 10 by default, and 4 for item animations. `set_animation` only restarts when the name actually changes and exists.

**Item database** (`item_database.py`). Keys are item ids, values are `Item` or `EquipmentItem` templates. Templates are never put in an inventory directly. Code always works with `clone()`s.

**`CHEST_LOOT`** (`loot_table_data.py`). Each entry is rolled independently, so one chest can drop several things:

```python
{"item_id": "small_health_potion", "chance": 0.5, "min_quantity": 1, "max_quantity": 3}
{"item_id": "speed_boots", "chance": 0.08, "min_quantity": 1, "max_quantity": 1}
```

Keys are not chest loot: they're placed on the map (the `Items` layer), so every floor is guaranteed to have the keys its doors need, and routes don't depend on luck. Chests are for random extras: potions and gear.

**Crate loot.** `CRATE_LOOT` is a 15% chance of 1 to 2 small health potions per broken crate: crates are quick and plentiful, so each one is a small gamble, rolled at the moment of the hit.

**Enemy loot.** Each enemy type has its own table, the same shape as `CHEST_LOOT`, kept in `loot_table_data.py` and attached to the type as `ENEMY_TYPES[...]["loot_table"]`:

```python
SKULL_LOOT    = [{"item_id": "small_health_potion", "chance": 0.25, "min_quantity": 1, "max_quantity": 1}]
SKELETON_LOOT = [{"item_id": "small_health_potion", "chance": 0.35, "min_quantity": 1, "max_quantity": 1}]
```

Enemies drop single potions, smaller than a chest's 1 to 3, so chests stay the bigger prize and are worth a detour. A chest and an enemy go through the same pipeline; only the event and the table differ:

```
chest opened ──▶ roll_loot(CHEST_LOOT)        ──▶ floor.spawn_loot(drops, chest center)
enemy dies   ──▶ roll_loot(enemy.loot_table)  ──▶ floor.spawn_loot(drops, enemy center)
```

The table belongs to the enemy type, so a tougher enemy can be worth more, and because it's data, a difficulty mode can later scale every table (more potions on Easy) without touching code. With Level One's 2 Skulls and 2 Skeletons:

```
average potions per kill:  Skull 0.25, Skeleton 0.35
per full clear:            2 × 0.25 + 2 × 0.35 = 1.2 potions on average
chance of no drop at all:  0.75² × 0.65² ≈ 0.24   (about 1 clear in 4)
```

`chance` is 0.0 to 1.0, and the quantity is a random whole number between min and max inclusive.

**Settings file.** `settings.json` in the project root. It is ignored by git, so each machine has its own. It is created when you leave the options menu.

```json
{"fps_enabled": false, "full_screen_enabled": false, "music_volume": 0.5, "sfx_volume": 0.5}
```

Missing keys fall back to the game's `DEFAULT_SETTINGS` (`game/data/constants.py`), and saved keys the defaults don't have are dropped. A corrupted file prints a warning and uses the defaults.

**Sounds.** Every file ending in one of `AUDIO_EXTENSIONS` (`.wav`, `.ogg`) in `SFX_FOLDER` (`Assets/Sounds`) and `MUSIC_FOLDER` (`Assets/Music`) is loaded and named by its filename without the extension. Sound files are named in lowercase snake_case, so their keys are too. Names currently used: `button_hover`, `button_click`, `pause`, `heal`, `death` and `roll_hit` (SFX), and `menu_music`, `level_music` and `game_over` (music). Each state picks its own track in `enter()` ([Architecture](architecture.md)). A missing name prints a message instead of crashing.

**The maps** (`Assets/Maps/*.tmx`, 16x16 tiles; the floors are written by the ASCII converter, and Tiled can open them). The loader looks for these names:

| Layer | Type | What the loader does |
| --- | --- | --- |
| `Floor` | Tile layer | Drawn once into `map_surface` |
| `Walls` | Tile layer | Drawn once into `map_surface`, on top of the floor, and one `WallTile` per tile. The walls next to open space block movement (`edge_walls`); every wall blocks light. |
| `Wall_Decor`, `Floor_Decor` | Tile layers | `DecorTile`s, drawn but not solid; light tiles (91, 92, 94, 96) become `AnimatedDecor` and lights |
| `Door_Tiles` | Tile layer | One `Door` per tile. These block movement until unlocked. |
| `Chests` | Object layer | One `Chest` per object named `chest` (any capitalization) |
| `Crates` | Object layer | One `Crate` per object |
| `Items` | Object layer | Placed items: each object is named by its item id (`silver_key`, `gold_key`) and spawned as a `GroundItem` at its center |
| `Doors` | Object layer | One `door` object per door group, with `door_id` and `key` properties; every door tile inside its rect gets both |
| `Entity_Spawns` | Object layer | `Player` is the player spawn. `Enemy_<Type>` objects (e.g. `Enemy_Skull`) are enemy spawns. A rectangle object named `Exit` is the floor's exit. A map without one can't be finished, but doesn't crash. |

Door tiles that share a `door_id` (e.g. `door_1`) unlock together as one door. The exit is drawn by the ladder tile on `Floor_Decor`.
