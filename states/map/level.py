import pygame

from entities.player.load_player import load_player
from globals import (
    GAME_SCALE,
    LEVEL_ORDER,
    MENU_BACKGROUND_COLOR,
    PALETTE_CANDLE,
    PALETTE_STEEL,
    WORLD_HEIGHT,
    WORLD_WIDTH,
)
from items.item_database import initialize_item_database
from systems import debug, interact, sound
from systems.camera import center_camera
from systems.health import is_dead
from systems.input import read_input
from systems.timer import advance_timer, is_running, new_timer, start_timer, time_left
from ui_components.floor_transition import FloorTransition
from ui_components.hud import HUD
from ui_components.inventory_ui import InventoryUI
from world.floor import Floor

# Music
LEVEL_MUSIC = "level_music"

# Death: the world freezes while the player's body fades, then the game-over screen
DEATH_DELAY = 3.0  # seconds, the whole freeze
DEATH_FADE_DURATION = 1.5  # seconds; must be no longer than DEATH_DELAY

# True makes the inventory pause the game (it's an overlay by default)
INVENTORY_PAUSES_GAME = False


class Level:
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

        # Which entry of LEVEL_ORDER is being played, and its map
        self.level_index = 0
        self.load_floor(LEVEL_ORDER[self.level_index])

        self.show_inventory = False
        self.inventory_ui = InventoryUI(self.player.inventory)

        self.interact_target = None
        self.interact_prompt = None

        self.dying = False
        self.death_timer = new_timer()

        # Fade to black, "Floor N" card, fade back in
        self.floor_transition = FloorTransition()

    def load_floor(self, map_path):
        self.floor = Floor(map_path, self.item_database)

        # Move the same player (health, inventory, gear) to this floor's spawn
        self.player.rect.center = self.floor.player_spawn
        self.player.pos.xy = self.player.rect.topleft
        self.player.velocity.update(0, 0)
        center_camera(self.player.rect.center)

        self.interact_target = None
        self.interact_prompt = None

    def enter(self):
        sound.play_music(LEVEL_MUSIC)

    def update(self, dt):
        if self.dying:
            self.interact_target = None
            self.interact_prompt = None

            advance_timer(self.death_timer, dt)
            elapsed = DEATH_DELAY - time_left(self.death_timer)
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

        if self.player.intent["debug"]:
            debug.toggle_hitboxes()

        if self.player.intent["interact"]:
            interact.interact(self.player, self.floor)

        if self.player.intent["inventory"]:
            if self.show_inventory:
                if self.inventory_ui.return_held_item(self.player.inventory):
                    self.show_inventory = False
            else:
                self.show_inventory = True

        if self.show_inventory and self.player.intent["mouse_left_click"] is not None:
            self.inventory_ui.handle_click(
                self.player.intent["mouse_left_click"], self.player.inventory
            )

        if self.show_inventory and INVENTORY_PAUSES_GAME:
            return

        self.player.update(dt, self.floor.solid_tiles)
        self.floor.update(dt, self.player)

        # What F would act on now; drives the outline and the HUD prompt
        self.interact_target = interact.find_target(self.player, self.floor)
        self.interact_prompt = None
        if self.interact_target is not None:
            self.interact_prompt = interact.describe_target(
                self.player, self.interact_target
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
            if self.level_index + 1 < len(LEVEL_ORDER):
                self.floor_transition.start()
            else:
                self.game_state_manager.set_state("level_complete")
            return

        center_camera(self.player.rect.center)

    def update_transition(self, dt):
        if self.floor_transition.update(dt):
            self.level_index += 1
            self.load_floor(LEVEL_ORDER[self.level_index])
            self.floor_transition.set_floor_number(self.level_index + 1)

    def draw(self, screen):
        self.world_surface.fill(MENU_BACKGROUND_COLOR)

        # Outline what F would act on: candle if it will work, steel if not
        highlight = None
        if self.interact_target is not None:
            _, available = self.interact_prompt
            color = PALETTE_CANDLE if available else PALETTE_STEEL
            highlight = (self.floor.highlighted_sprites(self.interact_target), color)

        self.floor.draw(self.world_surface, self.player, highlight)

        scaled_world = pygame.transform.scale_by(self.world_surface, GAME_SCALE)
        screen.blit(scaled_world, (0, 0))

        self.hud.draw(
            screen,
            self.player,
            self.run_time,
            self.level_index + 1,
            self.interact_prompt,
        )

        if self.show_inventory:
            self.inventory_ui.draw(screen, self.player.inventory)

        self.floor_transition.draw(screen)
