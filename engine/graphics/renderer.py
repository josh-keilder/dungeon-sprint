from array import array

import moderngl
import pygame

from engine.graphics.display import letterbox
from engine.graphics.lighting import MAX_LIGHTS

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

# The world, lit: ambient light plus each light's falloff, stopped by walls and doors
WORLD_SHADER = "#version 330\n" f"#define MAX_LIGHTS {MAX_LIGHTS}\n" + """
uniform sampler2D image;
uniform usampler2D blockers;
uniform vec2 world_size;
uniform vec2 camera_offset;
uniform float tile_size;
uniform vec3 ambient;
uniform vec3 void_color;
uniform float max_light;
uniform int bands;
uniform int light_count;
uniform vec2 light_positions[MAX_LIGHTS];
uniform float light_radii[MAX_LIGHTS];
uniform vec3 light_colors[MAX_LIGHTS];
in vec2 uv;
out vec4 color;

const float SHADOW_STEP = 4.0;
const ivec2 FRONT_DIRECTIONS[4] = ivec2[4](ivec2(0, 1), ivec2(1, 0), ivec2(-1, 0), ivec2(0, -1));

ivec2 cell_at(vec2 world_position) {
    return ivec2(floor(world_position / tile_size));
}

// Walls, closed doors and everything off the map block light
bool is_blocker(ivec2 cell) {
    ivec2 map_size = textureSize(blockers, 0);
    if (any(lessThan(cell, ivec2(0))) || any(greaterThanEqual(cell, map_size))) {
        return true;
    }
    return texelFetch(blockers, cell, 0).r > 0u;
}

// Where light enters or leaves a tile: the point itself in the open, or the
// center of the open tile in front of a wall (below, right, left, then above)
bool open_point(vec2 world_position, out vec2 point) {
    ivec2 cell = cell_at(world_position);
    point = world_position;
    if (!is_blocker(cell)) {
        return true;
    }
    for (int i = 0; i < 4; i++) {
        ivec2 front = cell + FRONT_DIRECTIONS[i];
        if (!is_blocker(front)) {
            point = (vec2(front) + 0.5) * tile_size;
            return true;
        }
    }
    return false;
}

// True when no wall or closed door stands between the two points
bool reaches(vec2 from, vec2 to) {
    vec2 start, target;
    if (!open_point(from, start) || !open_point(to, target)) {
        return false;
    }
    float steps = ceil(distance(start, target) / SHADOW_STEP);
    for (float step = 1.0; step < steps; step++) {
        if (is_blocker(cell_at(mix(start, target, step / steps)))) {
            return false;
        }
    }
    return true;
}

void main() {
    vec2 pixel = floor(uv * world_size) + 0.5;
    vec3 light = ambient;
    vec4 art = texture(image, uv);

    // The empty part of a wall tile (only void color) never takes light
    bool empty_wall = is_blocker(cell_at(pixel + camera_offset))
        && all(lessThan(abs(art.rgb - void_color), vec3(0.5 / 255.0)));

    for (int i = 0; i < light_count && !empty_wall; i++) {
        float distance_ratio = distance(pixel, light_positions[i]) / light_radii[i];
        float falloff = clamp(1.0 - distance_ratio, 0.0, 1.0);
        if (falloff <= 0.0) {
            continue;
        }
        if (!reaches(light_positions[i] + camera_offset, pixel + camera_offset)) {
            continue;
        }
        if (bands > 0) {
            falloff = floor(falloff * bands) / bands;
        }
        light += light_colors[i] * falloff;
    }

    color = vec4(art.rgb * min(light, vec3(max_light)), art.a);
}
"""


# What a run handed over this frame: (world surface, camera offset, lights,
# light blockers), or None (menus)
_world = None


def submit_world(world_surface, camera_offset, lights, blockers):
    global _world
    _world = (world_surface, camera_offset, lights, blockers)


class Renderer:
    def __init__(self, screen_size, world_size, world_scale, tile_size, lighting):
        # lighting: {"ambient", "max_light", "bands", "void_color" (0-255 RGB)}
        self.screen_size = screen_size

        self.ctx = moderngl.create_context()
        self.ctx.enable(moderngl.BLEND)
        self.ctx.blend_func = moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA

        self.ui_program = self.ctx.program(
            vertex_shader=VERTEX_SHADER, fragment_shader=TEXTURE_SHADER
        )
        self.world_program = self.ctx.program(
            vertex_shader=VERTEX_SHADER, fragment_shader=WORLD_SHADER
        )

        # The world is world width x world_scale px wide (1281 on a 1280 px screen):
        # show only the part that fits, so one world pixel stays world_scale pixels
        uv_right = screen_size[0] / (world_size[0] * world_scale)
        uv_bottom = screen_size[1] / (world_size[1] * world_scale)
        self.world_quad = self.make_quad(self.world_program, uv_right, uv_bottom)
        self.ui_quad = self.make_quad(self.ui_program, 1.0, 1.0)

        # Light settings that never change while the game runs
        self.world_program["image"].value = 0  # texture slot 0: the world
        self.world_program["blockers"].value = 1  # texture slot 1: the blocker mask
        self.world_program["tile_size"].value = tile_size
        self.world_program["world_size"].value = world_size
        self.world_program["ambient"].value = lighting["ambient"]
        self.world_program["max_light"].value = lighting["max_light"]
        self.world_program["void_color"].value = tuple(
            channel / 255 for channel in lighting["void_color"]
        )
        self.world_program["bands"].value = lighting["bands"]

        self.world_texture = self.make_texture(world_size)
        self.ui_texture = self.make_texture(screen_size)
        # The UI surface's memory is B, G, R, A per pixel (see its masks): upload it
        # untouched and let the texture read the channels in that order
        self.ui_texture.swizzle = "BGRA"

        # The current floor's light blockers, rebuilt when they change
        self.blockers = None
        self.blocker_texture = None

    def present(self, ui_surface):
        global _world

        window_size = pygame.display.get_window_size()
        self.ctx.viewport = (0, 0, *window_size)
        self.ctx.clear(0.0, 0.0, 0.0)

        left, top, scale = letterbox(window_size)
        self.ctx.viewport = (
            round(left),
            round(top),  # the bars are equal, so top works from the bottom too
            round(self.screen_size[0] * scale),
            round(self.screen_size[1] * scale),
        )

        if _world is not None:
            world_surface, camera_offset, lights, blockers = _world
            self.world_program["camera_offset"].value = camera_offset
            self.set_blockers(blockers)
            self.set_lights(lights)
            self.world_texture.write(pygame.image.tobytes(world_surface, "RGBA"))
            self.draw_layer(self.world_texture, self.world_quad)
            _world = None

        self.ui_texture.write(ui_surface.get_view("1"))
        self.draw_layer(self.ui_texture, self.ui_quad)

    def draw_layer(self, texture, quad):
        texture.use(0)
        quad.render(moderngl.TRIANGLE_STRIP)

    def set_blockers(self, blockers):
        # A new mask only comes with a new floor or an opened door
        if blockers is not self.blockers:
            self.blockers = blockers
            size, mask = blockers
            if self.blocker_texture is not None:
                self.blocker_texture.release()
            self.blocker_texture = self.ctx.texture(size, 1, mask, dtype="u1")
            self.blocker_texture.filter = (moderngl.NEAREST, moderngl.NEAREST)

        self.blocker_texture.use(1)

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
