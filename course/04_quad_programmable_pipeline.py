import glfw
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import numpy as np


vertex_src = """
# version 330
layout(location = 0) in vec3 a_position;
layout(location = 1) in vec3 a_color;
out vec3 v_color;
void main()
{
    gl_Position = vec4(a_position, 1.0);
    v_color = a_color;
}
"""

fragment_src = """
# version 330
in vec3 v_color;
out vec4 out_color;
void main()
{
    out_color = vec4(v_color, 1.0);
}
"""


def window_resize(window, width, height):
    glViewport(0, 0, width, height)


if not glfw.init():
    raise Exception('glfw con not be initialized')

window = glfw.create_window(1280, 720, 'My OpenGL window', None, None)

if not window:
    glfw.terminate()
    raise Exception('glfw window can not be created')

glfw.set_window_pos(window, 3400, 200)
glfw.set_window_size_callback(window, window_resize)

glfw.make_context_current(window)

buffer = [
    -0.5, -0.5, 0.0, 1.0, 0.0, 0.0,     # each value is 4 bytes
     0.5, -0.5, 0.0, 0.0, 1.0, 0.0,
    -0.5,  0.5, 0.0, 0.0, 0.0, 1.0,
     0.5,  0.5, 0.0, 1.0, 1.0, 1.0
]

buffer = np.array(buffer, dtype=np.float32)

shader = compileProgram(
    compileShader(vertex_src, GL_VERTEX_SHADER), compileShader(fragment_src, GL_FRAGMENT_SHADER))

VBO = glGenBuffers(1)
glBindBuffer(GL_ARRAY_BUFFER, VBO)
glBufferData(GL_ARRAY_BUFFER, buffer.nbytes, buffer, GL_STATIC_DRAW)

# thanks to "layout(location = 0)" into vertex_src we don't need this line
# position = glGetAttribLocation(shader, "a_position")
glEnableVertexAttribArray(0)
glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(0))

# thanks to "layout(location = 1)" into vertex_src we don't need this line
# color = glGetAttribLocation(shader, "a_color")
glEnableVertexAttribArray(1)
glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(12))

glUseProgram(shader)
glClearColor(0, 0.1, 0.1, 1)

while not glfw.window_should_close(window):
    glfw.poll_events()
    glClear(GL_COLOR_BUFFER_BIT)
    glRotatef(2, 0, 1, 0)
    glDrawArrays(GL_TRIANGLE_STRIP, 0, 4)
    glfw.swap_buffers(window)

glfw.terminate()
