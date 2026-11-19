# One gameplay frame, step by step

This is `Run.update(dt)` followed by `Run.draw(screen)`. `update` reads as a list of steps, each a method of `Run` ([Game reference](game.md)): `handle_actions`, `update_world`, `update_interact_target`, `finish_floor`, `update_camera`.

First of all, `hit_feedback.update(dt)` advances the camera shake and the hurt vignette, on every frame, frozen ones included, so a vignette started by the killing hit still fades during the death freeze. Then come two early exits. While `death.is_active()`, it only calls `update_death(dt)` (step 6). Then, while `floor_transition.is_active()`, it only calls `update_transition(dt)` and returns. Both come before `read_input()` and `run_time += dt`, so input, ESC, the world and the run timer are all frozen; transition time doesn't count toward the run, since loading speed differs between computers.

**1. Read input.** `read_input()` returns a fresh intent dict and stores it on `player.intent`:

| Key | Field | Kind |
| --- | --- | --- |
| WASD | `move` | Held. A normalized `Vector2`, so diagonals aren't faster. |
| SPACE | `roll` | Pressed this frame |
| F | `interact` | Pressed this frame |
| Q | `heal` | Pressed this frame |
| E | `inventory` | Pressed this frame |
| ESC | `pause` | Pressed this frame |
| P | `debug` | Pressed this frame |
| Left mouse | `mouse_left_click` | Click position this frame, or `None` |

"Pressed this frame" uses pygame-ce's `get_just_pressed`, so holding a key triggers it only once.

**2. Run-wide actions** (`handle_actions`, with the pause check and the timer just before it).
- `pause`: switch to options, play `pause`, and stop this frame's update.
- Right after the pause check, `run_time += dt`. Its position is the whole pause logic: while paused, `Run.update` isn't called at all; while dying, `update_death` has already returned; and on the frame ESC is pressed, the pause check returns first. So the timer only counts frames of real play. Opening the inventory doesn't pause the game, so it doesn't pause the timer either.
- `debug`: toggle hitbox drawing.
- `interact`: run `interact.interact(player, floor)` (below).
- `inventory`: open the inventory. When closing, any held item goes back into the inventory first. If it doesn't fit, the inventory stays open.
- A mouse click while the inventory is open goes to `InventoryUI.handle_click`.

The game keeps running while the inventory is open. It is an overlay, not a pause, so managing items costs time and the world can still hurt you. `INVENTORY_PAUSES_GAME` (`False`, in `run.py`) makes this a one-word change: right after the inventory input (opening, closing and clicking), `Run.update` returns early when the inventory is open and the constant is `True`, which would stop the player, enemies, contacts and camera while the inventory stays usable. The check sits after `run_time += dt`, so the run timer would keep counting even while paused.

**3. Player update** (`Player.update`):
1. Sets `walking` and updates `facing` from the move direction. Facing doesn't change mid-roll. Vertical input wins over horizontal for facing.
2. Recomputes `stats` from `base_stats` plus equipment bonuses, every frame, so equipping takes effect immediately. If the health stat changed, `set_max_health` updates the maximum and clamps current health.
3. `roll` intent → `try_start_roll`. A roll needs a move direction, can't start during another roll (`is_rolling`), and can't start while `cooldown_timer` is running. Starting one starts both `active_timer` and `cooldown_timer`.
4. `heal` intent → `use_small_health_potion`. Heals `SMALL_HEALTH_POTION_VALUE` (10 of the 25 max), removes one potion and starts the heal cooldown, unless the cooldown is still running, health is already full or there is no potion. It returns whether a potion was used, and only then does the player play the `heal` sound. The sound is played here rather than in `game/rules/consumables.py` because it is feedback, not a rule.
5. `update_movement`: `steer` computes the new velocity from the move direction and the `max_speed`, `acceleration_rate`, `deceleration_rate` and `grip` stats, then `move_and_collide` moves the rect against the walls the run passed in, `floor.player_walls(player)`: the solid tiles, plus solid enemies while walking (step 5). Hitting a wall zeros velocity on that axis.
6. `update_roll`: while rolling, the player is also moved by `roll_speed` in the roll direction (on top of normal movement), scaled by `roll_speed_multiplier` so the push fades out at the end of the roll (see below), then `advance_roll` counts down `active_timer` and `cooldown_timer`.
   Then the player's `speed` is measured. At the very start of `update`, the player's center is copied into `start_pos`, before anything moves. After `update_movement` and `update_roll`, the distance from `start_pos` to the new center, divided by `dt`, gives the actual speed in pixels per second. Because it is measured rather than calculated, it includes walls: rolling into a wall gives a low speed.

   ```
   speed = distance moved this frame  ÷  dt
           └────── pixels ───────┘     └ seconds ┘   →  pixels per second
   ```

