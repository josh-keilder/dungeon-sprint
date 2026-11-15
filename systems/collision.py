from systems.masks import images_overlap

# Broad phase: only enemies this close get the pixel-perfect mask check
CONTACT_CHECK_RANGE = 100  # pixels


def find_player_contacts(player, enemies):
    contacts = []

    for enemy in enemies:
        if player.pos.distance_to(enemy.pos) < CONTACT_CHECK_RANGE:
            if images_overlap(
                player.image, player.rect.topleft, enemy.image, enemy.art_topleft()
            ):
                contacts.append(enemy)

    return contacts
