import OpenGL.GL as gl
from OpenGL.GL import shaders
from pyglm import glm
import numpy as np
import time
import ctypes
from dataclasses import dataclass

VERT_SHADER = """
#version 330 core
layout(location = 0) in vec2 a_Position;
uniform float scale;
uniform mat4 proj_matrix;
uniform mat4 model_matrix;
void main() {
    gl_Position = proj_matrix * model_matrix * vec4(a_Position * scale, 0.0, 1.0);
}
"""

FRAG_SHADER = """
#version 330 core
out vec4 FragColor;
uniform vec3 color;
uniform float alpha;
void main() {
    FragColor = vec4(color, alpha);
}
"""


@dataclass
class Instance:
    start_time: float
    scale: float
    color: list
    x: np.float32
    y: np.float32


class EmitterRenderer:
    def __init__(
        self,
        window_width,
        window_height,
        segments=100,
        expansion_speed=1.0,
        duration=0.5,
        fade_speed=1.0,
    ):
        self.active_instances = []
        self.duration = duration
        self.segments = segments
        self.expansion_speed = expansion_speed
        self.fade_speed = fade_speed

        self.vao = gl.glGenVertexArrays(1)
        self.vbo = gl.glGenBuffers(1)
        gl.glBindVertexArray(self.vao)

        vert = shaders.compileShader(VERT_SHADER, gl.GL_VERTEX_SHADER)
        frag = shaders.compileShader(FRAG_SHADER, gl.GL_FRAGMENT_SHADER)
        self.shader_program = shaders.compileProgram(vert, frag)

        vertices = []
        for i in range(self.segments):
            angle = 2.0 * np.pi * i / self.segments
            x = np.cos(angle)
            y = np.sin(angle)
            vertices.extend([x * 0.5, y * 0.5])

        vertex_data = np.array(vertices, dtype=np.float32)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo)
        gl.glBufferData(
            gl.GL_ARRAY_BUFFER, vertex_data.nbytes, vertex_data, gl.GL_STATIC_DRAW
        )

        gl.glEnableVertexAttribArray(0)
        gl.glVertexAttribPointer(
            0, 2, gl.GL_FLOAT, gl.GL_FALSE, 2 * 4, ctypes.c_void_p(0)
        )

        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)
        gl.glBindVertexArray(0)

        self.loc_scale = gl.glGetUniformLocation(self.shader_program, "scale")
        self.loc_alpha = gl.glGetUniformLocation(self.shader_program, "alpha")
        self.loc_color = gl.glGetUniformLocation(self.shader_program, "color")

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

    def add_instance(self, scale, color, x, y):
        start_time = time.time()
        new_instance = Instance(start_time, scale, color, x, y)
        self.active_instances.append(new_instance)

    def render(self):
        current_time = time.time()

        if not self.active_instances:
            return

        next_active_instances = []

        gl.glUseProgram(self.shader_program)
        transform_loc = gl.glGetUniformLocation(self.shader_program, "proj_matrix")
        gl.glUniformMatrix4fv(
            transform_loc, 1, gl.GL_FALSE, glm.value_ptr(self.proj_matrix)
        )

        for instance in self.active_instances:
            elapsed = current_time - instance.start_time
            if elapsed >= self.duration:
                continue

            progress = elapsed / self.duration
            current_scale = progress * self.expansion_speed
            current_alpha = max(0.0, 1.0 - (progress * self.fade_speed))

            model_matrix = glm.mat4(1.0)
            model_matrix = glm.translate(
                model_matrix,
                glm.vec3(
                    instance.x,
                    instance.y,
                    0.0,
                ),
            )
            model_matrix = glm.scale(
                model_matrix,
                glm.vec3(
                    instance.scale,
                    instance.scale,
                    instance.scale,
                ),
            )

            transform_loc = gl.glGetUniformLocation(self.shader_program, "model_matrix")
            gl.glUniformMatrix4fv(
                transform_loc, 1, gl.GL_FALSE, glm.value_ptr(model_matrix)
            )

            gl.glUniform1f(self.loc_scale, current_scale)
            gl.glUniform1f(self.loc_alpha, current_alpha)
            gl.glUniform3f(
                self.loc_color, instance.color[0], instance.color[1], instance.color[2]
            )

            gl.glBindVertexArray(self.vao)
            gl.glDrawArrays(gl.GL_LINE_LOOP, 0, self.segments)
            next_active_instances.append(instance)

        self.active_instances = next_active_instances
        gl.glBindVertexArray(0)
        gl.glUseProgram(0)
