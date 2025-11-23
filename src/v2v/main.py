import pygame as pg
import OpenGL.GL as gl
from sprite import SpriteRenderer, load_sprite


def main():
    pg.init()
    dt = 0.0
    rot = 0.0
    clock = pg.time.Clock()
    running = True

    window_width = 1280
    window_height = 720
    sprite_renderer = SpriteRenderer(window_width, window_height)
    sprite, width, height = load_sprite("cars/manual.png")

    while running:
        # input
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

        # update
        keys = pg.key.get_pressed()
        if keys[pg.K_ESCAPE]:
            running = False

        # render
        gl.glClearColor(0.1, 0.1, 0.1, 1.0)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        sprite_renderer.render(sprite, width, height, scale=[2.0, 2.0], rotation=rot)
        rot += dt
        pg.display.flip()

        dt = float(clock.tick(60)) / 1_000.0
    pg.quit()


if __name__ == "__main__":
    main()
