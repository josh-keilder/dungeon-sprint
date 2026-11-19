import copy


# Item data: templates in the item database, and stacks in the inventory
class Item:
    def __init__(
        self,
        item_id,
        name=None,
        animations=None,
        description=None,
        quantity=1,
        max_stack=99,
        animation_speed=4,
        value_text=None,
    ):
        # What it is, how it's described, and how many fit in one slot
        self.id = item_id
        self.name = name
        self.animations = animations
        self.description = description
        self.quantity = quantity
        self.max_stack = max_stack
        self.animation_speed = animation_speed
        self.value_text = value_text

        # Icon: the first idle frame
        self.image = animations.get("idle", [None])[0]

    def clone(self):
        return copy.copy(self)


class EquipmentItem(Item):
    def __init__(
        self,
        item_id,
        name=None,
        animations=None,
        description=None,
        slot=None,
        bonuses=None,
        value_text=None,
    ):
        super().__init__(
            item_id=item_id,
            name=name,
            animations=animations,
            description=description,
            quantity=1,
            max_stack=1,
            value_text=value_text,
        )
        self.slot = slot
        self.bonuses = bonuses
