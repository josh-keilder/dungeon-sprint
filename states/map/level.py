import random

import pygame

from entities.enemies.load_enemies import load_enemies
from entities.player.load_player import load_player
from globals import (
    GAME_SCALE,
    LEVEL_ORDER,
    MENU_BACKGROUND_COLOR,
    PALETTE_STEEL,
    PALETTE_VOID,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    UNLOCK_DOOR_DISTANCE,
    WORLD_HEIGHT,
    WORLD_WIDTH,
    YELLOW,
)
from items.item_database import initialize_item_database
from items.items import WorldItem
from states.map.map_loader import load_level_data
from systems import debug, interact, sound
from systems.camera import camera, center_camera, is_on_screen
from systems.collision import find_player_contacts
from systems.combat import resolve_contact
from systems.health import is_dead
from systems.hitbox import draw_hitbox
from systems.input import read_input
from systems.loot import roll_loot
from systems.timer import advance_timer, is_running, new_timer, start_timer, time_left
from ui_components.hud import HUD, centered_text_y
from ui_components.inventory_ui import InventoryUI
from ui_components.text_label import TextLabel

LOOT_SCATTER_X = 10
LOOT_SCATTER_Y = 5

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

        self.dying = False
        self.death_timer = new_timer()

        # Floor transition: None while playing, else "fade_out", "card", or "fade_in"
        self.transition_phase = None
        self.transition_timer = new_timer()
        self.fade_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.fade_overlay.fill(PALETTE_VOID)
        self.floor_label = TextLabel("", font_size=48)

    def load_floor(self, map_path):
        # Ground items, spawned during play; left-behind items don't carry over
        self.ground_items = pygame.sprite.Group()

        level_data = load_level_data(map_path)
        self.map_surface = level_data["map_surface"]
        self.decor_tiles = level_data["decor_tiles"]
        self.wall_tiles = level_data["wall_tiles"]
        self.door_tiles = level_data["door_tiles"]
        self.chests = level_data["chests"]
        self.exit_rect = level_data["exit_rect"]

        # Placed items (keys), from the map's Items layer
        for item_id, center in level_data["placed_items"]:
            WorldItem(
                groups=self.ground_items,
                pos=center,
                item_data=self.item_database[item_id],
                quantity=1,
            )

        # Enemy Spawning
        self.enemies = load_enemies(level_data["enemy_spawns"])

        # Everything that blocks movement: walls and locked doors
        self.solid_tiles = []
        self.refresh_walls()

        # Move the same player (health, inventory, gear) to this floor's spawn
        self.player.rect.center = level_data["player_spawn"]
        self.player.pos.xy = self.player.rect.topleft
        self.player.velocity.update(0, 0)
        center_camera(self.player.rect.center)

    def enter(self):
        sound.play_music(LEVEL_MUSIC)

    def update(self, dt):
        if self.dying:
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
            interact.interact(self.player, self)

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

        self.player.update(dt, self.solid_tiles)
        for enemy in self.enemies:
            enemy.update(dt, self.solid_tiles, self.player.pos)

        contacts = find_player_contacts(self.player, self.enemies)

        for enemy in contacts:
            enemy_hit = resolve_contact(self.player, enemy)
            if enemy_hit:
                sound.play_sfx("roll_hit")

            if is_dead(enemy.health):
                drops = roll_loot(enemy.loot_table)
                self.spawn_loot(drops, enemy.rect.center)
                self.enemies.remove(enemy)

        if is_dead(self.player.health) and not self.dying:
            self.dying = True
            start_timer(self.death_timer, DEATH_DELAY)
            sound.stop_music()
            sound.play_sfx("death")
            return

        if self.exit_rect is not None and self.player.rect.colliderect(self.exit_rect):
            self.splits.append(self.run_time)
            if self.level_index + 1 < len(LEVEL_ORDER):
                self.transition_phase = "fade_out"
                start_timer(self.transition_timer, FADE_DURATION)
            else:
                self.game_state_manager.set_state("level_complete")
            return

        self.ground_items.update(dt)
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
        self.world_surface.blit(self.map_surface, (-camera.x, -camera.y))

        # Static tiles: decor, walls, doors
        for group in [self.decor_tiles, self.wall_tiles, self.door_tiles]:
            for sprite in group:
                if is_on_screen(sprite.rect):
                    sprite.draw(self.world_surface)

                    # Highlight doors when player is nearby
                    if group == self.door_tiles:
                        if (
                            sprite.pos.distance_to(self.player.pos)
                            < UNLOCK_DOOR_DISTANCE
                        ):
                            draw_hitbox(
                                self.world_surface,
                                sprite.image,
                                sprite.rect,
                                camera,
                                PALETTE_STEEL,
                            )

        if self.exit_rect is not None:
            pygame.draw.rect(
                self.world_surface, YELLOW, self.exit_rect.move(-camera.x, -camera.y), 2
            )

        # Ground items and chests
        for group in [self.ground_items, self.chests]:
            for sprite in group:
                if is_on_screen(sprite.rect):
                    sprite.draw(self.world_surface, camera)

        # Actors, sorted by y so lower ones draw on top
        actors = [self.player] + self.enemies
        actors = sorted(actors, key=lambda actor: actor.rect.y)

        for actor in actors:
            if is_on_screen(actor.rect):
                actor.draw(self.world_surface, camera)

        scaled_world = pygame.transform.scale_by(self.world_surface, GAME_SCALE)
        screen.blit(scaled_world, (0, 0))

        self.hud.draw(screen, self.player, self.run_time, self.level_index + 1)

        if self.show_inventory:
            self.inventory_ui.draw(screen, self.player.inventory)

        if self.transition_phase is not None:
            self.fade_overlay.set_alpha(self.transition_alpha())
            screen.blit(self.fade_overlay, (0, 0))

            if self.transition_phase == "card":
                self.floor_label.draw(screen)

    def show_floor_card(self):
        self.floor_label.update_text(f"Floor {self.level_index + 1}")
        text_surface = self.floor_label.text_surface
        text_bounds = text_surface.get_bounding_rect()
        text_x = (SCREEN_WIDTH // 2 - text_bounds.centerx) // GAME_SCALE * GAME_SCALE
        text_y = centered_text_y(text_surface, SCREEN_HEIGHT // 2)
        self.floor_label.pos = (text_x, text_y)

    def transition_alpha(self):
        fade_left = time_left(self.transition_timer) / FADE_DURATION

        if self.transition_phase == "fade_out":
            return round(255 * (1 - fade_left))
        if self.transition_phase == "fade_in":
            return round(255 * fade_left)
        return 255

    def unlock_door(self, door_id):
        for door in self.door_tiles.sprites():
            if door.door_id == door_id:
                door.kill()

        self.refresh_walls()

    def refresh_walls(self):
        self.solid_tiles = list(self.wall_tiles) + list(self.door_tiles)

    def spawn_loot(self, drops, center):
        for item_id, quantity in drops:
            item_data = self.item_database[item_id]
            offset_x = random.randint(-LOOT_SCATTER_X, LOOT_SCATTER_X)
            offset_y = random.randint(-LOOT_SCATTER_Y, LOOT_SCATTER_Y)

            WorldItem(
                groups=self.ground_items,
                pos=(center[0] + offset_x, center[1] + offset_y),
                item_data=item_data,
                quantity=quantity,
            )
