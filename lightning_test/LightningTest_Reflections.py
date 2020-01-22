import pyrr
import glfw
import numpy as np
from OpenGL.GL import *
from utils.Camera import Camera
from utils.TextureLoader import load_texture, load_cubemap
from utils.ObjLoader import MyObjLoader
from utils.Shader import ShaderLoader


WINDOW_RESOLUTION = (1280, 720)

cube_vertices = [
    -0.5, -0.5, -0.5, 0.0, 0.0, 0.0, 0.0, -1.0,
    0.5,  -0.5, -0.5, 1.0, 0.0, 0.0, 0.0, -1.0,
    0.5,   0.5, -0.5, 1.0, 1.0, 0.0, 0.0, -1.0,
    0.5,   0.5, -0.5, 1.0, 1.0, 0.0, 0.0, -1.0,
    -0.5,  0.5, -0.5, 0.0, 1.0, 0.0, 0.0, -1.0,
    -0.5, -0.5, -0.5, 0.0, 0.0, 0.0, 0.0, -1.0,

    -0.5, -0.5,  0.5, 0.0, 0.0, 0.0,  0.0, 1.0,
    0.5,  -0.5,  0.5, 1.0, 0.0, 0.0,  0.0, 1.0,
    0.5,   0.5,  0.5, 1.0, 1.0, 0.0,  0.0, 1.0,
    0.5,   0.5,  0.5, 1.0, 1.0, 0.0,  0.0, 1.0,
    -0.5,  0.5,  0.5, 0.0, 1.0, 0.0,  0.0, 1.0,
    -0.5, -0.5,  0.5, 0.0, 0.0, 0.0,  0.0, 1.0,

    -0.5,  0.5,  0.5, 1.0, 0.0, -1.0, 0.0, 0.0,
    -0.5,  0.5, -0.5, 1.0, 1.0, -1.0, 0.0, 0.0,
    -0.5, -0.5, -0.5, 0.0, 1.0, -1.0, 0.0, 0.0,
    -0.5, -0.5, -0.5, 0.0, 1.0, -1.0, 0.0, 0.0,
    -0.5, -0.5,  0.5, 0.0, 0.0, -1.0, 0.0, 0.0,
    -0.5,  0.5,  0.5, 1.0, 0.0, -1.0, 0.0, 0.0,

    0.5,   0.5,  0.5, 1.0, 0.0, 1.0,  0.0, 0.0,
    0.5,   0.5, -0.5, 1.0, 1.0, 1.0,  0.0, 0.0,
    0.5,  -0.5, -0.5, 0.0, 1.0, 1.0,  0.0, 0.0,
    0.5,  -0.5, -0.5, 0.0, 1.0, 1.0,  0.0, 0.0,
    0.5,  -0.5,  0.5, 0.0, 0.0, 1.0,  0.0, 0.0,
    0.5,   0.5,  0.5, 1.0, 0.0, 1.0,  0.0, 0.0,

    -0.5, -0.5, -0.5, 0.0, 1.0, 0.0, -1.0, 0.0,
    0.5,  -0.5, -0.5, 1.0, 1.0, 0.0, -1.0, 0.0,
    0.5,  -0.5,  0.5, 1.0, 0.0, 0.0, -1.0, 0.0,
    0.5,  -0.5,  0.5, 1.0, 0.0, 0.0, -1.0, 0.0,
    -0.5, -0.5,  0.5, 0.0, 0.0, 0.0, -1.0, 0.0,
    -0.5, -0.5, -0.5, 0.0, 1.0, 0.0, -1.0, 0.0,

    -0.5,  0.5, -0.5, 0.0, 1.0, 0.0,  1.0, 0.0,
    0.5,   0.5, -0.5, 1.0, 1.0, 0.0,  1.0, 0.0,
    0.5,   0.5,  0.5, 1.0, 0.0, 0.0,  1.0, 0.0,
    0.5,   0.5,  0.5, 1.0, 0.0, 0.0,  1.0, 0.0,
    -0.5,  0.5,  0.5, 0.0, 0.0, 0.0,  1.0, 0.0,
    -0.5,  0.5, -0.5, 0.0, 1.0, 0.0,  1.0, 0.0,
]

