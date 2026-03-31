from globals import *
import pygame, copy, random
from Components.animationComponent import AnimationComponent


class Item:

    _image_cache = {}

    def __init__(
        self,
        id: str,
        type: str = None,
        name: str = None,
        animations: dict = None,
        desc: str = None,
        quantity: int = 1,
        max_stack: int = 99,
        anim_speed: int = 4,
        value: str = None,
    ):
        self.id = id
        self.type = type
        self.name = name
        self.animations = animations
        self.desc = desc
        self.quantity = quantity
        self.max_stack = max_stack
        self.anim_speed = anim_speed
        self.value = value

        self.image = animations.get("idle", [None])[0]
        self.ui_icon = None

    def clone(self):
        return copy.deepcopy(self)

    @staticmethod
    def gen_item_textures(texture_data: dict, item_name: str) -> dict:
        textures = {}
        data = texture_data.get(item_name)
        if not data:
            return textures

        path = data["file_path"]
        if path not in Item._image_cache:
            Item._image_cache[path] = pygame.image.load(path).convert_alpha()

        sheet = Item._image_cache[path]
        w, h = data["size"]
        frames = data["frames"]
        row = data["position"][1]

        textures[item_name] = []
        for i in range(frames):
            rect = pygame.Rect(i * w, row * h, w, h)
            textures[item_name].append(sheet.subsurface(rect))

        return textures


class EquipmentItem(Item):
    def __init__(
        self,
        id: str,
        name: str = None,
        animations: dict = None,
        desc: str = None,
        slot: str = None,
        stats: dict = None,
        ability: str = None,
        value: str = None,
    ):
        super().__init__(
            id=id,
            type="equipment",
            name=name,
            animations=animations,
            desc=desc,
            quantity=1,
            max_stack=1,
            value=value,
        )

        self.slot = slot
        self.stats = stats
        self.ability = ability

        self.image = animations.get("idle", [None])[0]


class WorldItem(pygame.sprite.Sprite):
    def __init__(self, groups, pos, item_data):
        super().__init__(groups)
        self.item_data = item_data.clone()
        self.animations = AnimationComponent(
            node=self,
            animations=item_data.animations,
            start_anim="idle",
            anim_speed=item_data.anim_speed,
        )
        self.image = item_data.image
        self.pos = pos
        self.rect = self.image.get_rect(center=self.pos)

        # Specific Item Modifiers
        if self.item_data.type == "small_potion":
            self.item_data.quantity = random.randint(1, 3)

    def draw(self, screen, camera):
        screen.blit(self.image, (self.rect.x - camera.x, self.rect.y - camera.y))

    def update(self, dt):
        self.animations.update(dt)


class Chest(pygame.sprite.Sprite):
    def __init__(self, groups, pos, map):
        super().__init__(groups)
        self.image = CHEST_IMAGE
        self.rect = self.image.get_frect(topleft=pos)
        self.pos = pygame.math.Vector2(pos)
        self.map = map
        self.opened = False

    def draw(self, screen, camera):
        # Draws the tiles based on the camera offset
        screen.blit(self.image, (self.rect.x - camera.x, self.rect.y - camera.y))

    def update(self):
        pass

    def roll_loot(self):
        drops = []
        if random.random() < 0.8:
            drops.append("gold_key")
        if random.random() < 0.9:
            drops.append("small_health_potion")

        drops.append("speed_boots")

        return drops

    def open(self):
        if self.opened:
            return

        self.opened = True
        cx, cy = self.rect.center
        for item_id in self.roll_loot():
            item_data = self.map.ITEM_DATABASE.get(item_id)
            if item_data:
                offset_x = random.randint(-10, 10)
                offset_y = random.randint(-5, 5)
                WorldItem(
                    groups=self.map.items,
                    pos=(cx + offset_x, cy + offset_y),
                    item_data=item_data,
                )
