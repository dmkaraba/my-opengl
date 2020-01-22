import glfw
import numpy as np
import pyrr
from race_game.assets.car import Car
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
from utils.Camera import Camera
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

grid_vertices = [-1, 0,  1, 0.0, 0.0,
                 -1, 0, -1, 0.0, 1.0,
                  1, 0, -1, 1.0, 1.0,
                  1, 0,  1, 1.0, 0.0]

grid_indices = [0, 1, 2, 0, 2, 3]

grid_vertices = np.array(grid_vertices, dtype=np.float32)
grid_indices = np.array(grid_indices, dtype=np.uint32)


def window_resize(window, width, height):
    glViewport(0, 0, width, height)


def key_check(window):
    if glfw.get_key(window, glfw.KEY_S) == glfw.PRESS:
        car.reverse = True
        car.speed = car.speed + car.acceleration * time_since_last_frame
        car.speed = min(car.max_speed, car.speed)
    if glfw.get_key(window, glfw.KEY_W) == glfw.PRESS:
        car.reverse = False
        car.speed = car.speed + car.acceleration * time_since_last_frame
        car.speed = min(car.max_speed, car.speed)
    if (glfw.get_key(window, glfw.KEY_W) == glfw.PRESS or glfw.get_key(window, glfw.KEY_S) == glfw.PRESS) \
            and glfw.get_key(window, glfw.KEY_A) == glfw.PRESS:
        car.speed = car.speed + car.acceleration * time_since_last_frame
        car.speed = min(car.max_speed, car.speed)
        car.turn_left()
    if (glfw.get_key(window, glfw.KEY_W) == glfw.PRESS or glfw.get_key(window, glfw.KEY_S) == glfw.PRESS) \
            and glfw.get_key(window, glfw.KEY_D) == glfw.PRESS:
        car.speed = car.speed + car.acceleration * time_since_last_frame
        car.speed = min(car.max_speed, car.speed)
        car.turn_right()


# def key_callback(window, key, scancode, action, mods):
#     print(key, scancode, action, mods)
#     if glfw.get_key(window, glfw.KEY_W) == glfw.PRESS:
#         car.speed = car.speed + car.acceleration * time_since_last_frame
#         car.speed = min(car.max_speed, car.speed)
#     if glfw.get_key(window, glfw.KEY_W) == glfw.PRESS and glfw.get_key(window, glfw.KEY_A) == glfw.PRESS:
#         car.speed = car.speed + car.acceleration * time_since_last_frame
#         car.speed = min(car.max_speed, car.speed)
#         car.turn_left()
#     if glfw.get_key(window, glfw.KEY_W) == glfw.PRESS and glfw.get_key(window, glfw.KEY_D) == glfw.PRESS:
#         car.speed = car.speed + car.acceleration * time_since_last_frame
#         car.speed = min(car.max_speed, car.speed)
#         car.turn_right()


def cursor_position_callback(window, xpos, ypos):
    # camera.mouth_update(np.array([xpos, ypos]))
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
# glfw.set_key_callback(window, key_callback)
glfw.set_cursor_pos_callback(window, cursor_position_callback)
glfw.make_context_current(window)


car = Car()


shader = compileProgram(
    compileShader(vertex_src, GL_VERTEX_SHADER),
    compileShader(fragment_src, GL_FRAGMENT_SHADER)
)

texture = glGenTextures(2)
load_texture(car.texture_path, texture[0])
load_texture("race_game/textures/uv_grid.jpg", texture[1])

# Car #############################################
car_VAO = glGenVertexArrays(1)
glBindVertexArray(car_VAO)

car_VBO = glGenBuffers(1)
glBindBuffer(GL_ARRAY_BUFFER, car_VBO)
glBufferData(GL_ARRAY_BUFFER, car.buffer.nbytes, car.buffer, GL_STATIC_DRAW)

car_EBO = glGenBuffers(1)
glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, car_EBO)
glBufferData(GL_ELEMENT_ARRAY_BUFFER, car.indices.nbytes, car.indices, GL_STATIC_DRAW)

glEnableVertexAttribArray(0)
glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, car.buffer.itemsize * 8, ctypes.c_void_p(0))
glEnableVertexAttribArray(1)
glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, car.buffer.itemsize * 8, ctypes.c_void_p(12))

# Quad ############################################
quad_VAO = glGenVertexArrays(1)
glBindVertexArray(quad_VAO)

quad_VBO = glGenBuffers(1)
glBindBuffer(GL_ARRAY_BUFFER, quad_VBO)
glBufferData(GL_ARRAY_BUFFER, grid_vertices.nbytes, grid_vertices, GL_STATIC_DRAW)

quad_EBO = glGenBuffers(1)
glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, quad_EBO)
glBufferData(GL_ELEMENT_ARRAY_BUFFER, grid_indices.nbytes, grid_indices, GL_STATIC_DRAW)

glEnableVertexAttribArray(0)
glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, grid_vertices.itemsize * 5, ctypes.c_void_p(0))
glEnableVertexAttribArray(1)
glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, grid_vertices.itemsize * 5, ctypes.c_void_p(12))
##################################################

glUseProgram(shader)
glClearColor(0, 0.1, 0.1, 1)
glEnable(GL_DEPTH_TEST)

model_loc = glGetUniformLocation(shader, "model")
projection_loc = glGetUniformLocation(shader, "projection")
view_loc = glGetUniformLocation(shader, "view")

camera = Camera()
camera.position = pyrr.Vector3((0, 1, 3))

grid_scale = pyrr.matrix44.create_from_scale(pyrr.Vector3((10, 0, 25)))
projection = pyrr.matrix44.create_perspective_projection_matrix(
                45, WINDOW_RESOLUTION[0]/WINDOW_RESOLUTION[1], 0.1, 100)
glUniformMatrix4fv(projection_loc, 1, GL_FALSE, projection)

t = 0
while not glfw.window_should_close(window):
    global time_since_last_frame
    time_since_last_frame = glfw.get_time() - t

    key_check(window)

    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

    glBindVertexArray(car_VAO)
    glBindTexture(GL_TEXTURE_2D, texture[0])

    ### Car
    car.speed -= car.damping_acceleration * time_since_last_frame
    car.speed = max(car.speed, 0)
    if not car.reverse:
        car.position = car.position + car.headVector * car.speed
    else:
        car.position = car.position - car.headVector * car.speed

    car_pos = pyrr.matrix44.create_from_translation(car.position)
    car_rot = pyrr.matrix44.create_from_y_rotation(car.steer_angle)
    model = pyrr.matrix44.multiply(car_rot, car_pos)
    glUniformMatrix4fv(model_loc, 1, GL_FALSE, model)

    # set Camera
    camera.position = car.position - pyrr.vector3.normalize(car.headVector) * 2 + pyrr.Vector3((0, 1, 0))
    camera.front = pyrr.vector3.normalize(car.position - camera.position)
    view = camera.get_world_to_view_matrix()
    glUniformMatrix4fv(view_loc, 1, GL_FALSE, view)

    glDrawArrays(GL_TRIANGLES, 0, len(car.indices))

    glBindVertexArray(quad_VAO)
    glBindTexture(GL_TEXTURE_2D, texture[1])
    glUniformMatrix4fv(model_loc, 1, GL_FALSE, grid_scale)
    glDrawElements(GL_TRIANGLES, len(grid_indices), GL_UNSIGNED_INT, None)

    glfw.swap_buffers(window)
    glfw.poll_events()
    t = glfw.get_time()

glfw.terminate()
