import pygame

from entities.player.load_player import load_player
from globals import (
    GAME_SCALE,
    LEVEL_ORDER,
    MENU_BACKGROUND_COLOR,
    PALETTE_CANDLE,
    PALETTE_STEEL,
    PALETTE_VOID,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    WORLD_HEIGHT,
    WORLD_WIDTH,
)
from items.item_database import initialize_item_database
from systems import debug, interact, sound
from systems.camera import camera, center_camera, is_on_screen
from systems.health import is_dead
from systems.hitbox import draw_highlight
from systems.input import read_input
from systems.particles import draw_particles
from systems.timer import advance_timer, is_running, new_timer, start_timer, time_left
from ui_components.hud import HUD
from ui_components.inventory_ui import InventoryUI
from ui_components.text_label import TextLabel
from ui_components.text_layout import centered_text_x, centered_text_y
from world.floor import Floor

LEVEL_MUSIC = "level_music"

DEATH_DELAY = 3.0
DEATH_FADE_DURATION = 1.5

FADE_DURATION = 0.4
FLOOR_CARD_DURATION = 1.0
MAX_TRANSITION_DT = 1 / 30

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

        # Floor transition: None while playing, else "fade_out", "card", or "fade_in"
        self.transition_phase = None
        self.transition_timer = new_timer()
        self.fade_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.fade_overlay.fill(PALETTE_VOID)
        self.floor_label = TextLabel("", font_size=48)

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

        if self.transition_phase is not None:
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
                self.transition_phase = "fade_out"
                start_timer(self.transition_timer, FADE_DURATION)
            else:
                self.game_state_manager.set_state("level_complete")
            return

        center_camera(self.player.rect.center)

    def update_transition(self, dt):
        advance_timer(self.transition_timer, min(dt, MAX_TRANSITION_DT))
        if is_running(self.transition_timer):
            return

        if self.transition_phase == "fade_out":
            self.level_index += 1
            self.load_floor(LEVEL_ORDER[self.level_index])
            self.show_floor_card()
            self.transition_phase = "card"
            start_timer(self.transition_timer, FLOOR_CARD_DURATION)
        elif self.transition_phase == "card":
            self.transition_phase = "fade_in"
            start_timer(self.transition_timer, FADE_DURATION)
        else:
            self.transition_phase = None

    def draw(self, screen):
        self.world_surface.fill(MENU_BACKGROUND_COLOR)

        # Floor
        self.world_surface.blit(self.floor.map_surface, (-camera.x, -camera.y))

        # Static tiles: decor, walls, doors
        for group in [
            self.floor.decor_tiles,
            self.floor.wall_tiles,
            self.floor.door_tiles,
        ]:
            for sprite in group:
                if is_on_screen(sprite.rect):
                    sprite.draw(self.world_surface)

        # Padlocks on locked doors, in the color of the key they need
        for key, center in self.floor.padlocks:
            image = self.floor.padlock_images.get(key)
            if image is None:
                continue
            padlock_rect = image.get_rect(
                center=(center[0] - camera.x, center[1] - camera.y)
            )
            self.world_surface.blit(image, padlock_rect)

        # Ground items and chests
        for group in [self.floor.crates, self.floor.ground_items, self.floor.chests]:
            for sprite in group:
                if is_on_screen(sprite.rect):
                    sprite.draw(self.world_surface, camera)

        # Outline what F would act on: candle if it will work, steel if not
        if self.interact_target is not None:
            _, available = self.interact_prompt
            outline_color = PALETTE_CANDLE if available else PALETTE_STEEL
            highlight_sprites = self.interact_highlight()
            if highlight_sprites:
                draw_highlight(
                    self.world_surface, highlight_sprites, camera, outline_color
                )

        # Actors, sorted by y so lower ones draw on top
        actors = [self.player] + self.floor.enemies
        actors = sorted(actors, key=lambda actor: actor.rect.y)

        for actor in actors:
            if is_on_screen(actor.rect):
                actor.draw(self.world_surface, camera)

        # Particles, on top of the world
        draw_particles(self.world_surface, self.floor.particles, camera)

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

        if self.transition_phase is not None:
            self.fade_overlay.set_alpha(self.transition_alpha())
            screen.blit(self.fade_overlay, (0, 0))

            if self.transition_phase == "card":
                self.floor_label.draw(screen)

    def interact_highlight(self):
        kind, target = self.interact_target

        if kind == "door":
            return [
                door for door in self.floor.door_tiles if door.door_id == target.door_id
            ]
        if kind == "exit":
            return [
                tile
                for tile in self.floor.decor_tiles
                if tile.rect.colliderect(self.floor.exit_rect)
            ]

        return [target]

    def show_floor_card(self):
        self.floor_label.update_text(f"Floor {self.level_index + 1}")
        text_surface = self.floor_label.text_surface
        self.floor_label.pos = (
            centered_text_x(text_surface, SCREEN_WIDTH // 2),
            centered_text_y(text_surface, SCREEN_HEIGHT // 2),
        )

    def transition_alpha(self):
        fade_left = time_left(self.transition_timer) / FADE_DURATION

        if self.transition_phase == "fade_out":
            return round(255 * (1 - fade_left))
        if self.transition_phase == "fade_in":
            return round(255 * fade_left)
        return 255
