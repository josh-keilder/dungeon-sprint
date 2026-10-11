CONTACT_CHECK_RANGE = 100


def find_player_contacts(player, enemies):
    contacts = []

    for enemy in enemies:
        if player.pos.distance_to(enemy.pos) < CONTACT_CHECK_RANGE:
            if player.hitbox.collides_with(enemy.hitbox):
                contacts.append(enemy)

    return contacts