skybox_vertices = [
    -1.0,  1.0, -1.0,
    -1.0, -1.0, -1.0,
     1.0, -1.0, -1.0,
     1.0, -1.0, -1.0,
     1.0,  1.0, -1.0,
    -1.0,  1.0, -1.0,

    -1.0, -1.0,  1.0,
    -1.0, -1.0, -1.0,
    -1.0,  1.0, -1.0,
    -1.0,  1.0, -1.0,
    -1.0,  1.0,  1.0,
    -1.0, -1.0,  1.0,

     1.0, -1.0, -1.0,
     1.0, -1.0,  1.0,
     1.0,  1.0,  1.0,
     1.0,  1.0,  1.0,
     1.0,  1.0, -1.0,
     1.0, -1.0, -1.0,

    -1.0, -1.0, 1.0,
    -1.0,  1.0, 1.0,
     1.0,  1.0, 1.0,
     1.0,  1.0, 1.0,
     1.0, -1.0, 1.0,
    -1.0, -1.0, 1.0,

    -1.0, 1.0, -1.0,
     1.0, 1.0, -1.0,
     1.0, 1.0,  1.0,
     1.0, 1.0,  1.0,
    -1.0, 1.0,  1.0,
    -1.0, 1.0, -1.0,

    -1.0, -1.0, -1.0,
    -1.0, -1.0,  1.0,
     1.0, -1.0, -1.0,
     1.0, -1.0, -1.0,
    -1.0, -1.0,  1.0,
     1.0, -1.0,  1.0
]

cube_vertices = np.array(cube_vertices, dtype=np.float32)
skybox_vertices = np.array(skybox_vertices, dtype=np.float32)

camera = Camera(pyrr.Vector3((0.0, 0.0, 3.0)))


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


if not glfw.init():
    raise Exception('glfw con not be initialized')

window = glfw.create_window(1280, 720, 'My OpenGL window', None, None)

if not window:
    glfw.terminate()
    raise Exception('glfw window can not be created')

glfw.set_window_pos(window, 4000, 200)
glfw.set_cursor_pos(window, WINDOW_RESOLUTION[0] / 2, WINDOW_RESOLUTION[1] / 2)
glfw.set_window_size_callback(window, window_resize)
glfw.set_cursor_pos_callback(window, cursor_position_callback)
glfw.make_context_current(window)

glEnable(GL_DEPTH_TEST)

# ============================================================ #
#                   Loading shaders                            #
# ============================================================ #
shader = ShaderLoader('lightning_test/shaders/test.vs', 'lightning_test/shaders/test.fs')
test_shader = shader.get_compiled_shader()
shader = ShaderLoader('lightning_test/shaders/skybox.vs', 'lightning_test/shaders/skybox.fs')
skybox_shader = shader.get_compiled_shader()

# ============================================================ #
#                   Loading textures                           #
# ============================================================ #
textureID = glGenTextures(2)
load_texture('lightning_test/textures/container.png', textureID[0])

cubemap_images = [
    'lightning_test/textures/skybox/right.tga',
    'lightning_test/textures/skybox/left.tga',
    'lightning_test/textures/skybox/top.tga',
    'lightning_test/textures/skybox/bottom.tga',
    'lightning_test/textures/skybox/back.tga',
    'lightning_test/textures/skybox/front.tga',
]
cubemapTexture = load_cubemap(cubemap_images, textureID[1])

# ============================================================ #
#               Setup Cube Vertex Array Object                 #
# ============================================================ #
cube_VAO = glGenVertexArrays(1)
glBindVertexArray(cube_VAO)

VBO = glGenBuffers(1)
glBindBuffer(GL_ARRAY_BUFFER, VBO)
glBufferData(GL_ARRAY_BUFFER, cube_vertices.nbytes, cube_vertices, GL_STATIC_DRAW)

glEnableVertexAttribArray(0)
glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, cube_vertices.itemsize * 8, ctypes.c_void_p(0))
glEnableVertexAttribArray(1)
glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, cube_vertices.itemsize * 8, ctypes.c_void_p(12))
glEnableVertexAttribArray(2)
glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, cube_vertices.itemsize * 8, ctypes.c_void_p(20))

