from globals import SMALL_HEALTH_POTION_VALUE
from items.itemTextureData import health_potions, keys, speed_boots
from items.items import EquipmentItem, Item
from systems.assets import load_animations


def initialize_item_database():
    ITEM_DATABASE = {}

    # Animation frames for each item
    gold_key_frames = load_animations(keys)
    small_health_potion_frames = load_animations(health_potions)
    speed_boots_frames = load_animations(speed_boots)


    # Key Items
    ITEM_DATABASE["gold_key"] = Item(
        id="gold_key",
        name="Gold Key",
        animations={"idle": gold_key_frames["gold_key"]},
        desc="Unlocks Doors",
    )

    # Consumables
    ITEM_DATABASE["small_health_potion"] = Item(
        id="small_health_potion",
        name="Small Health Potion",
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
    )

    return ITEM_DATABASE
