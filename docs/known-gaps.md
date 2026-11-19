# Known gaps and planned work

**Combat:**
- Death fades the player's body out as a stand-in until real character art and a death animation exist.
- A per-enemy speed drain on contact (set in `ENEMY_TYPES`) is planned.
- A stagger (no AI movement while an enemy is being knocked back) is a possible follow-up if hits feel too floaty.
- `KNOCKBACK_PER_SPEED` could move into the player's `base_stats` if gear should ever boost knockback, so `compute_stats` picks up the bonus.
- The `defense` stat exists but isn't used yet.
- A Skeleton starts a swing by distance, but the strike box only reaches left or right, so a player standing straight above or below it can make it swing at nothing. Fine for now; a vertical strike (or only swinging when the player is level with it) is a possible follow-up.
- Skulls aren't solid, so several can overlap each other.
- Solid enemies can pin a walking player against a wall; rolling through them is the way out, and is on its cooldown sometimes. Part of the design, to judge in the tuning pass.
- Enemy hits have no particles yet (bone chips for Skeletons, sparks for Skulls; in the backlog).
- With the current stats, roll speed only varies between about 200 and 270 pixels per second, so roll damage varies only a little until movement tuning and gear change it.

**Movement:**
- All movement values are first-pass numbers. They will be tuned once the basic gameplay features are in and levels are being built, with feedback from playtesters.
- Speeds are in world pixels per second, so the player covers the same number of tiles per second at any `GAME_SCALE`. At 3× the screen shows a third as many tiles across, so movement looks about 3× faster on screen than it did at 1×. Something to judge in the tuning pass.

**Content and map:**
- Level One's `Keys` tile layer is unused and hidden: it was only a visual stand-in, and the `Items` object layer, which the loader reads, replaces it.
- `start_new_run()` reloads the map inside the update of whichever menu calls it (`RunEndScreen` or `OptionsMenu`), so the first frame of the new run gets a large `dt` covering the load time.
- If the inventory is open when the player touches an exit, it stays open underneath the floor transition (harmless; clicks are ignored until play resumes).
- Easy has 1 of its 5 floors so far, so a run currently ends at floor 1's exit, and the floor transition and split rows only show once floor 2 exists.
- The old hand-made `Dungeon_Level_One.tmx` still uses a `Logic_Layer`, which the loader no longer reads, so its doors load without ids. `Logic_Tile.tsx`, `Logic_Tiles.tsx` and their PNGs are only kept for it, and can go with it.
- The ASCII converter needs doors exactly 2 tiles long and walls at least 2 thick. Decor is automatic and first-pass (its values will need tuning), it places only keys, and several `X` cells become one bounding rect, so they should form a rectangle.
- There are no rules for room sizes yet. They'll be needed before more floors: hand-made floors and Hard's generated ones should follow the same size rules, so floors feel consistent.
- The old hand-made `Dungeon_Level_One.tmx` has no ladder tile, so its exit is invisible in-game now that the yellow outline is gone. It's only kept as Tiled reference.

**Lighting and visuals:**
- All light values are first-pass (`AMBIENT_LIGHT`, `LIGHT_TYPES`, flicker), to judge again as floors and art change.
- Shadows follow the tile grid, so their edges are hard rather than soft, and a wall's whole tile is lit or not. Light walks in 4-pixel steps, so a walk that only clips a wall's corner can slip past it.
- Torches and candlesticks start on random frames but switch frames on the same tick (every decor timer starts at 0 at the shared `DECOR_ANIMATION_SPEED`), so their animation looks in step next to the out-of-step flicker. A random starting timer, and maybe a slightly different speed per object, is in the backlog.
- The potion is one still frame of the pack's small red flask; the pack's `flasks` folder has it as a 4-frame animation (and three more flasks for future potions). In the backlog, the same route as the keys' strips.

**HUD:**
- The health panel has a fixed width, so health text wider than `25/25` (for example `100/100`) won't fit. Its width should be worked out from the text before max health goes above 99.
- The floor panel also has a fixed width, which fits up to `F9`.
- The end screen's split table fits up to 5 floors above the buttons.
- The menus and end screens use font sizes 32 and 64, which aren't on the 24/48 pixel grid the HUD follows; to be fixed in one menu pass.

**Menus and saving:**
- Choosing Main Menu from the pause menu throws the run away with no warning. A confirmation box that tells the player their progress won't be saved is planned. It would go in the Options Main Menu branch, before `start_new_run`.
- There is no saving system yet, so a run can't be saved and resumed later. Once saving exists, the confirmation box can change its wording, or save first.