7. `advance_timer` counts down the invulnerability timer, then the heal cooldown.
8. Picks the animation `player_{idle|walk|roll}_{direction}` and advances it.
9. Copies `rect.topleft` into `pos`.

**How `steer` works.** `steer` is a kinematic controller, like Godot's: it doesn't push the player with forces, it moves the current velocity toward a *target velocity*, `direction * max_speed` (zero when there is no input). Each frame it closes a fraction of the gap between the two.

```
target velocity = direction × max_speed           (zero when there is no input)
new velocity    = velocity + (target velocity − velocity) × fraction
                             └────────── the gap ─────────┘
```

- **The fraction.** `approach_fraction(rate, dt)` returns `1 - exp(-rate * dt)`. Closing a fixed fraction of the gap per *frame* would feel snappier at higher frame rates, but this formula gives the same motion at any frame rate, because two frames of `dt` multiply out to exactly one frame of `2 * dt`. A higher `rate` is snappier. As a rule of thumb, the velocity is 95 % of the way to its target after about `3 / rate` seconds.

  ```
  fraction = 1 − e^(−rate × dt)              (approach_fraction)
  time to get 95 % of the way ≈ 3 ÷ rate seconds
  ```

- **Acceleration scales by itself.** Because a fraction of the *gap* is closed, the player gains a lot of speed when standing still (big gap) and very little near `max_speed` (small gap), easing in without overshooting. No speed cap is needed.
- **Grip.** With input, the velocity is split using the dot product: `along_speed = velocity.dot(direction)` is the speed in the input direction, `along_velocity` is that part as a vector, and `across_velocity` is everything left over (sideways motion from the previous heading). The along part approaches the target at `acceleration_rate`. The across part is removed at the `grip` rate, so turns don't drift. When `along_speed` is negative (the player is reversing), the along part uses `grip` too, so turning around is as snappy as turning sideways.

  ```
  along_speed     = velocity · direction        (dot product: speed in the input direction)
  along_velocity  = direction × along_speed
  across_velocity = velocity − along_velocity   (the sideways leftover)

  new along    = along_velocity  lerped toward target velocity
                 at acceleration_rate, or at grip when along_speed < 0 (reversing)
  new across   = across_velocity × (1 − approach_fraction(grip, dt))
  new velocity = new along + new across
  ```

  The split, with the input pointing up and the old velocity still heading right:

  ```
                direction (your input, length 1)
                ↑
                |   velocity
                |  ↗
    along part  | /
                |/____→ across part (sideways)
  ```

  The along part speeds up toward `max_speed`. The across part is the leftover from the previous heading, and grip removes it.
- **Stopping.** With no input, `steer` calls `decay_velocity(velocity, deceleration_rate, dt)`, which multiplies the velocity by `1 - approach_fraction(rate, dt)` and collapses it within a few frames. Below `STOP_SPEED` (1.0 px/s) it snaps to exactly 0, because closing a fraction of the gap never quite reaches zero. Enemy knockback fades with the same function. A velocity faded this way travels a total distance of about `speed / rate` before stopping, which is handy for tuning: 250 px/s at a rate of 12 slides about 21 px.

  ```
  new velocity = velocity × (1 − approach_fraction(rate, dt))      (decay_velocity)
                 then snapped to 0 below STOP_SPEED (1.0 px/s)

  total distance travelled ≈ starting speed ÷ rate
  ```

**How the roll eases out.** The roll push isn't constant. `roll_speed_multiplier(roll)` (`game/rules/roll.py`) scales it, holding at 1.0 for most of the roll and then fading to 0.0 just as the roll ends, so the player slides back into walking speed instead of dropping to it in one frame.

```
multiplier
1.0 ┤████████████████████▄
    │                     ▀▄
    │                       ▀▄
0.0 ┤                         ▀
    └──────────────────────────
    0 %      roll progress    100 %
                     ↑
           ROLL_EASE_OUT_START (0.7)
```

- **Progress.** `active_timer` counts down from `ROLL_DURATION` (0.4) to 0, so the fraction of the roll done is `1 - fraction_left(active_timer)`: 0.0 at the start, 1.0 at the end. `fraction_left` divides by the duration the timer was started with, and `time_left` inside it clamps at 0, because a timer that has counted below zero would otherwise give progress above 1.0 and a negative multiplier.

  ```
  progress = 1 − fraction_left(active_timer)                    (0.0 at the start → 1.0 at the end)
  ```

