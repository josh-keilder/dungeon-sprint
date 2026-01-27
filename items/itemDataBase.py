from items.itemTextureData import *
from items.items import Item
import random


def initialize_item_database():
    ITEM_DATABASE = {}

    # Load Textures
    gold_key_frames = Item.gen_item_textures(keys, 'gold_key')
    small_health_potion_frames = Item.gen_item_textures(health_potions, 'health_potion')

    # Add items to database
    ITEM_DATABASE['gold_key'] = Item(id='gold_key',
                                    type='key',
                                    name='Gold Key',
                                    animations={'idle': gold_key_frames['gold_key']},
                                    desc='Unlocks Doors')
    ITEM_DATABASE['small_health_potion'] = Item(id='small_health_potion',
                                        name='Small Health Potion',
                                        type='small_potion',
                                        animations={'idle': small_health_potion_frames['health_potion']},
                                        desc='Heals Player',
                                        value='Value: ' + str(SMALL_HEALTH_POTION_VALUE) + ' HP'
                                        )
    
    return ITEM_DATABASE