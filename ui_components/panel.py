import pygame

from globals import GAME_SCALE

# Corner size in art pixels. Must match the border in tools/make_panel_frame.py
PANEL_CORNER_SIZE = 4


def make_panel(frame_image, size):
    width = size[0] // GAME_SCALE
    height = size[1] // GAME_SCALE

    corner = PANEL_CORNER_SIZE

    frame_width, frame_height = frame_image.get_size()
    frame_middle_width = frame_width - 2 * corner
    frame_middle_height = frame_height - 2 * corner

    panel_middle_width = width - 2 * corner
    panel_middle_height = height - 2 * corner

    pieces = [
        # Top-left corner
        (
            pygame.Rect(0, 0, corner, corner),
            pygame.Rect(0, 0, corner, corner),
        ),
        # Top edge
        (
            pygame.Rect(corner, 0, frame_middle_width, corner),
            pygame.Rect(corner, 0, panel_middle_width, corner),
        ),
        # Top-right corner
        (
            pygame.Rect(frame_width - corner, 0, corner, corner),
            pygame.Rect(width - corner, 0, corner, corner),
        ),
        # Left edge
        (
            pygame.Rect(0, corner, corner, frame_middle_height),
            pygame.Rect(0, corner, corner, panel_middle_height),
        ),
        # Center
        (
            pygame.Rect(corner, corner, frame_middle_width, frame_middle_height),
            pygame.Rect(corner, corner, panel_middle_width, panel_middle_height),
        ),
        # Right edge
        (
            pygame.Rect(frame_width - corner, corner, corner, frame_middle_height),
            pygame.Rect(width - corner, corner, corner, panel_middle_height),
        ),
        # Bottom-left corner
        (
            pygame.Rect(0, frame_height - corner, corner, corner),
            pygame.Rect(0, height - corner, corner, corner),
        ),
        # Bottom edge
        (
            pygame.Rect(corner, frame_height - corner, frame_middle_width, corner),
            pygame.Rect(corner, height - corner, panel_middle_width, corner),
        ),
        # Bottom-right corner
        (
            pygame.Rect(frame_width - corner, frame_height - corner, corner, corner),
            pygame.Rect(width - corner, height - corner, corner, corner),
        ),
    ]

    panel = pygame.Surface((width, height), pygame.SRCALPHA)

    for source_rect, target_rect in pieces:
        piece = frame_image.subsurface(source_rect)
        stretched_piece = pygame.transform.scale(piece, target_rect.size)
        panel.blit(stretched_piece, target_rect.topleft)

    return pygame.transform.scale_by(panel, GAME_SCALE)
