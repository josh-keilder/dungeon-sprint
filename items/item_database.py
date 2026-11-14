from items.item_texture_data import (
    gold_key_texture_data,
    health_potion_texture_data,
    silver_key_texture_data,
    speed_boots_texture_data,
)
from items.items import EquipmentItem, Item
from systems.assets import load_animations

# Item Values
SMALL_HEALTH_POTION_VALUE = 10


def initialize_item_database():
    item_database = {}

    # Animation frames for each item
    gold_key_frames = load_animations(gold_key_texture_data)
    silver_key_frames = load_animations(silver_key_texture_data)
    small_health_potion_frames = load_animations(health_potion_texture_data)
    speed_boots_frames = load_animations(speed_boots_texture_data)

    # Key Items
    item_database["gold_key"] = Item(
        item_id="gold_key",
        name="Gold Key",
        animations={"idle": gold_key_frames["gold_key"]},
        description="Opens treasure rooms",
    )
    item_database["silver_key"] = Item(
        item_id="silver_key",
        name="Silver Key",
        animations={"idle": silver_key_frames["silver_key"]},
        description="Opens the way forward",
    )

    # Consumables
    item_database["small_health_potion"] = Item(
        item_id="small_health_potion",
        name="Small Health Potion",
        animations={"idle": small_health_potion_frames["health_potion"]},
        description="Heals Player",
        value_text=f"Value: {SMALL_HEALTH_POTION_VALUE} HP",
    )

    # Equipment
    item_database["speed_boots"] = EquipmentItem(
        item_id="speed_boots",
        name="Speed boots",
        animations={"idle": speed_boots_frames["speed_boots"]},
        description="Run faster",
        slot="boots",
        bonuses={"max_speed": 10, "acceleration_rate": 7, "defense": 3, "health": 10},
    )

    return item_database
