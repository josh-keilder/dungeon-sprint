import pygame

_IMAGE_CACHE = {}

_ANIMATION_CACHE = {}


def load_image(path):
    if path not in _IMAGE_CACHE:
        sheet = pygame.image.load(path).convert_alpha()
        _IMAGE_CACHE[path] = sheet

    return _IMAGE_CACHE[path]


def slice_frames(sheet, entry):
    width, height = entry["size"]
    row = entry["position"][1]

    frames = []

    for i in range(entry["frames"]):

        frame = sheet.subsurface(pygame.Rect(i * width, row * height, width, height))
        frames.append(frame)

    return frames


def crop_center(frames, crop_size):
    cropped_frames = []

    for frame in frames:
        x = (frame.get_width() - crop_size) // 2
        y = (frame.get_height() - crop_size) // 2

        cropped_frame = frame.subsurface(pygame.Rect(x, y, crop_size, crop_size)).copy()

        cropped_frames.append(cropped_frame)

    return cropped_frames


def add_flipped_left(animations):

    for name, frames in list(animations.items()):
        if not name.endswith("_right"):
            continue
        left_name = name.replace("_right", "_left")

        if left_name in animations:
            continue

        flipped = []
        for frame in frames:
            flipped.append(pygame.transform.flip(frame, True, False))

        animations[left_name] = flipped


def load_animations(texture_data, crop_size=None):
    cache_key = (tuple(texture_data.keys()), crop_size)

    if cache_key not in _ANIMATION_CACHE:
        animations = {}

        for name, entry in texture_data.items():
            sheet = load_image(entry["file_path"])
            frames = slice_frames(sheet, entry)

            if crop_size is not None:
                frames = crop_center(frames, crop_size)

            animations[name] = frames

        add_flipped_left(animations)

        _ANIMATION_CACHE[cache_key] = animations

    return _ANIMATION_CACHE[cache_key]
