import pyrr
import glfw
import numpy as np
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
from utils.Camera import Camera


WINDOW_RESOLUTION = (1280, 720)


light_vs = """
# version 330
layout(location = 0) in vec3 a_position;

uniform mat4 model;
uniform mat4 projection;
uniform mat4 view;

void main()
{
    gl_Position = projection * view * model * vec4(a_position, 1.0);
}
"""

light_fs = """
# version 330
out vec4 color;

uniform vec3 objectColor;
uniform vec3 lightColor;

void main()
{
    color = vec4(lightColor*objectColor, 1.0);
}
"""

lamp_vs = """
# version 330
layout(location = 0) in vec3 a_position;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

void main()
{
    gl_Position = projection * view * model * vec4(a_position, 1.0);
}
"""

lamp_fs = """
# version 330
out vec4 color;

void main()
{
    color = vec4(1.0, 1.0, 1.0, 1.0);
}
"""


vertices = [-0.5, -0.5, 0.5, 1.0, 0.0, 0.0,
             0.5, -0.5, 0.5, 0.0, 1.0, 0.0,
             0.5,  0.5, 0.5, 0.0, 0.0, 1.0,
            -0.5,  0.5, 0.5, 1.0, 1.0, 1.0,

            -0.5, -0.5, -0.5, 1.0, 0.0, 0.0,
             0.5, -0.5, -0.5, 0.0, 1.0, 0.0,
             0.5,  0.5, -0.5, 0.0, 0.0, 1.0,
            -0.5,  0.5, -0.5, 1.0, 1.0, 1.0]

indices = [0, 1, 2, 2, 3, 0,
           4, 5, 6, 6, 7, 4,
           4, 5, 1, 1, 0, 4,
           6, 7, 3, 3, 2, 6,
           5, 6, 2, 2, 1, 5,
           7, 4, 0, 0, 3, 7]

vertices = np.array(vertices, dtype=np.float32)
indices = np.array(indices, dtype=np.uint32)

camera = Camera()


def window_resize(window, width, height):
    glViewport(0, 0, width, height)


def move_camera(window):
    if glfw.get_key(window, glfw.KEY_W) == glfw.PRESS:
        camera.move_forward()
    if glfw.get_key(window, glfw.KEY_S) == glfw.PRESS:
        camera.move_backward()
    if glfw.get_key(window, glfw.KEY_D) == glfw.PRESS:
        camera.strafe_right()
    if glfw.get_key(window, glfw.KEY_A) == glfw.PRESS:
        camera.strafe_left()
    if glfw.get_key(window, glfw.KEY_R) == glfw.PRESS:
        camera.move_up()
    if glfw.get_key(window, glfw.KEY_F) == glfw.PRESS:
        camera.move_down()


def cursor_position_callback(window, xpos, ypos):
    camera.mouth_update(xpos, ypos)
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
glfw.set_cursor_pos_callback(window, cursor_position_callback)
glfw.make_context_current(window)

light_shader = compileProgram(compileShader(light_vs, GL_VERTEX_SHADER), compileShader(light_fs, GL_FRAGMENT_SHADER))
lamp_shader = compileProgram(compileShader(lamp_vs, GL_VERTEX_SHADER), compileShader(lamp_fs, GL_FRAGMENT_SHADER))

### BOX ###############################
box_VAO = glGenVertexArrays(1)
glBindVertexArray(box_VAO)

VBO = glGenBuffers(1)
glBindBuffer(GL_ARRAY_BUFFER, VBO)
glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

EBO = glGenBuffers(1)
glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO)
glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)

glEnableVertexAttribArray(0)
glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(0))

### LIGHT #############################
lamp_VAO = glGenVertexArrays(1)
glBindVertexArray(lamp_VAO)

lamp_VBO = glGenBuffers(1)
glBindBuffer(GL_ARRAY_BUFFER, lamp_VBO)
glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

lamp_EBO = glGenBuffers(1)
glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, lamp_EBO)
glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)

glEnableVertexAttribArray(0)
glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(0))

glUseProgram(light_shader)
glClearColor(0.1, 0.1, 0.1, 1)
glEnable(GL_DEPTH_TEST)


model_loc = glGetUniformLocation(light_shader, "model")
view_loc = glGetUniformLocation(light_shader, "view")
projection_loc = glGetUniformLocation(light_shader, "projection")
object_loc = glGetUniformLocation(light_shader, "objectColor")
light_loc = glGetUniformLocation(light_shader, "lightColor")

lamp_model_loc = glGetUniformLocation(lamp_shader, "model")
lamp_view_loc = glGetUniformLocation(lamp_shader, "view")
lamp_projection_loc = glGetUniformLocation(lamp_shader, "projection")

lamp_pos = pyrr.matrix44.create_from_translation(pyrr.Vector3((1.2, 1.0, 0.0)))
lamp_scale = pyrr.matrix44.create_from_scale(pyrr.Vector3((0.2, 0.2, 0.2)))
lamp_model = pyrr.matrix44.multiply(lamp_scale, lamp_pos)
pos = pyrr.matrix44.create_from_translation(pyrr.Vector3((0, 0, -4)))
projection = pyrr.matrix44.create_perspective_projection_matrix(
                45, WINDOW_RESOLUTION[0]/WINDOW_RESOLUTION[1], 0.1, 100)

while not glfw.window_should_close(window):
    glfw.poll_events()
    move_camera(window)
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
    glUseProgram(light_shader)
    view = camera.get_world_to_view_matrix()
    glUniformMatrix4fv(view_loc, 1, GL_FALSE, view)
    glUniformMatrix4fv(projection_loc, 1, GL_FALSE, projection)
    glUniformMatrix4fv(model_loc, 1, GL_FALSE, pos)
    glUniform3f(object_loc, 1.0, 0.5, 0.31)
    glUniform3f(light_loc, 1.0, 0.5, 1.0)
    glBindVertexArray(box_VAO)
    glDrawElements(GL_TRIANGLES, len(indices), GL_UNSIGNED_INT, None)

    glUseProgram(lamp_shader)
    glUniformMatrix4fv(lamp_view_loc, 1, GL_FALSE, view)
    glUniformMatrix4fv(lamp_projection_loc, 1, GL_FALSE, projection)
    glUniformMatrix4fv(lamp_model_loc, 1, GL_FALSE, lamp_model)
    glBindVertexArray(lamp_VAO)
    glDrawElements(GL_TRIANGLES, len(indices), GL_UNSIGNED_INT, None)

    glfw.swap_buffers(window)

glfw.terminate()
