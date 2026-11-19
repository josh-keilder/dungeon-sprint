import random

import pygame

from engine.core import debug
from engine.core.assets import load_image
from engine.gameplay.loot import roll_loot
from engine.graphics.camera import is_on_screen, world_to_screen
from engine.graphics.lighting import light_blockers
from engine.graphics.masks import draw_highlight, draw_hitbox
from engine.graphics.particles import draw_particles, emit_burst, update_particles
from engine.physics.collision import edge_walls
from game.data.constants import TILE_SIZE
from game.data.loot_table_data import CRATE_LOOT
from game.data.palette import BLUE
from game.data.particle_presets import CRATE_DEBRIS
from game.entities.enemies.load_enemies import load_enemies
from game.rules.combat import resolve_combat
from game.rules.roll import is_rolling
from game.rules.separation import separate_enemies
from game.world.map_loader import load_floor_data
from game.world.objects import GroundItem

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
        floor_data = load_floor_data(map_path)
        self.map_surface = floor_data["map_surface"]
        self.decor_tiles = floor_data["decor_tiles"]
        self.wall_tiles = floor_data["wall_tiles"]
        self.edge_walls = edge_walls(self.wall_tiles, TILE_SIZE)
        self.door_tiles = floor_data["door_tiles"]
        self.chests = floor_data["chests"]
        self.crates = floor_data["crates"]
        self.exit_rect = floor_data["exit_rect"]
        self.player_spawn = floor_data["player_spawn"]
        self.lights = floor_data["lights"]

        # Things that appear and change during play
        self.ground_items = pygame.sprite.Group()
        self.particles = []
        self.exit_requested = False

        # Placed items (keys), from the map's Items layer
        for item_id, center in floor_data["placed_items"]:
            GroundItem(
                groups=self.ground_items,
                pos=center,
                item=self.item_database[item_id],
                quantity=1,
            )

        # Enemies
        self.enemies = load_enemies(floor_data["enemy_spawns"])

        # Padlocks and solid tiles, rebuilt whenever the doors or crates change
        self.padlock_images = {
            key: load_image(path) for key, path in PADLOCK_IMAGE_PATHS.items()
        }
        self.refresh_solid_rects()
        self.refresh_light_blockers()
        self.refresh_padlocks()

    def update(self, dt, player):
        if is_rolling(player.roll):
            self.break_touched_crates(player)

        for enemy in self.enemies:
            enemy.update(dt, self.solid_rects, player.pos)
        hit_landed = resolve_combat(player, self.enemies, self.particles)
        separate_enemies(self.enemies, player, self.solid_rects)
        self.remove_dead_enemies()

        self.decor_tiles.update(dt)
        self.ground_items.update(dt)
        self.update_crates(dt)
        update_particles(self.particles, dt)

        return hit_landed

    def draw(self, surface, player, camera, highlight=None):
        # Floor
        surface.blit(self.map_surface, world_to_screen(camera, (0, 0)))

        # Static tiles: decor on the walls (drawn into map_surface), then doors
        for group in [self.decor_tiles, self.door_tiles]:
            for sprite in group:
                if is_on_screen(camera, sprite.rect):
                    sprite.draw(surface, camera)

        # Debug: wall outlines (the walls themselves are part of map_surface)
        if debug.show_hitboxes:
            for wall in self.edge_walls:
                if is_on_screen(camera, wall.rect):
                    draw_hitbox(surface, wall.image, wall.rect, camera, BLUE)

        # Padlocks on locked doors, in the color of the key they need
        for key, center in self.padlocks:
            image = self.padlock_images.get(key)
            if image is None:
                continue
            padlock_rect = image.get_rect(center=world_to_screen(camera, center))
            surface.blit(image, padlock_rect)

        # Crates, ground items and chests
        for group in [self.crates, self.ground_items, self.chests]:
            for sprite in group:
                if is_on_screen(camera, sprite.rect):
                    sprite.draw(surface, camera)

        # Outline what F would act on
        if highlight is not None:
            sprites, color = highlight
            if sprites:
                draw_highlight(surface, sprites, camera, color)

        # Actors, sorted by y so lower ones draw on top
        actors = sorted([player] + self.enemies, key=lambda actor: actor.rect.y)
        for actor in actors:
            if is_on_screen(camera, actor.rect):
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

    def player_walls(self, player):
        if is_rolling(player.roll):
            return self.solid_rects

        solid_enemies = [
            enemy.rect
            for enemy in self.enemies
            if enemy.is_solid() and not enemy.rect.colliderect(player.rect)
        ]
        return self.solid_rects + solid_enemies

    def enemies_left(self):
        return sum(1 for enemy in self.enemies if not enemy.dying)

    def remove_dead_enemies(self):
        for enemy in list(self.enemies):
            if enemy.is_done_dying():
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
            self.refresh_solid_rects()

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

        self.refresh_solid_rects()
        self.refresh_light_blockers()
        self.refresh_padlocks()

    def refresh_solid_rects(self):
        solid_crates = [crate for crate in self.crates if not crate.breaking]
        tiles = self.edge_walls + list(self.door_tiles) + solid_crates
        self.solid_rects = [tile.rect for tile in tiles]

    def refresh_light_blockers(self):
        tiles = list(self.wall_tiles) + list(self.door_tiles)
        self.light_blockers = light_blockers(
            self.map_surface.get_size(), tiles, TILE_SIZE
        )

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
            item = self.item_database[item_id]
            offset_x = random.randint(-LOOT_SCATTER_X, LOOT_SCATTER_X)
            offset_y = random.randint(-LOOT_SCATTER_Y, LOOT_SCATTER_Y)

            GroundItem(
                groups=self.ground_items,
                pos=(center[0] + offset_x, center[1] + offset_y),
                item=item,
                quantity=quantity,
            )
