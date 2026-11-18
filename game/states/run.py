import pygame

from constants import (
    FLOOR_ORDER,
    MENU_BACKGROUND_COLOR,
    PALETTE_CANDLE,
    PALETTE_STEEL,
    WORLD_HEIGHT,
    WORLD_WIDTH,
)
from engine.core import debug, settings
from engine.core.timer import (
    advance_timer,
    is_running,
    new_timer,
    start_timer,
    time_elapsed,
)
from engine.gameplay.health import is_dead
from engine.graphics.camera import center_camera, new_camera
from engine.graphics.lighting import visible_lights
from engine.graphics.renderer import submit_world
from engine.graphics.shake import new_shake, start_shake, update_shake
from engine.io import sound
from game.data.item_database import initialize_item_database
from game.data.light_types import LIGHT_TYPES
from game.entities.player.load_player import load_player
from game.rules import interact
from game.rules.input import read_input
from game.ui.floor_transition import FloorTransition
from game.ui.hud import HUD
from game.ui.hurt_vignette import HurtVignette
from game.ui.inventory_ui import InventoryUI
from game.world.floor import Floor

# Music
LEVEL_MUSIC = "level_music"

# Death: the world freezes while the player's body fades, then the game-over screen
DEATH_DELAY = 3.0  # seconds, the whole freeze
DEATH_FADE_DURATION = 1.5  # seconds; must be no longer than DEATH_DELAY

# True makes the inventory pause the game (it's an overlay by default)
INVENTORY_PAUSES_GAME = False

# Hit feel
HIT_SHAKE_STRENGTH = 1  # world pixels
HURT_SHAKE_STRENGTH = 4  # world pixels


class Run:
    def __init__(self, game_state_manager):
        self.game_state_manager = game_state_manager

        # The world is drawn here at 1x, then scaled to the screen
        self.world_surface = pygame.Surface((WORLD_WIDTH, WORLD_HEIGHT))

        # Run timer
        self.run_time = 0.0

        # run_time at each exit touched, one per finished floor
        self.splits = []

        # Item templates
        self.item_database = initialize_item_database()

        # Player Setup, placed on each floor by load_floor
        self.player = load_player((0, 0))

        # HUD setup
        self.hud = HUD(self.item_database)

        # The visible part of the world, centered on the player each frame
        self.camera = new_camera((WORLD_WIDTH, WORLD_HEIGHT))

        # Which entry of FLOOR_ORDER is being played, and its map
        self.floor_index = 0
        self.load_floor(FLOOR_ORDER[self.floor_index])

        self.inventory_open = False
        self.inventory_ui = InventoryUI(self.player.inventory)

        self.interact_target = None
        self.interact_prompt = None

        self.dying = False
        self.death_timer = new_timer()

        self.shake = new_shake()

        self.hurt_vignette = HurtVignette()

        # Fade to black, "Floor N" card, fade back in
        self.floor_transition = FloorTransition()

    def load_floor(self, map_path):
        self.floor = Floor(map_path, self.item_database)

        # Move the same player (health, inventory, gear) to this floor's spawn
        self.player.rect.center = self.floor.player_spawn
        self.player.pos.xy = self.player.rect.topleft
        self.player.velocity.update(0, 0)
        center_camera(self.camera, self.player.rect.center)

        self.interact_target = None
        self.interact_prompt = None

    def enter(self):
        sound.play_music(LEVEL_MUSIC)

    def update(self, dt):
        self.hurt_vignette.update(dt)
        if self.dying:
            self.interact_target = None
            self.interact_prompt = None

            advance_timer(self.death_timer, dt)
            elapsed = time_elapsed(self.death_timer)
            fade_progress = min(1.0, elapsed / DEATH_FADE_DURATION)
            self.player.alpha = round(255 * (1 - fade_progress))

            if not is_running(self.death_timer):
                self.game_state_manager.set_state("game_over")
            return

        if self.floor_transition.is_active():
            self.update_transition(dt)
            return

        self.player.intent = read_input()

        if self.player.intent["pause"]:
            self.game_state_manager.set_state("options")
            sound.play_sfx("pause")
            return

        self.run_time += dt

        update_shake(self.shake, dt)

        if self.player.intent["debug"]:
            debug.toggle_hitboxes()

        if self.player.intent["interact"]:
            interact.interact(self.player, self.floor)

        if self.player.intent["inventory"]:
            if self.inventory_open:
                if self.inventory_ui.return_held_item(self.player.inventory):
                    self.inventory_open = False
            else:
                self.inventory_open = True

        if self.inventory_open and self.player.intent["mouse_left_click"] is not None:
            self.inventory_ui.handle_click(
                self.player.intent["mouse_left_click"], self.player.inventory
            )

        if self.inventory_open and INVENTORY_PAUSES_GAME:
            return

        health_before = self.player.health["current"]
        self.player.update(dt, self.floor.player_walls(self.player))
        self.floor.update(dt, self.player)

        if self.floor.hit_landed:
            self.shake_camera(HIT_SHAKE_STRENGTH)
        if self.player.health["current"] < health_before:
            self.shake_camera(HURT_SHAKE_STRENGTH)
            if settings.get_setting("hurt_vignette_enabled"):
                self.hurt_vignette.start()

        # What F would act on now; drives the outline and the HUD prompt
        self.interact_target = interact.find_target(self.player, self.floor)
        self.interact_prompt = None
        if self.interact_target is not None:
            self.interact_prompt = interact.describe_target(
                self.player, self.floor, self.interact_target
            )

        if is_dead(self.player.health) and not self.dying:
            self.dying = True
            start_timer(self.death_timer, DEATH_DELAY)
            sound.stop_music()
            sound.play_sfx("death")
            return

        if self.floor.exit_requested:
            self.floor.exit_requested = False
            self.splits.append(self.run_time)
            if self.floor_index + 1 < len(FLOOR_ORDER):
                self.floor_transition.start()
            else:
                self.game_state_manager.set_state("run_complete")
            return

        self.update_camera()

    def update_transition(self, dt):
        if self.floor_transition.update(dt):
            self.floor_index += 1
            self.load_floor(FLOOR_ORDER[self.floor_index])
            self.floor_transition.set_floor_number(self.floor_index + 1)

    def shake_camera(self, strength):
        if settings.get_setting("screen_shake_enabled"):
            start_shake(self.shake, strength)

    def update_camera(self):
        x, y = self.player.rect.center
        offset_x, offset_y = self.shake["offset"]
        center_camera(self.camera, (x + offset_x, y + offset_y))

    def draw(self, screen):
        self.world_surface.fill(MENU_BACKGROUND_COLOR)

        # Outline what F would act on: candle if it will work, steel if not
        highlight = None
        if self.interact_target is not None:
            _, available = self.interact_prompt
            color = PALETTE_CANDLE if available else PALETTE_STEEL
            highlight = (self.floor.highlighted_sprites(self.interact_target), color)

        self.floor.draw(self.world_surface, self.player, self.camera, highlight)

        time = pygame.time.get_ticks() / 1000
        # The player's light first, so it's never the one cut at MAX_LIGHTS
        lights = [("player", self.player.rect.center)] + self.floor.lights
        visible = visible_lights(lights, LIGHT_TYPES, self.camera, time)
        submit_world(
            self.world_surface, self.camera.topleft, visible, self.floor.light_blockers
        )

        self.hurt_vignette.draw(screen)

        self.hud.draw(
            screen,
            self.player,
            self.run_time,
            self.floor_index + 1,
            self.interact_prompt,
        )

        if self.inventory_open:
            self.inventory_ui.draw(screen, self.player.inventory)

        self.floor_transition.draw(screen)