- **The fade.** Before `ROLL_EASE_OUT_START` the multiplier is 1.0. After it, it is `(1 - progress) / (1 - ROLL_EASE_OUT_START)`, a straight line from 1.0 at progress 0.7 to 0.0 at progress 1.0. With a 0.4 s roll, the fade covers the last 0.12 s.

  ```
  multiplier = 1.0                                          while progress < ROLL_EASE_OUT_START
             = (1 − progress) ÷ (1 − ROLL_EASE_OUT_START)    after it  (1.0 → 0.0)

  roll push  = roll direction × roll_speed × multiplier
  ```

- **Measured example.** Rolling from full walking speed, the player's `speed` sampled every 0.05 s is `270, 270, 270, 270, 270, 244, 160, 77`, then 70 on the first frame after the roll.

**How `move_and_collide` works.** It moves on X, pushes the rect out of the first wall it overlaps, then does the same on Y. Doing the axes separately lets you slide along walls. It returns `(hit_x, hit_y)`. `walls` is a list of plain rects, and each axis is one `rect.collidelist(walls)` call, which checks the whole list in C and returns the index of the first rect hit, or `-1`. `has_line_of_sight` and `separate_enemies` take the same rect list.

**Performance.** Profiling 600 frames of a run on floor 1 (frame cap off, a room with torches and enemies in view) showed the time wasn't in rendering but in wall collision: `move_and_collide` looped over every wall in Python, twice per call, about 10 calls a frame, against floor 1's 2570 walls, about 50,000 checks a frame. Three changes fixed it, each measured:

```
                                                  uncapped FPS   ms per frame
before                                                 142           7.05     (update alone 5.84)
collide only with edge_walls (614 of 2570)             353           2.83
+ walls as rects, checked with collidelist             782           1.28     (update 0.21)
+ walls drawn into map_surface once                    draw −0.25 ms (Floor.draw no longer visits 2570 walls)

now: 1.37 ms ≈ 730 FPS   update 0.19   state draw 0.48   present 0.68   flip 0.02
```

In game the counter sits around 200, not at the 240 cap: `clock.tick(240)` waits in whole milliseconds, so a 4.17 ms frame usually waits 5 ms. An empty loop with no work at all reaches only about 204 FPS with `tick(240)`. `clock.tick_busy_loop` would hit 240 exactly but keeps a CPU core busy waiting, which isn't worth it above any common monitor's refresh rate.

**Particles** (`engine/graphics/particles.py`, with the presets in `game/data/particle_presets.py`). A particle is a tiny short-lived square that flies out, slows down and shrinks away. It's pure data, a dict with `pos`, `velocity`, `color`, `size`, `drag`, `lifetime` and `age`, and the functions are the rules; the list of live particles belongs to the `Floor` (`floor.particles`, a fresh list for every floor).

```
something happens ──▶ emit_burst(particles, center, PRESET)    adds `count` particles
every frame       ──▶ update_particles(particles, dt)          move, slow down, age, drop the dead
draw              ──▶ draw_particles(surface, particles, camera) one small square each, shrinking with age
```

- **Presets are recipes**: `CRATE_DEBRIS` is `{"count": 8, "colors": (leather, torch, clay), "speed": (40, 100), "lifetime": (0.25, 0.45), "size": (2, 3), "drag": 6}`, the crate's own colors so the debris reads as the same wood. Ranges are `(lowest, highest)`, picked at random per particle with `random.uniform(*range)` (`*` unpacks the pair into two arguments). A new effect (hits, deaths, roll dust) is a new preset, with no new code.
- **`emit_burst`** gives each particle a random direction at a random speed: `pygame.Vector2(speed, 0).rotate(direction)` is a vector pointing right with length `speed`, turned by a random 0 to 360 degrees.
- **`update_particles`** moves each particle by `velocity × dt` and slows it with drag, then keeps only the live ones. `particles[:] = [...]` replaces the list's **contents**, not the list: the floor holds a reference to the same list object, so a plain `particles = [...]` inside the function would only rebind a local name, and dead particles would never leave the run's list.
- **`draw_particles`** draws each one with `surface.fill(color, rect)`, the fastest way to draw a solid square, and makes it **shrink** in whole-pixel steps instead of fading: per-pixel alpha looks muddy at 3×, while hard steps (3, 2, 1 pixels, then gone) stay crisp pixel art. They're drawn on top of the world, after the actors.

```
speed after t seconds = start speed × e^(−drag × t)        (frame-rate independent, like movement steering;
                                                            drag 6 loses about 99.75% of the speed per second)
size on screen        = ceil(start size × (1 − age ÷ lifetime)), at least 1
```

