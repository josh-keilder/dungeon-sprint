"""
Data: Item Initialization
-------------------------
Constructs the global ITEM_DATABASE by instantiating Item and EquipmentItem
objects. This module links raw texture data (spritesheets) to logical
game objects, defining their properties, animations, and statistics.

Functions:
    initialize_item_database: The primary factory function for game loot.
"""

from items.itemTextureData import *
from items.items import Item, EquipmentItem
from systems.assets import load_animations


def initialize_item_database():
    """
    Instantiates all items in the game and returns them in a searchable dictionary.
    Each item is initialized with its sliced texture frames and gameplay metadata.
    """
    ITEM_DATABASE = {}

    # --- Texture Generation ---
    # Slices spritesheets into frame lists using the Item static method
    gold_key_frames = load_animations(keys)
    small_health_potion_frames = load_animations(health_potions)
    speed_boots_frames = load_animations(speed_boots)

    # --- Item Registration ---

    # Key Items
    ITEM_DATABASE["gold_key"] = Item(
        id="gold_key",
        type="key",
        name="Gold Key",
        animations={"idle": gold_key_frames["gold_key"]},
        desc="Unlocks Doors",
    )

    # Consumables
    ITEM_DATABASE["small_health_potion"] = Item(
        id="small_health_potion",
        name="Small Health Potion",
        type="small_potion",
        animations={"idle": small_health_potion_frames["health_potion"]},
        desc="Heals Player",
        value=f"Value: {SMALL_HEALTH_POTION_VALUE} HP",
    )

    # Equipment
    ITEM_DATABASE["speed_boots"] = EquipmentItem(
        id="speed_boots",
        name="Speed boots",
        animations={"idle": speed_boots_frames["speed_boots"]},
        desc="Run faster",
        slot="boots",
        bonuses={"max_speed": 10, "acceleration": 20, "defense": 3, "health": 10},
        ability=None,
    )

    return ITEM_DATABASE
