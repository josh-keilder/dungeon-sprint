import random

import pygame

from entities.enemies.load_enemies import load_enemies
from items.loot_table_data import CRATE_LOOT
from systems import sound
from systems.assets import load_image
from systems.camera import camera, is_on_screen
from systems.collision import find_player_contacts
from systems.combat import resolve_contact
from systems.health import is_dead
from systems.hitbox import draw_highlight
from systems.loot import roll_loot
from systems.particles import CRATE_DEBRIS, draw_particles, emit_burst, update_particles
from systems.roll import is_rolling
from world.map_loader import load_level_data
from world.objects import WorldItem

# Loot scatters a little around where it came from
LOOT_SCATTER_X = 10  # world pixels
LOOT_SCATTER_Y = 5  # world pixels

# Crate breaking: how close (in pixels) a rolling player must be to break a crate
CRATE_TOUCH_MARGIN = 2

# Padlock art, by the key that opens the door
PADLOCK_IMAGE_PATHS = {
    "silver_key": "Assets/Objects/padlock_silver.png",
    "gold_key": "Assets/Objects/padlock_gold.png",
}


class Floor:
    def __init__(self, map_path, item_database):
        self.item_database = item_database

        # Map data
        level_data = load_level_data(map_path)
        self.map_surface = level_data["map_surface"]
        self.decor_tiles = level_data["decor_tiles"]
        self.wall_tiles = level_data["wall_tiles"]
        self.door_tiles = level_data["door_tiles"]
        self.chests = level_data["chests"]
        self.crates = level_data["crates"]
        self.exit_rect = level_data["exit_rect"]
        self.player_spawn = level_data["player_spawn"]

        # Things that appear and change during play
        self.ground_items = pygame.sprite.Group()
        self.particles = []
        self.exit_requested = False

        # Placed items (keys), from the map's Items layer
        for item_id, center in level_data["placed_items"]:
            WorldItem(
                groups=self.ground_items,
                pos=center,
                item_data=self.item_database[item_id],
                quantity=1,
            )

        # Enemies
        self.enemies = load_enemies(level_data["enemy_spawns"])

        # Padlocks and solid tiles, rebuilt whenever the doors or crates change
        self.padlock_images = {
            key: load_image(path) for key, path in PADLOCK_IMAGE_PATHS.items()
        }
        self.refresh_walls()
        self.refresh_padlocks()

    def update(self, dt, player):
        if is_rolling(player.roll):
            self.break_touched_crates(player)

        for enemy in self.enemies:
            enemy.update(dt, self.solid_tiles, player.pos)
        self.resolve_enemy_contacts(player)

        self.ground_items.update(dt)
        self.update_crates(dt)
        update_particles(self.particles, dt)

    def draw(self, surface, player, highlight=None):
        # Floor
        surface.blit(self.map_surface, (-camera.x, -camera.y))

        # Static tiles: decor, walls, doors
        for group in [self.decor_tiles, self.wall_tiles, self.door_tiles]:
            for sprite in group:
                if is_on_screen(sprite.rect):
                    sprite.draw(surface)

        # Padlocks on locked doors, in the color of the key they need
        for key, center in self.padlocks:
            image = self.padlock_images.get(key)
            if image is None:
                continue
            padlock_rect = image.get_rect(
                center=(center[0] - camera.x, center[1] - camera.y)
            )
            surface.blit(image, padlock_rect)

        # Crates, ground items and chests
        for group in [self.crates, self.ground_items, self.chests]:
            for sprite in group:
                if is_on_screen(sprite.rect):
                    sprite.draw(surface, camera)

        # Outline what F would act on
        if highlight is not None:
            sprites, color = highlight
            if sprites:
                draw_highlight(surface, sprites, camera, color)

        # Actors, sorted by y so lower ones draw on top
        actors = sorted([player] + self.enemies, key=lambda actor: actor.rect.y)
        for actor in actors:
            if is_on_screen(actor.rect):
                actor.draw(surface, camera)

        # Particles, on top of the world
        draw_particles(surface, self.particles, camera)

    def highlighted_sprites(self, target):
        kind, sprite = target

        if kind == "door":
            return [door for door in self.door_tiles if door.door_id == sprite.door_id]
        if kind == "exit":
            return [
                tile
                for tile in self.decor_tiles
                if tile.rect.colliderect(self.exit_rect)
            ]

        return [sprite]

    def resolve_enemy_contacts(self, player):
        for enemy in find_player_contacts(player, self.enemies):
            enemy_hit = resolve_contact(player, enemy)
            if enemy_hit:
                sound.play_sfx("roll_hit")

            if is_dead(enemy.health):
                drops = roll_loot(enemy.loot_table)
                self.spawn_loot(drops, enemy.rect.center)
                self.enemies.remove(enemy)

    def break_touched_crates(self, player):
        touch_box = player.rect.inflate(CRATE_TOUCH_MARGIN, CRATE_TOUCH_MARGIN)
        broke_any = False

        for crate in self.crates:
            if not crate.breaking and touch_box.colliderect(crate.rect):
                crate.start_breaking()
                drops = roll_loot(CRATE_LOOT)
                self.spawn_loot(drops, crate.rect.center)
                broke_any = True

        if broke_any:
            self.refresh_walls()

    def update_crates(self, dt):
        for crate in self.crates.sprites():
            crate.update(dt)

            if crate.done_breaking:
                emit_burst(self.particles, crate.rect.center, CRATE_DEBRIS)
                crate.kill()

    def unlock_door(self, door_id):
        for door in self.door_tiles.sprites():
            if door.door_id == door_id:
                door.kill()

        self.refresh_walls()
        self.refresh_padlocks()

    def refresh_walls(self):
        solid_crates = [crate for crate in self.crates if not crate.breaking]
        self.solid_tiles = list(self.wall_tiles) + list(self.door_tiles) + solid_crates

    def refresh_padlocks(self):
        doors_by_id = {}
        for door in self.door_tiles:
            doors_by_id.setdefault(door.door_id, []).append(door)

        self.padlocks = []
        for doors in doors_by_id.values():
            rects = [door.rect for door in doors]
            door_area = rects[0].unionall(rects[1:])
            self.padlocks.append((doors[0].key, door_area.center))

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
