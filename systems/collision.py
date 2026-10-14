from systems.hitbox import sprites_overlap

CONTACT_CHECK_RANGE = 100


def find_player_contacts(player, enemies):
    contacts = []

    for enemy in enemies:
        if player.pos.distance_to(enemy.pos) < CONTACT_CHECK_RANGE:
            if sprites_overlap(player, enemy):
                contacts.append(enemy)

    return contacts
