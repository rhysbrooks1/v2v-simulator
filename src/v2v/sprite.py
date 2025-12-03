import OpenGL.GL as gl
from OpenGL.GL import shaders
from pyglm import glm

from PIL import Image
import numpy as np
import ctypes

import os

ASSETS_DIR = os.path.join(os.getcwd(), "assets")


# Loads sprite from the 'assets' directory.
#
# Returns (sprite, width, height)
def load_sprite(path):
    texture = gl.glGenTextures(1)
    gl.glBindTexture(gl.GL_TEXTURE_2D, texture)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_REPEAT)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_REPEAT)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)

    image = Image.open(os.path.join(ASSETS_DIR, "cars/manual.png"))
    image = image.convert("RGBA")
    image = image.transpose(Image.FLIP_TOP_BOTTOM)
    width, height = image.size
    data = np.array(image, dtype=np.uint8)
    gl.glTexImage2D(
        gl.GL_TEXTURE_2D,
        0,
        gl.GL_RGBA,
        width,
        height,
        0,
        gl.GL_RGBA,
        gl.GL_UNSIGNED_BYTE,
        data,
    )
    return (
        texture,
        width,
        height,
    )


VERT_SHADER = """
#version 330 core
layout (location = 0) in vec3 aPos;
layout (location = 1) in vec2 aTexCoord;
out vec2 TexCoord;
uniform mat4 proj_matrix;
uniform mat4 model_matrix;
void main()
{
	gl_Position = proj_matrix * model_matrix * vec4(aPos, 1.0);
	TexCoord = vec2(aTexCoord.x, aTexCoord.y);
}
"""
FRAG_SHADER = """
#version 330 core
out vec4 FragColor;
in vec2 TexCoord;
uniform sampler2D texture1;
void main()
{
	FragColor = texture(texture1, TexCoord);
}
"""


class SpriteRenderer:
    def __init__(self, window_width, window_height):
        # The OpenGL code here is adapted from these learnopengl resources:
        # - https://learnopengl.com/code_viewer_gh.php?code=src/1.getting_started/4.1.textures/textures.cpp
        # - https://learnopengl.com/code_viewer_gh.php?code=src/1.getting_started/5.1.transformations/transformations.cpp

        # fmt: off
        vertices = np.array([
             # positions       # texture coords
             0.5,  0.5, 0.0,   1.0, 1.0, # top right
             0.5, -0.5, 0.0,   1.0, 0.0, # bottom right
            -0.5, -0.5, 0.0,   0.0, 0.0, # bottom let
            -0.5,  0.5, 0.0,   0.0, 1.0  # top let 
        ], dtype=np.float32)
        indices = np.array([
             0, 1, 3, # first triangle
             1, 2, 3, # second triangle
        ], dtype=np.uint32)
        # fmt: on

        vert = shaders.compileShader(VERT_SHADER, gl.GL_VERTEX_SHADER)
        frag = shaders.compileShader(FRAG_SHADER, gl.GL_FRAGMENT_SHADER)
        self.sprite_shader = shaders.compileProgram(vert, frag)
        # sprite_shader needs to blend alpha
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

        self.vao = gl.glGenVertexArrays(1)
        vbo = gl.glGenBuffers(1)
        ebo = gl.glGenBuffers(1)

        # configure buffers
        gl.glBindVertexArray(self.vao)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo)
        gl.glBufferData(
            gl.GL_ARRAY_BUFFER, vertices.nbytes, vertices, gl.GL_STATIC_DRAW
        )
        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, ebo)
        gl.glBufferData(
            gl.GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, gl.GL_STATIC_DRAW
        )

        # position attributes
        gl.glVertexAttribPointer(
            0, 3, gl.GL_FLOAT, gl.GL_FALSE, 5 * 4, ctypes.c_void_p(0)
        )
        gl.glEnableVertexAttribArray(0)
        # uv attributes
        gl.glVertexAttribPointer(
            1, 2, gl.GL_FLOAT, gl.GL_FALSE, 5 * 4, ctypes.c_void_p(3 * 4)
        )
        gl.glEnableVertexAttribArray(1)

        # unbind buffers, prevent any external edits
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)
        gl.glBindVertexArray(0)

        self.window_width = float(window_width)
        self.window_height = float(window_height)
        self.proj_matrix = glm.ortho(
            -self.window_width / 2.0,
            self.window_width / 2.0,
            -self.window_height / 2.0,
            self.window_height / 2.0,
            -1.0,
            1.0,
        )

    def render(
        self,
        sprite,
        sprite_width,
        sprite_height,
        translation=[0.0, 0.0],
        rotation=0.0,
        scale=[1.0, 1.0],
    ):
        gl.glBindTexture(gl.GL_TEXTURE_2D, sprite)
        gl.glUseProgram(self.sprite_shader)

        # These transforms are applied in reverse order
        model_matrix = glm.mat4(1.0)
        model_matrix = glm.translate(
            model_matrix,
            glm.vec3(
                translation[0],
                translation[1],
                1.0,
            ),
        )
        model_matrix = glm.rotate(model_matrix, -rotation, glm.vec3(0.0, 0.0, 1.0))
        model_matrix = glm.scale(
            model_matrix,
            glm.vec3(
                float(sprite_width) * scale[0],
                float(sprite_height) * scale[1],
                1.0,
            ),
        )

        transform_loc = gl.glGetUniformLocation(self.sprite_shader, "proj_matrix")
        gl.glUniformMatrix4fv(
            transform_loc, 1, gl.GL_FALSE, glm.value_ptr(self.proj_matrix)
        )

        transform_loc = gl.glGetUniformLocation(self.sprite_shader, "model_matrix")
        gl.glUniformMatrix4fv(
            transform_loc, 1, gl.GL_FALSE, glm.value_ptr(model_matrix)
        )

        gl.glBindVertexArray(self.vao)
        gl.glDrawElements(gl.GL_TRIANGLES, 6, gl.GL_UNSIGNED_INT, ctypes.c_void_p(0))
