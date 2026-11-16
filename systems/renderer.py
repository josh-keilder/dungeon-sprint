from array import array

import moderngl
import pygame

from constants import GAME_SCALE, SCREEN_HEIGHT, SCREEN_WIDTH, WORLD_HEIGHT, WORLD_WIDTH
from systems.display import letterbox
from systems.lighting import AMBIENT_LIGHT, LIGHT_BANDS, MAX_LIGHT, MAX_LIGHTS

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

# The world, lit: ambient light plus each light's falloff, in bands or smooth
WORLD_SHADER = "#version 330\n" f"#define MAX_LIGHTS {MAX_LIGHTS}\n" + """
uniform sampler2D image;
uniform vec2 world_size;
uniform vec3 ambient;
uniform float max_light;
uniform int bands;
uniform int light_count;
uniform vec2 light_positions[MAX_LIGHTS];
uniform float light_radii[MAX_LIGHTS];
uniform vec3 light_colors[MAX_LIGHTS];
in vec2 uv;
out vec4 color;

void main() {
    vec2 pixel = floor(uv * world_size) + 0.5;
    vec3 light = ambient;

    for (int i = 0; i < light_count; i++) {
        float distance_ratio = distance(pixel, light_positions[i]) / light_radii[i];
        float falloff = clamp(1.0 - distance_ratio, 0.0, 1.0);
        if (bands > 0) {
            falloff = floor(falloff * bands) / bands;
        }
        light += light_colors[i] * falloff;
    }

    vec4 art = texture(image, uv);
    color = vec4(art.rgb * min(light, vec3(max_light)), art.a);
}
"""

# The world is WORLD_WIDTH x GAME_SCALE = 1281 px wide on a 1280 px screen: show only the
# part that fits, so one world pixel stays exactly GAME_SCALE screen pixels
WORLD_UV_RIGHT = SCREEN_WIDTH / (WORLD_WIDTH * GAME_SCALE)
WORLD_UV_BOTTOM = SCREEN_HEIGHT / (WORLD_HEIGHT * GAME_SCALE)

# What a run handed over this frame: (world surface, lights), or None (menus)
_world = None


def submit_world(world_surface, lights):
    global _world
    _world = (world_surface, lights)


class Renderer:
    def __init__(self):
        self.ctx = moderngl.create_context()
        self.ctx.enable(moderngl.BLEND)
        self.ctx.blend_func = moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA

        self.ui_program = self.ctx.program(
            vertex_shader=VERTEX_SHADER, fragment_shader=TEXTURE_SHADER
        )
        self.world_program = self.ctx.program(
            vertex_shader=VERTEX_SHADER, fragment_shader=WORLD_SHADER
        )
        self.world_quad = self.make_quad(
            self.world_program, WORLD_UV_RIGHT, WORLD_UV_BOTTOM
        )
        self.ui_quad = self.make_quad(self.ui_program, 1.0, 1.0)

        # Light settings that never change while the game runs
        self.world_program["world_size"].value = (WORLD_WIDTH, WORLD_HEIGHT)
        self.world_program["ambient"].value = AMBIENT_LIGHT
        self.world_program["max_light"].value = MAX_LIGHT
        self.world_program["bands"].value = LIGHT_BANDS

        self.world_texture = self.make_texture((WORLD_WIDTH, WORLD_HEIGHT))
        self.ui_texture = self.make_texture((SCREEN_WIDTH, SCREEN_HEIGHT))
        # The UI surface's memory is B, G, R, A per pixel (see its masks): upload it
        # untouched and let the texture read the channels in that order
        self.ui_texture.swizzle = "BGRA"

    def present(self, ui_surface):
        global _world

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

        if _world is not None:
            world_surface, lights = _world
            self.set_lights(lights)
            self.world_texture.write(pygame.image.tobytes(world_surface, "RGBA"))
            self.draw_layer(self.world_texture, self.world_quad)
            _world = None

        self.ui_texture.write(ui_surface.get_view("1"))
        self.draw_layer(self.ui_texture, self.ui_quad)

    def draw_layer(self, texture, quad):
        texture.use(0)
        quad.render(moderngl.TRIANGLE_STRIP)

    def set_lights(self, lights):
        padding = MAX_LIGHTS - len(lights)
        positions = [position for position, _, _ in lights] + [(0.0, 0.0)] * padding
        radii = [radius for _, radius, _ in lights] + [1.0] * padding
        colors = [color for _, _, color in lights] + [(0.0, 0.0, 0.0)] * padding

        self.world_program["light_count"].value = len(lights)
        self.world_program["light_positions"].value = positions
        self.world_program["light_radii"].value = radii
        self.world_program["light_colors"].value = colors

    def make_quad(self, program, uv_right, uv_bottom):
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
            program, [(buffer, "2f 2f", "in_position", "in_uv")]
        )

    def make_texture(self, size):
        texture = self.ctx.texture(size, 4)
        texture.filter = (moderngl.NEAREST, moderngl.NEAREST)
        return texture
