import OpenGL.GL as gl
from OpenGL.GL import shaders
from pyglm import glm
import numpy as np
import math
import ctypes


VERT_SHADER = """
#version 330 core
layout (location = 0) in vec3 aPos;
uniform mat4 proj_matrix, model_matrix;
void main()
{
    gl_Position = proj_matrix * model_matrix * vec4(aPos, 1.0);
}
"""
FRAG_SHADER = """
#version 330 core
out vec4 FragColor;
uniform vec4 color;
void main()
{
    FragColor = color;
}
"""


class LineRenderer:
    def __init__(self, window_width, window_height):
        # Makes the ends look nice
        gl.glEnable(gl.GL_LINE_SMOOTH)

        self.vao = gl.glGenVertexArrays(1)
        self.vbo = gl.glGenBuffers(1)

        gl.glBindVertexArray(self.vao)

        vert = shaders.compileShader(VERT_SHADER, gl.GL_VERTEX_SHADER)
        frag = shaders.compileShader(FRAG_SHADER, gl.GL_FRAGMENT_SHADER)
        self.sprite_shader = shaders.compileProgram(vert, frag)

        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo)
        gl.glVertexAttribPointer(
            0, 3, gl.GL_FLOAT, gl.GL_FALSE, 3 * 4, ctypes.c_void_p(0)
        )
        gl.glEnableVertexAttribArray(0)

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
        gl.glUseProgram(self.sprite_shader)
        gl.glUniformMatrix4fv(
            gl.glGetUniformLocation(self.sprite_shader, "proj_matrix"),
            1,
            gl.GL_FALSE,
            glm.value_ptr(self.proj_matrix),
        )
        gl.glUseProgram(0)

    def render_lines(
        self,
        points,
        color=[1.0, 1.0, 1.0, 1.0],
    ):
        if len(points) == 0:
            return

        gl.glUseProgram(self.sprite_shader)

        gl.glBindVertexArray(self.vao)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, points.nbytes, points, gl.GL_DYNAMIC_DRAW)

        # identity matrix since points are in world space
        identity = glm.identity(glm.mat4x4)
        gl.glUniformMatrix4fv(
            gl.glGetUniformLocation(self.sprite_shader, "model_matrix"),
            1,
            gl.GL_FALSE,
            glm.value_ptr(identity),
        )

        gl.glUniform4f(
            gl.glGetUniformLocation(self.sprite_shader, "color"),
            color[0],
            color[1],
            color[2],
            color[3],
        )

        # macos doesn't support line width, so unfortunately the lines must be skinny
        # gl.glLineWidth(3)
        gl.glDrawArrays(gl.GL_LINES, 0, len(points) // 3)

    def render_arrows(
        self,
        points,
        color=[1.0, 1.0, 1.0, 1.0],
    ):
        if len(points) == 0:
            return

        # render lines like normal then attach triangles at the end
        self.render_lines(points, color)

        # fmt: off
        vertices = np.array([
            -0.25, -0.25, 0.0,
             0.0,   0.25, 0.0,
             0.25, -0.25, 0.0,
        ], dtype=np.float32)
        # fmt: on

        gl.glUseProgram(self.sprite_shader)
        gl.glBindVertexArray(self.vao)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo)
        gl.glBufferData(
            gl.GL_ARRAY_BUFFER, vertices.nbytes, vertices, gl.GL_DYNAMIC_DRAW
        )

        for i in range(0, len(points), 6):
            chunk = points[i:i+6]
            target = glm.vec3(chunk[3], chunk[4], chunk[5])

            model_matrix = glm.identity(glm.mat4x4)
            model_matrix = glm.translate(model_matrix, target)
            scale = 40.0
            model_matrix = glm.scale(
                model_matrix,
                # convert to world space
                glm.vec3(scale, scale, scale),
            )

            gl.glUniformMatrix4fv(
                gl.glGetUniformLocation(self.sprite_shader, "model_matrix"),
                1,
                gl.GL_FALSE,
                glm.value_ptr(model_matrix),
            )

            gl.glDrawArrays(gl.GL_TRIANGLES, 0, 3)
