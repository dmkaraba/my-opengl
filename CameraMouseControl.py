import glfw
import numpy as np
import pyrr
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
from utils.Camera import Camera
from utils.ObjLoader import MyObjLoader
from utils.TextureLoader import load_texture


WINDOW_RESOLUTION = (1280, 720)

vertex_src = """
# version 330
layout(location = 0) in vec3 a_position;
layout(location = 1) in vec2 a_texture;

uniform mat4 model;
uniform mat4 projection;
uniform mat4 view;

out vec2 v_texture;

void main()
{
    gl_Position = projection * view * model * vec4(a_position, 1.0);
    v_texture = a_texture;
}
"""

fragment_src = """
# version 330
in vec2 v_texture;
out vec4 out_color;

uniform sampler2D s_texture;

void main()
{
    out_color = texture(s_texture, v_texture);
}
"""


def window_resize(window, width, height):
    glViewport(0, 0, width, height)


def key_callback(window, key, scancode, action, mods):
    camera.keyboard_update(key)


def cursor_position_callback(window, xpos, ypos):
    camera.mouth_update(np.array([xpos, ypos]))
    glfw.set_cursor_pos(window, WINDOW_RESOLUTION[0]/2, WINDOW_RESOLUTION[1]/2)


if not glfw.init():
    raise Exception('glfw con not be initialized')

window = glfw.create_window(1280, 720, 'My OpenGL window', None, None)

if not window:
    glfw.terminate()
    raise Exception('glfw window can not be created')

glfw.set_window_pos(window, 4000, 200)
glfw.set_cursor_pos(window, WINDOW_RESOLUTION[0]/2, WINDOW_RESOLUTION[1]/2)
glfw.set_window_size_callback(window, window_resize)
glfw.set_key_callback(window, key_callback)
glfw.set_cursor_pos_callback(window, cursor_position_callback)

glfw.make_context_current(window)

pig_indices, pig_buffer = MyObjLoader.load_model('course/meshes/pig.obj')

shader = compileProgram(
    compileShader(vertex_src, GL_VERTEX_SHADER),
    compileShader(fragment_src, GL_FRAGMENT_SHADER)
)

texture = glGenTextures(1)
load_texture("course/textures/pig_diffuse.jpg", texture)

VBO = glGenBuffers(1)
glBindBuffer(GL_ARRAY_BUFFER, VBO)
glBufferData(GL_ARRAY_BUFFER, pig_buffer.nbytes, pig_buffer, GL_STATIC_DRAW)

EBO = glGenBuffers(1)
glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO)
glBufferData(GL_ELEMENT_ARRAY_BUFFER, pig_indices.nbytes, pig_indices, GL_STATIC_DRAW)

glEnableVertexAttribArray(0)
glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, pig_buffer.itemsize * 8, ctypes.c_void_p(0))

glEnableVertexAttribArray(1)
glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, pig_buffer.itemsize * 8, ctypes.c_void_p(12))


glUseProgram(shader)
glClearColor(0, 0.1, 0.1, 1)
glEnable(GL_DEPTH_TEST)

model_loc = glGetUniformLocation(shader, "model")
projection_loc = glGetUniformLocation(shader, "projection")
view_loc = glGetUniformLocation(shader, "view")

camera = Camera()

projection = pyrr.matrix44.create_perspective_projection_matrix(
                45, WINDOW_RESOLUTION[0]/WINDOW_RESOLUTION[1], 0.1, 100)
pos = pyrr.matrix44.create_from_translation(pyrr.Vector3((0, 0, -4)))
glUniformMatrix4fv(model_loc, 1, GL_FALSE, pos)
glUniformMatrix4fv(projection_loc, 1, GL_FALSE, projection)

while not glfw.window_should_close(window):
    glfw.poll_events()
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
    view = camera.get_world_to_view_matrix()
    glUniformMatrix4fv(view_loc, 1, GL_FALSE, view)
    # glDrawElements(GL_TRIANGLES, len(pig_indices), GL_UNSIGNED_INT, None)
    glDrawArrays(GL_TRIANGLES, 0, len(pig_indices))
    glfw.swap_buffers(window)

glfw.terminate()