**After `floor.update`, the interaction target** is worked out (see "The interaction target, outline and prompt" below), and drawn later with **`draw_highlight(screen, sprites, camera, color)`** from `engine/graphics/masks.py`. `draw_hitbox` (the debug outline) draws each sprite's `mask.outline()` on the sprite's own edge pixels, which went wrong for interaction in two ways: each door tile was outlined separately, so the shared edge between the halves showed as a line down the middle, and `outline()` only traces **one** connected shape, so the chest, whose art has a transparent row between lid and body, only got its lid outlined. `draw_highlight` instead builds one combined shape from all the sprites, seals 1-pixel gaps, and draws a ring just **outside** it, so the art isn't painted over:

  ```
  grow:   every set pixel also sets its 4 neighbors       (grow_mask; 1 px bigger all round)
  shrink: grow the OUTSIDE instead, then flip it back      (invert, grow_mask, invert)
  close:  grow, then shrink   → fills 1-pixel gaps (the chest's lid seam), keeps the outer edge
  ring:   grow(shape) − shape → the pixels just outside the shape
  ```

  - The work area is the union of the sprites' rects (converted to whole-pixel `pygame.Rect`s, since sprites use float rects and a mask needs whole sizes), grown by 2 pixels on every side (`inflate(4, 4)`) so the ring and the close step aren't cut off.
  - `mask.draw(other, offset)` copies another mask's set pixels in at an offset (used to combine the sprites, and 4 times by `grow_mask`); `invert()` flips every pixel; `erase(other, offset)` clears pixels; `to_surface(setcolor=color, unsetcolor=(0, 0, 0, 0))` turns the ring into an image with everything else transparent.
  - It's rebuilt each frame for at most a couple of 16-pixel sprites, which is cheap.

