from array import array

import moderngl
import pygame

from constants import GAME_SCALE, SCREEN_HEIGHT, SCREEN_WIDTH, WORLD_HEIGHT, WORLD_WIDTH
from systems.display import letterbox

# Shaders: put a texture on a rectangle (the quad)
VERTEX_SHADER = """
#version 330
in vec2 in_position;
in vec2 in_uv;
out vec2 uv;

void main() {
    uv = in_uv;
    gl_Position = vec4(in_position, 0.0, 1.0);
}
"""

TEXTURE_SHADER = """
#version 330
uniform sampler2D image;
in vec2 uv;
out vec4 color;

void main() {
    color = texture(image, uv);
}
"""

# The world is WORLD_WIDTH x GAME_SCALE = 1281 px wide on a 1280 px screen: show only the
# part that fits, so one world pixel stays exactly GAME_SCALE screen pixels
WORLD_UV_RIGHT = SCREEN_WIDTH / (WORLD_WIDTH * GAME_SCALE)
WORLD_UV_BOTTOM = SCREEN_HEIGHT / (WORLD_HEIGHT * GAME_SCALE)

# The world surface handed over this frame; None when nothing submitted one (menus)
_world_surface = None


def submit_world(world_surface):
    global _world_surface
    _world_surface = world_surface


class Renderer:
    def __init__(self):
        self.ctx = moderngl.create_context()
        self.ctx.enable(moderngl.BLEND)
        self.ctx.blend_func = moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA

        self.program = self.ctx.program(
            vertex_shader=VERTEX_SHADER, fragment_shader=TEXTURE_SHADER
        )
        self.world_quad = self.make_quad(WORLD_UV_RIGHT, WORLD_UV_BOTTOM)
        self.ui_quad = self.make_quad(1.0, 1.0)

        self.world_texture = self.make_texture((WORLD_WIDTH, WORLD_HEIGHT))
        self.ui_texture = self.make_texture((SCREEN_WIDTH, SCREEN_HEIGHT))
        # The UI surface's memory is B, G, R, A per pixel (see its masks): upload it
        # untouched and let the texture read the channels in that order
        self.ui_texture.swizzle = "BGRA"

    def present(self, ui_surface):
        global _world_surface

        window_size = pygame.display.get_window_size()
        self.ctx.viewport = (0, 0, *window_size)
        self.ctx.clear(0.0, 0.0, 0.0)

        left, top, scale = letterbox(window_size)
        self.ctx.viewport = (
            round(left),
            round(top),  # the bars are equal, so top works from the bottom too
            round(SCREEN_WIDTH * scale),
            round(SCREEN_HEIGHT * scale),
        )

        if _world_surface is not None:
            self.world_texture.write(pygame.image.tobytes(_world_surface, "RGBA"))
            self.draw_layer(self.world_texture, self.world_quad)
            _world_surface = None

        self.ui_texture.write(ui_surface.get_view("1"))
        self.draw_layer(self.ui_texture, self.ui_quad)

    def draw_layer(self, texture, quad):
        texture.use(0)
        quad.render(moderngl.TRIANGLE_STRIP)

    def make_quad(self, uv_right, uv_bottom):
        # Each corner: x, y on screen (-1 to 1, up is +), the u, v in the texture
        # (0 to 1, from the top-left, like pygame)
        vertices = array("f", [
            -1.0, 1.0, 0.0, 0.0,  # top left
            1.0, 1.0, uv_right, 0.0,  # top right
            -1.0, -1.0, 0.0, uv_bottom,  # bottom left
            1.0, -1.0, uv_right, uv_bottom,  # bottom right
        ])  # fmt: skip
        buffer = self.ctx.buffer(vertices)
        return self.ctx.vertex_array(
            self.program, [(buffer, "2f 2f", "in_position", "in_uv")]
        )

    def make_texture(self, size):
        texture = self.ctx.texture(size, 4)
        texture.filter = (moderngl.NEAREST, moderngl.NEAREST)
        return texture
