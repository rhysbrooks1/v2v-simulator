import pygame
import OpenGL.GL as gl
from sprite import SpriteRenderer

text_renderer = None  # global renderer

### MOVE TEXT BOX ###
DEFAULT_FONT_SIZE = 12
MOVE_HORIZONTALLY = 125
MOVE_VERTICALLY = 20


def init_text_renderer(window_width, window_height):
    global text_renderer
    text_renderer = SpriteRenderer(window_width, window_height)


def create_text_texture(text, font_size=14, color=(255, 255, 255)):
    font = pygame.font.SysFont("consolas", font_size)
    surf = font.render(text, True, color)

    tex = gl.glGenTextures(1)
    gl.glBindTexture(gl.GL_TEXTURE_2D, tex)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
    image = pygame.image.tostring(
        surf, "RGBA", True
    )  # True flips rows for OpenGL automatically
    gl.glTexImage2D(
        gl.GL_TEXTURE_2D,
        0,
        gl.GL_RGBA,
        surf.get_width(),
        surf.get_height(),
        0,
        gl.GL_RGBA,
        gl.GL_UNSIGNED_BYTE,
        image,
    )
    return tex, surf.get_width(), surf.get_height()


def draw_stats_panel(stats, window_width, window_height, col_count=2):
    global text_renderer
    if text_renderer is None:
        init_text_renderer(window_width, window_height)

    panel_width = 300
    panel_x = (
        -window_width / 2 + window_width - panel_width + MOVE_HORIZONTALLY
    )  # MOVE HORIZONTALLY
    y_top = window_height / 2 - MOVE_VERTICALLY  # MOVE VERTICALLY

    lines_static = [
        "=== STATISTICS ===",
        f"Vehicles: {stats['vehicles']}",
        f"BSM/sec: {stats['bsm_rate']}",
        f"CWM Count: {stats['cwm_count']}",
        f"Latency: {stats['latency']} ms",
        f"Packet Loss: {stats['packet_loss']}%",
        "",
        "=== VEHICLES ===",
    ]

    # Draw static lines first
    y_offset = 0
    for line in lines_static:
        tex, w, h = create_text_texture(line, font_size=12, color=(255, 255, 255))
        x_gl = panel_x
        y_gl = y_top - y_offset
        text_renderer.render(tex, w, h, translation=[x_gl, y_gl, 0], scale=[1.0, 1.0])
        gl.glDeleteTextures([tex])
        y_offset += h + 2

    # Now draw vehicles in columns
    vehicle_states = stats["vehicle_states"]
    col_width = panel_width / col_count
    row_height = 18 + 2  # font size + padding

    for idx, v in enumerate(vehicle_states):
        col = idx % col_count
        row = idx // col_count

        x_offset = panel_x + col * col_width - 75
        y_offset_vehicle = y_offset + row * 3 * row_height  # 3 lines per vehicle

        # Vehicle info
        lines = [
            f"ID {v['id']} | {v['speed']} m/s",
            f"Pos: ({int(v['x'])}, {int(v['y'])})",
        ]
        for i, line in enumerate(lines):
            tex, w, h = create_text_texture(line, font_size=12, color=(255, 255, 255))
            text_renderer.render(
                tex,
                w,
                h,
                translation=[x_offset, y_top - y_offset_vehicle - i * row_height, 0],
                scale=[1.0, 1.0],
            )
            gl.glDeleteTextures([tex])