**4. The floor's frame: enemies.** Right after the player moves, `update_world` calls `floor.update(dt, player)` (`game/world/floor.py`), which runs steps 4 and 5 and then finishes the floor's frame: crate breaking first if the player is rolling, then the enemies, then combat (`resolve_combat`: contacts, then swing strikes), separation and removing finished deaths, then the ground items, breaking crates and particles. Each enemy gets the solid tiles and the player's position. An enemy that isn't swinging or staggered moves with its behaviour:
- **`fly`** (Skull): ignores walls. While its `flee_timer` is running it moves away from the player, then while its `return_timer` is running it moves toward the player (both are timers from `new_timer()`, started by `trigger_flee` after a contact), within `CHASE_RANGE` (200) it chases, and otherwise it drifts slowly in a random diagonal that occasionally changes.
- **`wander_chase`** (Skeleton): collides with walls. If it has line of sight to the player (`has_line_of_sight`: no wall rect crosses the line between them), it chases. Otherwise it wanders at half speed. A type with an `"attack"` doesn't chase the player's own position but `line_up_spot`: a point `line_up_gap` (16 px) beside the player, on the side it's already on and level with them, because its swing only reaches sideways; it stops once it's within `ARRIVE_DISTANCE` (1 px) of it.
- **Stagger.** After a roll hit the enemy stands still while `is_staggered()`: its `stagger` timer (the type's `stagger_duration`: Skull 0, Skeleton 0.75 s) is running, or its knockback hasn't stopped, whichever is longer. It can't start a swing then either.
- **The swing** (types with an `"attack"` dict, the Skeleton; `game/rules/swing.py`, its state in the enemy's `swing` dict). After moving, `try_start_swing` starts a swing when the cooldown (`swing["cooldown"]`) isn't running, the player is within `range` (20 px), and the player is level with it (within `level_tolerance`, 6 px, of height): it sets `swing["active"]`, zeroes `swing["time"]`, clears `swing["landed"]` and turns to face the player. While the swing is active, the enemy doesn't move; `update_swing` counts `swing["time"]` up. The attack animation **is** the swing's clock: `swing_step(enemy)` is `int(time × frame_rate)`, the frame shown and the swing's phase at once, so the hitbox can never drift out of sync with the art:

  ```
  swing_step = int(swing["time"] × frame_rate)           frame_rate 10 → one frame per 0.1 s

  step:   0  1  2  3  4  5 │ 6  7 │ 8
          └── wind-up ───┘ │strike│ recover               9 attack frames
          0.0 s ─────── 0.6 s ─ 0.8 s ─ 0.9 s → end_swing: inactive, cooldown starts (1.0 s)
  ```

  `is_striking(enemy)` is true while the step is one of `strike_frames` (6 and 7, where the slash is drawn). `strike_rect(enemy)` is the hitbox in front of the body: `reach` (18 px) wide and as tall as the body, against the body's right edge when facing right and its left edge when facing left. When the step passes the last frame, `end_swing` ends it and starts the cooldown; it's the one place a swing finishes, shared with `interrupt_swing`. The 0.6 s wind-up is the telegraph: long enough to walk out of the swing or roll through it.
- **Knockback**, after the behaviour's movement: `update_knockback` calls the engine's `move_knockback`, which moves the enemy by `knockback_velocity * dt` with `move_and_collide`, sets the shove to 0 on any axis that hits a wall (so the enemy doesn't keep pressing into it), then fades it with `decay_velocity` at the enemy's `knockback_decay_rate`. The player's knockback when hurt uses the same function. Walls block knockback for every enemy, including flying Skulls that otherwise pass through walls. The AI keeps running during a shove for types with no stagger, and since a hit also starts the flee, both push the enemy away.

**5. The floor's frame: contact and combat** (`resolve_combat(player, enemies, particles)` in `game/rules/combat.py`). `find_player_contacts` checks enemies within 100 pixels and keeps those whose masks actually overlap the player (pixel-perfect, not rectangle). For each contact, `resolve_contact`:
- **only while the player is rolling**, deals `round(player.speed * ROLL_DAMAGE_PER_SPEED)` to the enemy, shoves it, and starts the enemy's own invulnerability window for `enemy.invulnerability_duration`, unless the enemy is already invulnerable. Rolling is the player's only attack: walking into an enemy doesn't hurt it.
- **interrupts a swing**: a roll hit on an enemy with an `attack` calls `interrupt_swing(enemy)`, which cancels a swing still in its wind-up (not once it's striking or has landed) and starts the attack cooldown, so rolling into a winding-up Skeleton stops the blow,
- **only for types with `touch_damage`** (the Skull), hurts the player with `hurt_player(player, enemy)`: the enemy's `attack_damage`, the player's invulnerability window, and a knockback away from the enemy (`PLAYER_KNOCKBACK_SPEED`, 160 px/s), unless the player is already invulnerable or is rolling. The Skeleton only hurts with its swing,
- always starts the enemy's flee (2 s) then return (3 s) timers, even when both hits were skipped, so an enemy can't stay on top of the player.

An enemy whose health reaches 0 calls `start_dying()`: it stops moving, attacking and blocking, and plays its death animation. Once `is_done_dying()`, `remove_dead_enemies` rolls its `loot_table` with `roll_loot`, spawns the drops at its center with `spawn_loot`, then removes it from `enemies`. The drops are spawned before the removal, while the enemy and its position still exist.

**Strikes** (the second half of `resolve_combat` → `resolve_strike(player, enemy)`). For every living enemy with an `attack` (an enemy killed by this frame's contacts can't strike back): if it `is_striking(enemy)`, hasn't landed this swing, and its `strike_rect(enemy)` touches the player's rect, the swing **lands**: `swing["landed"]` is set, so one swing can only hit once across both strike frames. If the player is invulnerable or rolling, the landed swing does nothing (dodged); otherwise it calls `hurt_player`, the same as a touch. It returns whether the player was hit. The strike uses rectangles, not masks: the hitbox is a rule, not a picture.

**Bodies: separation and blocking.** Solid enemies (walkers, not fliers or the dying; `enemy.is_solid()`) can't stack on each other or stand on the player, and the player can't push them:

```
walking into an enemy   → blocked: solid enemies are in player_walls, so the player stops at its edge
rolling into an enemy   → player_walls drops the enemies: the roll passes through, hits and knocks it back
roll ends inside one    → that enemy is left out of player_walls (it overlaps), separation pushes it off
an enemy walks into you → it overlaps (combat sees it), then separation pushes the ENEMY out
two enemies overlap     → separation pushes each half the overlap apart
fliers (Skull)          → not solid: pass over everything, so their touch damage can always reach you
```

`separate_enemies(enemies, player, walls)` (`game/rules/separation.py`) runs **after** contacts and strikes, so combat has had its chance to see an overlap before it's undone. For each pair of solid enemies, the engine's `push_out(rect, other_rect)` (`engine/physics/collision.py`) returns the shortest way out of the overlap, or `None` if they don't overlap: it clips the two rects, and pushes along the **thinner** side of the overlap (the minimum translation), in the direction from the other's center to this one's. Each enemy is then `shove`d half of it, in opposite directions. Then, unless the player is rolling, an enemy overlapping the player is shoved the **whole** way out: the enemy always yields, because the player is blocked by solid enemies and can't be the one moving into them. While rolling there's no push, or the roll would carry the enemy along in front of it.

```
overlap = rect.clip(other_rect)                    the shared area (width or height 0 = no overlap)

overlap.width < overlap.height  → push x by ±overlap.width     (narrower sideways: slide apart sideways)
otherwise                       → push y by ±overlap.height
sign: + when this rect's center is right of / below the other's
```

`shove` moves with `move_and_collide`, so separation can't push an enemy into a wall. One pass a frame is enough: an overlap left over (three enemies in a cluster, or one pinned against a wall) is resolved over the next frames.

`floor.player_walls(player)` is the other half: the walls `Run.update` passes to `player.update`. It's chosen before the player moves, so on the single frame a roll starts the player is still blocked (1/240 s, not noticeable). An enemy already overlapping the player is left out, because `move_and_collide` against a rect you're already inside would snap the player to its edge.

**The shove.** The direction is from the player's center to the enemy's center, normalized, so a head-on hit pushes the enemy straight back and a glancing hit pushes it sideways. If the two centers are exactly the same point, that vector has zero length and can't be normalized, so the roll direction is used instead. The shove is `direction * player.speed * KNOCKBACK_PER_SPEED * enemy.knockback_multiplier`: the player's hit strength (roll speed times `KNOCKBACK_PER_SPEED`, 1.2) scaled by how easily this enemy is pushed. Speed now drives both damage and knockback, so a full-speed roll hits hardest and a hit as the roll fades barely shoves.

```
knockback speed    = player.speed  ×  KNOCKBACK_PER_SPEED  ×  enemy.knockback_multiplier
                     └──── the player's hit strength ────┘     └─ this enemy's weight ─┘

knockback velocity = direction (player → enemy, length 1) × knockback speed
slide distance     ≈ knockback speed ÷ enemy.knockback_decay_rate
```

The player's window lasts `PLAYER_INVULNERABILITY_DURATION` (1 s), and each enemy's lasts its own `invulnerability_duration`, so each side can be hit at most once per window however long the sprites overlap. If several enemies touch the player on the same frame, the first one's hit starts the window and the rest are skipped, because the contacts are resolved one at a time. A roll blocks damage for its 0.4 s but doesn't start a window. Enemies at 0 health start dying.

```
roll damage = round(player.speed  ×  ROLL_DAMAGE_PER_SPEED)
                    └ measured ─┘     └────── 0.15 ──────┘
                      roll speed
```

`ROLL_DAMAGE_PER_SPEED` is 0.15, so a roll at about 204 pixels per second deals 31, and a 100 health enemy takes about 3 rolls. Because damage comes from measured speed and the roll push fades out, a hit near the end of a roll does less damage than one early in it, which rewards rolling *into* enemies. Because an enemy's invulnerability (1 s) lasts longer than a roll (0.4 s), each enemy can be hit at most once per roll, but different enemies each have their own window, so rolling through a group hits them all. `resolve_contact` returns `True` when the enemy was hit, and `resolve_combat` then plays the `roll_hit` sound and bursts the enemy's `hit_particles` along its knockback. `resolve_combat` returns whether any roll hit landed, `floor.update` passes that on, and `update_world` calls `hit_feedback.on_hit()` for it (a 1-pixel camera shake) and `hit_feedback.on_hurt()` when the player's health went down this frame (a 4-pixel shake and the red vignette, each only if its setting is on).

**6. Player death.** After `update_world` and the interaction target, the run checks `is_dead(player.health)`. The check is here rather than in `engine/gameplay/health.py` because `is_dead` is the rule and what happens next is the run's decision.

`is_dead` stays true on every frame once health is 0, but the death sequence must start only once. It does, because the check is only reached while the death **isn't** running: on the first dead frame the run calls `death.start()` (`game/states/death_sequence.py`), which starts its timer with `DEATH_DELAY`, stops the music and plays the `death` sound, and returns early so the exit check and camera don't update. From the next frame on, `death.is_active()` sends `update` straight to `update_death`, so the check is never reached again.

`update_death(dt)` clears the interaction target and prompt, and calls `death.update(dt, player)`, which advances the timer, updates the fade, and returns `True` once the freeze is over, when the run switches to `"game_over"`. Because this comes before `read_input()`, input, movement, enemies and contacts are all skipped, so ESC can't pause and Q can't heal during the freeze. `Run.draw` still runs every frame, so the world stays on screen, frozen as it was. Restart and Main Menu build a brand new `Run`, so the death sequence resets on its own.

**The death fade.** Each frame of the freeze, `DeathSequence.update` works out how far the fade has gone and hands the result to the player, who only draws it:

```
elapsed       = time_elapsed(timer)                         (the timer remembers DEATH_DELAY)
fade_progress = min(1.0, elapsed ÷ DEATH_FADE_DURATION)    (0.0 → 1.0, then held)
player.alpha  = round(255 × (1 − fade_progress))           (255 visible → 0 invisible)
```

- `time_elapsed(timer)` is the seconds since death: the timer counts down and remembers the duration it was started with, so time passed is that duration minus what's left.
- `fade_progress = min(1.0, elapsed / DEATH_FADE_DURATION)` goes from 0.0 at death to 1.0 when the fade is done. The `min` holds it at 1.0 afterwards.
- `player.alpha = round(255 * (1 - fade_progress))` takes the body from fully visible to invisible.

So the body fades over 1.5 s, then the empty spot holds until the 3.0 s delay ends. The alpha is set in `update`, where the timer advances, so the player's `draw` only draws. The player's blink doesn't interfere: the killing hit started the player's i-frames at 1.0 s, the freeze stops them counting down, and that frozen blink phase is a visible one.

**7. Leaving through the exit.** Climbing down takes **F**, and only once the floor is cleared: walking onto the ladder does nothing by itself, so nobody leaves a floor by accident, and F is refused while `floor.enemies_left()` is above 0. Pressing F at the exit only sets `exit_requested` (see "What `interact` does"); the leaving happens here, after the death check. If `exit_requested` is set, `finish_floor` clears it, then records the split (`splits.append(run_time)`), for every floor including the last, then checks whether there is another floor (`floor_index + 1 < len(FLOOR_ORDER)`). If there is, it calls `floor_transition.start()`, which begins the fade; `floor_index` only goes up later, when the next floor actually loads at the end of the fade. Otherwise the run is over and the run switches to `"run_complete"`. Either way `update` returns.

```
FLOOR_ORDER = [floor 0, floor 1]

exit on floor 0:  0 + 1 < 2  →  floor_transition.start()  …  update returns True: floor_index 0 → 1, load_floor(FLOOR_ORDER[1])
exit on floor 1:  1 + 1 < 2 is false  →  "run_complete"
```

The check comes after the death check, so dying and pressing F at the exit on the same frame counts as a death. A map without an exit can never set the flag, because `find_target` checks `exit_rect is not None` first (and `and` stops at the first false part, so it never tries to collide with `None`). After the switch `Run.update` is no longer called, so `run_time` stays at the finishing time.

**8. Camera.** The camera centers on the player. (Ground items, breaking crates and particles were already updated at the end of `floor.update`, in step 4.)

**What `interact` does (F).** Everything about F comes from one question, `find_target(player, floor)`: "what would F act on right now?" All of `interact.py` takes the **floor**, since chests, ground items, doors, the exit and the enemy count all belong to it. It looks in a box `REACH` (15) pixels larger than the player and returns the first match, as `(kind, sprite)`, in this priority order:
1. **A chest.**
2. **A ground item.**
3. **The exit**, when the reach box touches `exit_rect`; the target is the rect itself, since the exit isn't a sprite. It comes after the ground items, so loot lying on the ladder is picked up first.
4. **A door tile**, even without a key. Doors are checked last because a locked door is now always a target: if they came first, a potion lying next to a locked door could never be picked up, since F would keep choosing the door. With doors last, things you can always act on win.

`describe_target(player, floor, found)` turns the target into the prompt text and whether F will work, `(text, available)`. It takes the floor for the exit, whose target is only `exit_rect`, a rect with no way back to the floor's enemies:

| Target | Text | Available |
|---|---|---|
| chest | `Press F to open chest` | yes |
| ground item | `Press F to pick up <item.name>` | yes |
| door, with its key (`door.key`) | `Press F to unlock door` | yes |
| silver door, no silver key | `Silver key required to unlock door` | no |
| gold door, no gold key | `Gold key required to unlock door` | no |
| exit, enemies left | `3 enemies left to defeat` (`1 enemy left to defeat` for one) | no |
| exit, floor cleared | `Press F to climb down` | yes |

`interact` asks the same question before acting and does nothing if the target isn't available, so the key check and the clear check each live in exactly one place, shared by the prompt, the outline color and the action. Then:
- **A chest:** rolls `CHEST_LOOT`, spawns the drops around the chest, and removes the chest.
- **A door:** removes every door tile with the same `door_id`, rebuilds the solid tiles, and uses up one key of the door's own color (`remove_item(inventory, door.key)`).

Every door tile knows which key opens it (`door.key`, `"silver_key"` or `"gold_key"`, from the map's `Doors` objects), so `describe_target` and `unlock_door` just ask the door; nothing in gameplay assumes a color. The "required" prompt builds the key's name from its id: `"silver_key".replace("_", " ")` is `"silver key"`, and `.capitalize()` uppercases only the first letter, giving `"Silver key"`. So a new key color later gets its prompt for free.
- **A ground item:** adds it to the inventory. If only part of the stack fits, the rest stays on the ground with the reduced quantity.
- **The exit:** sets `floor.exit_requested = True`, and nothing else. `interact` runs early in `Run.update`, before enemies move and before the death check; if it started the floor change right there, the rest of the frame would still run, and an enemy could hit (or kill) the player mid-transition. With a flag, the actual leaving happens at frame step 7, after the death check, so dying and exiting on the same frame still counts as a death, and the split and transition code stays in one place. Every new `Floor` starts with the flag `False`, so a new floor never starts with a pending exit.

**The interaction target, outline and prompt.** Right after `floor.update`, `Run.update` stores `interact_target` (from `find_target`) and `interact_prompt` (from `describe_target`, or `None`), so they match where the player is this frame; `draw` only uses them. Both are cleared in `__init__`, in `load_floor` (the target would otherwise point at a sprite from the old floor, and its outline would show during the fade-in, which skips `update`), and every frame of the death freeze (so no prompt shows while dying).

```
find_target(player, floor) ──▶ ("chest", …) / ("item", …) / ("exit", exit_rect) / ("door", …) / None
        ├──▶ describe_target ──▶ (text, available)
        ├──▶ outline: floor.highlighted_sprites(target) → the whole door group, the exit's ladder, or the one chest or item
        │             PALETTE_CANDLE if F will work, PALETTE_STEEL if it won't
        └──▶ HUD prompt: bottom center, steel text, or blood for "key required"
```

`floor.highlighted_sprites(target)` returns the sprites to outline (it lives on the floor because it needs the floor's doors and ladder; the run only picks the color and passes `(sprites, color)` to `floor.draw`): every door tile with the target's `door_id` (a door is 2 tiles, and unlocking works on the whole group, so the outline does too), the exit's ladder (the decor tiles inside `exit_rect`, since the exit has no sprite of its own), or just the chest or item. They're drawn with `draw_highlight` (see `masks.py`), but only if the list isn't empty: a map whose exit has no ladder tile (the old Level One) would give an empty list, and `draw_highlight` would crash on `rects[0]`. An empty list counts as false, so `if sprites:` reads "if there are any". The outline and the prompt come from the same answer as F itself, so they can never disagree with what F does.

**Drawing order** (`Run.draw`, then `Floor.draw`). Steps 1 to 5 draw onto `world_surface`, at `position - camera`, and anything outside the camera (`is_on_screen`) is skipped. Every world-drawing call already takes the surface to draw on as a parameter, so tiles, items and actors don't know or care that it's a small canvas. `Run.draw` does step 1, picks the interaction outline's color, and calls `floor.draw(world_surface, player, highlight)` for steps 2 to 5; then it does steps 6 to 9 itself:
1. Fill `world_surface` with `MENU_BACKGROUND_COLOR`, clearing last frame (the map doesn't cover the whole view, so old frames would otherwise smear around the edges).
2. The pre-rendered floor surface, walls included.
3. Decor (on top of the walls it hangs on; the walls themselves are part of the floor surface in step 2), then doors, then a padlock centered on each locked door group, in the color of the key it needs (`padlock_images[key]`). `padlock_images.get(key)` returns `None` for a door with no key (only the old hand-made Level One has those), and that door is skipped instead of crashing.
4. Crates, ground items and chests (crates first, so loot dropped by a breaking crate is drawn on top of it), then the interaction outline around `highlighted_sprites` (candle or steel, from the `highlight` pair the run passed in), drawn after them so it isn't covered and before the actors so the player stays in front.
5. The player and enemies, sorted by `rect.y` so whoever is lower on screen draws in front. Enemy health bars and debug hitboxes are drawn by the entities onto the same surface, so they scale too. Then the particles, on top of the world.
6. Hand the world to the renderer: `visible_lights(floor.lights, player center, camera, time)`, then `submit_world(world_surface, camera.topleft, lights, floor.light_blockers)`. The GPU lights it, scales it ×3 with nearest-neighbor filtering, so pixels stay crisp, and draws it under the UI layer ([Architecture](architecture.md), including "Lighting").
7. The HUD, `self.hud.draw(screen, player, run_time, floor_index + 1, interact_prompt)`: the health panel (top left), the run timer (top center), the floor number (right of the timer), the quick slots (bottom left) and the interaction prompt (bottom center), on the screen at full resolution. It comes after step 6, so it lands on top of the world.
8. The inventory overlay, if open.
9. `floor_transition.draw(screen)`: during a floor transition, the black overlay at `overlay_alpha()` over everything including the HUD, then the floor card text during `"card"`.

The pause menu and the end-of-run screens call `run.draw(screen)` to show the frozen run behind them, so the world is submitted and shown under their overlay automatically.

**Inventory screen** (`InventoryUI`):
- A centered window with 4 equipment slots (`head`, `chest`, `boots`, `ability`) on the left and a 5 × 4 grid of the 20 inventory slots on the right, over the dimmed world (layout and formulas in [Game reference](game.md)).
- Clicking a grid slot swaps it with the item in your hand, which picks up, places or swaps.
- Clicking an equipment slot while holding an item equips it only if `item.slot` matches that slot name. Clicking it with an empty hand takes the equipped item off.
- Hovering an item with an empty hand shows a framed tooltip with its name, description and `value_text` (if any); hovering an empty equipment slot shows the slot's name. Stack counts show, outlined, in the slot corner.