# ============================================================ #
#              Setup Monkey Vertex Array Object                #
# ============================================================ #
monkey_indices, monkey_buffer = MyObjLoader.load_model('lightning_test/meshes/monkey.obj')

monkey_VAO = glGenVertexArrays(1)
glBindVertexArray(monkey_VAO)

VBO = glGenBuffers(1)
glBindBuffer(GL_ARRAY_BUFFER, VBO)
glBufferData(GL_ARRAY_BUFFER, monkey_buffer.nbytes, monkey_buffer, GL_STATIC_DRAW)

glEnableVertexAttribArray(0)
glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, monkey_buffer.itemsize * 8, ctypes.c_void_p(0))
glEnableVertexAttribArray(1)
glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, monkey_buffer.itemsize * 8, ctypes.c_void_p(12))
glEnableVertexAttribArray(2)
glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, monkey_buffer.itemsize * 8, ctypes.c_void_p(20))

# ============================================================ #
#              Setup Skybox Vertex Array Object                #
# ============================================================ #
skybox_VAO = glGenVertexArrays(1)
glBindVertexArray(skybox_VAO)

skybox_VBO = glGenBuffers(1)
glBindBuffer(GL_ARRAY_BUFFER, skybox_VBO)
glBufferData(GL_ARRAY_BUFFER, skybox_vertices.nbytes, skybox_vertices, GL_STATIC_DRAW)

glEnableVertexAttribArray(0)
glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, skybox_vertices.itemsize * 3, ctypes.c_void_p(0))

glClearColor(0.1, 0.1, 0.1, 1)

test_model_loc = glGetUniformLocation(test_shader, "model")
test_view_loc = glGetUniformLocation(test_shader, "view")
test_projection_loc = glGetUniformLocation(test_shader, "projection")
test_camera_pos_loc = glGetUniformLocation(test_shader, "cameraPos")

skybox_view_loc = glGetUniformLocation(skybox_shader, "view")
skybox_projection_loc = glGetUniformLocation(skybox_shader, "projection")

projection = pyrr.matrix44.create_perspective_projection_matrix(
    45, WINDOW_RESOLUTION[0] / WINDOW_RESOLUTION[1], 0.1, 100)

while not glfw.window_should_close(window):
    glfw.poll_events()
    move_camera(window)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # ============================================================ #
    #                       Draw a Cube                            #
    # ============================================================ #
    glUseProgram(test_shader)
    model = pyrr.matrix44.create_from_translation(pyrr.Vector3((0, 0, 0)))
    view = camera.get_world_to_view_matrix()
    rot_x = pyrr.Matrix44.from_y_rotation(0.5 * glfw.get_time())
    model = pyrr.matrix44.multiply(rot_x, model)
    glUniformMatrix4fv(test_model_loc, 1, GL_FALSE, model)
    glUniformMatrix4fv(test_view_loc, 1, GL_FALSE, view)
    glUniformMatrix4fv(test_projection_loc, 1, GL_FALSE, projection)
    glUniform3fv(test_camera_pos_loc, 1, GL_FALSE, pyrr.Vector3(camera.position))

    glBindVertexArray(monkey_VAO)
    glBindTexture(GL_TEXTURE_CUBE_MAP, textureID[1])
    glDrawArrays(GL_TRIANGLES, 0, len(monkey_indices))
    glBindVertexArray(0)

    # ============================================================ #
    #                       Draw a Skybox                          #
    # ============================================================ #
    glUseProgram(skybox_shader)
    glDepthFunc(GL_LEQUAL)

    # Pass the matrices to the shader
    view = pyrr.Matrix44(pyrr.Matrix33(camera.get_world_to_view_matrix()))  # Remove any translation component of the view matrix
    glUniformMatrix4fv(skybox_view_loc, 1, GL_FALSE, view)
    glUniformMatrix4fv(skybox_projection_loc, 1, GL_FALSE, projection)

    # skybox cube
    glBindVertexArray(skybox_VAO)
    glBindTexture(GL_TEXTURE_CUBE_MAP, textureID[1])
    glDrawArrays(GL_TRIANGLES, 0, 36)
    glBindVertexArray(0)
    glDepthFunc(GL_LESS)

    glfw.swap_buffers(window)

glfw.terminate()
