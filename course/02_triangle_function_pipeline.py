import glfw
from OpenGL.GL import *
import numpy as np

if not glfw.init():
    raise Exception('glfw con not be initialized')

window = glfw.create_window(1280, 720, 'My OpenGL window', None, None)

if not window:
    glfw.terminate()
    raise Exception('glfw window can not be created')

glfw.set_window_pos(window, 3400, 200)
glfw.make_context_current(window)

vertices = [-0.5, -0.5, 0.0,
             0.5, -0.5, 0.0,
             0.0,  0.5, 0.0]

colors = [
    1.0, 0.0, 0.0,
    0.0, 1.0, 0.0,
    0.0, 0.0, 1.0,
]

vertices = np.array(vertices, dtype=np.float32)
colors = np.array(colors, dtype=np.float32)

glEnableClientState(GL_VERTEX_ARRAY)
glVertexPointer(3, GL_FLOAT, 0, vertices)

glEnableClientState(GL_COLOR_ARRAY)
glColorPointer(3, GL_FLOAT, 0, colors)

glClearColor(0, 0.1, 0.1, 1)

while not glfw.window_should_close(window):
    glfw.poll_events()
    glClear(GL_COLOR_BUFFER_BIT)
    glRotatef(2, 0, 1, 0)
    glDrawArrays(GL_TRIANGLES, 0, 3)
    glfw.swap_buffers(window)

glfw.terminate()
