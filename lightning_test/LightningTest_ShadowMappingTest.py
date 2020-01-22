import pyrr
import glfw
import numpy as np
from OpenGL.GL import *
from utils.Camera import Camera
from utils.TextureLoader import load_texture, create_2D_texture_depth
from utils.Shader import ShaderLoader


SCR_WIDTH = 1280
SCR_HEIGHT = 720

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

cubePositions = [
    (0.0,  0.0,  0.0),
    (2.0,  5.0,  -15.0),
    (-1.5, -2.2, -2.5),
    (-3.8, -2.0, -12.3),
    (2.4,  -0.4, 2.5),
    (-1.7, 3.0,  -7.5),
    (1.3,  -2.0, -2.5),
    (1.5,  2.0,  -2.5),
    (1.5,  0.2,  -1.5),
    (-1.3, 1.0,  -1.0),
]

# quad_vertices = [
#    -1.0,  1.0, 0.0, 1.0,
#    -1.0, -1.0, 0.0, 0.0,
#     1.0, -1.0, 1.0, 0.0,
#    -1.0,  1.0, 0.0, 1.0,
#     1.0, -1.0, 1.0, 0.0,
#     1.0,  1.0, 1.0, 1.0
# ]

quad_vertices = [
    -1.0,  1.0, 0.0, 0.0, 1.0,
    -1.0, -1.0, 0.0, 0.0, 0.0,
     1.0,  1.0, 0.0, 1.0, 1.0,
     1.0, -1.0, 0.0, 1.0, 0.0,
]

plane_vertices = [
    -10.0, 0.0,  10.0, 0.0, 0.0,
    -10.0, 0.0, -10.0, 0.0, 2.0,
     10.0, 0.0,  10.0, 2.0, 0.0,
     10.0, 0.0,  10.0, 2.0, 0.0,
    -10.0, 0.0, -10.0, 0.0, 2.0,
     10.0, 0.0, -10.0, 2.0, 2.0
]

cube_vertices = np.array(cube_vertices, dtype=np.float32)
quad_vertices = np.array(quad_vertices, dtype=np.float32)
plane_vertices = np.array(plane_vertices, dtype=np.float32)

camera = Camera(pyrr.Vector3((0.0, 0.0, 5.0)))


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


window = glfw.create_window(SCR_WIDTH, SCR_HEIGHT, 'My OpenGL window', None, None)

if not window:
    glfw.terminate()
    raise Exception('glfw window can not be created')


glfw.set_window_pos(window, 4000, 200)
glfw.set_cursor_pos(window, SCR_WIDTH / 2, SCR_HEIGHT / 2)
glfw.set_window_size_callback(window, window_resize)
glfw.set_cursor_pos_callback(window, cursor_position_callback)
glfw.make_context_current(window)

# ============================================================ #
#                   Loading shaders                            #
# ============================================================ #
shader = ShaderLoader('lightning_test/shaders/cube.vs', 'lightning_test/shaders/cube.fs')
cube_shader = shader.get_compiled_shader()
shader = ShaderLoader('lightning_test/shaders/simple_depth.vs', 'lightning_test/shaders/simple_depth.fs')
simple_depth_shader = shader.get_compiled_shader()
shader = ShaderLoader('lightning_test/shaders/screen_quad.vs', 'lightning_test/shaders/screen_quad.fs')
screen_quad_shader = shader.get_compiled_shader()

# ============================================================ #
#                   Loading textures                           #
# ============================================================ #
textureID = glGenTextures(2)
load_texture('lightning_test/textures/container.png', textureID[0])
load_texture('lightning_test/textures/floor_tiles.jpg', textureID[1])

# ============================================================ #
#                  configure depth map FBO                     #
# ============================================================ #
SHADOW_WIDTH = 1024
SHADOW_HEIGHT = 1024
depthMapFBO = glGenFramebuffers(1)

# create depth texture
depthMap = glGenTextures(1)
create_2D_texture_depth(depthMap, SHADOW_WIDTH, SHADOW_HEIGHT)
# attach depth texture as FBO's depth buffer
glBindFramebuffer(GL_FRAMEBUFFER, depthMapFBO)
glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_TEXTURE_2D, depthMap, 0)
glDrawBuffer(GL_NONE)
glReadBuffer(GL_NONE)
glBindFramebuffer(GL_FRAMEBUFFER, 0)

# ============================================================ #
#               Setup Cube Vertex Array Object (VAO)           #
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

# ============================================================ #
#               Setup Plane Vertex Array Object (VAO)          #
# ============================================================ #
plane_VAO = glGenVertexArrays(1)
glBindVertexArray(plane_VAO)

VBO = glGenBuffers(1)
glBindBuffer(GL_ARRAY_BUFFER, VBO)
glBufferData(GL_ARRAY_BUFFER, plane_vertices.nbytes, plane_vertices, GL_STATIC_DRAW)

glEnableVertexAttribArray(0)
glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, plane_vertices.itemsize * 5, ctypes.c_void_p(0))
glEnableVertexAttribArray(1)
glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, plane_vertices.itemsize * 5, ctypes.c_void_p(12))

# ============================================================ #
#       Setup screen quad Vertex Array Object (VAO)            #
# ============================================================ #
quad_VAO = glGenVertexArrays(1)
glBindVertexArray(quad_VAO)

VBO = glGenBuffers(1)
glBindBuffer(GL_ARRAY_BUFFER, VBO)
glBufferData(GL_ARRAY_BUFFER, quad_vertices.nbytes, quad_vertices, GL_STATIC_DRAW)

glEnableVertexAttribArray(0)
glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, quad_vertices.itemsize * 5, ctypes.c_void_p(0))
glEnableVertexAttribArray(1)
glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, quad_vertices.itemsize * 5, ctypes.c_void_p(12))


cube_model_loc = glGetUniformLocation(cube_shader, "model")
cube_view_loc = glGetUniformLocation(cube_shader, "view")
cube_projection_loc = glGetUniformLocation(cube_shader, "projection")
cube_texture1_loc = glGetUniformLocation(cube_shader, "texture1")
lightSpaceMatrix_loc = glGetUniformLocation(simple_depth_shader, "lightSpaceMatrix")
lightModel_loc = glGetUniformLocation(simple_depth_shader, "model")
screenTexture_loc = glGetUniformLocation(screen_quad_shader, "screenTexture")

# ============================================================ #
#                   Shader configuration                       #
# ============================================================ #
# glUseProgram(cube_shader)
# glUniform1i(cube_texture1_loc, 0)
glUseProgram(screen_quad_shader)
glUniform1i(screenTexture_loc, 0)

lightPos = pyrr.Vector3((-2.0, 4.0, -1.0))

glEnable(GL_DEPTH_TEST)

while not glfw.window_should_close(window):
    glfw.poll_events()
    move_camera(window)

    glClearColor(0.1, 0.1, 0.1, 1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # In the first pass we use a different projection and view matrix
    # to render the scene from the light's point of view.
    lightProjection = pyrr.matrix44.create_orthogonal_projection_matrix(
        left=-10, right=10, bottom=-10, top=10, near=1.0, far=7.5)
    lightView = pyrr.matrix44.create_look_at(
        eye=lightPos,
        target=pyrr.Vector3((0.0, 0.0, 0.0)),
        up=pyrr.Vector3((0.0, 1.0, 0.0))
    )
    lightSpaceMatrix = pyrr.matrix44.multiply(lightView, lightProjection)

    glUseProgram(simple_depth_shader)
    glUniformMatrix4fv(lightSpaceMatrix_loc, 1, GL_FALSE, lightSpaceMatrix)
    glViewport(0, 0, SHADOW_WIDTH, SHADOW_HEIGHT)
    glBindFramebuffer(GL_FRAMEBUFFER, depthMapFBO)
    glClear(GL_DEPTH_BUFFER_BIT)
    glActiveTexture(GL_TEXTURE0)
    glBindTexture(GL_TEXTURE_2D, textureID[0])

    # glUseProgram(cube_shader)
    # glViewport(0, 0, SCR_WIDTH, SCR_HEIGHT)
    # glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    # glActiveTexture(GL_TEXTURE0)
    # glBindTexture(GL_TEXTURE_2D, textureID[0])

    # Render Scene
    pos = pyrr.matrix44.create_from_translation(pyrr.Vector3((0.0,  0.0,  0.0)))
    rot = pyrr.matrix44.create_from_axis_rotation(pyrr.Vector3((1.0, 0.3, 0.5)), 0)
    model1 = pyrr.matrix44.multiply(rot, pos)
    glUniformMatrix4fv(lightModel_loc, 1, GL_FALSE, model1)
    glBindVertexArray(cube_VAO)
    glDrawArrays(GL_TRIANGLES, 0, 36)
    glBindVertexArray(0)

    pos = pyrr.matrix44.create_from_translation(pyrr.Vector3((2.0,  2.0,  -2.0)))
    rot = pyrr.matrix44.create_from_axis_rotation(pyrr.Vector3((1.0, 0.3, 0.5)), 0.3)
    model2 = pyrr.matrix44.multiply(rot, pos)
    glUniformMatrix4fv(lightModel_loc, 1, GL_FALSE, model2)
    glBindVertexArray(cube_VAO)
    glDrawArrays(GL_TRIANGLES, 0, 36)
    glBindVertexArray(0)

    glBindFramebuffer(GL_FRAMEBUFFER, 0)

    # glUniformMatrix4fv(cube_view_loc, 1, GL_FALSE, lightView)
    # glUniformMatrix4fv(cube_projection_loc, 1, GL_FALSE, lightProjection)
    # for i, p in enumerate(cubePositions):
    #     pos = pyrr.matrix44.create_from_translation(pyrr.Vector3(p))
    #     rot = pyrr.matrix44.create_from_axis_rotation(pyrr.Vector3((1.0, 0.3, 0.5)), 0.3 * i)
    #     model = pyrr.matrix44.multiply(rot, pos)
    #     # glUniformMatrix4fv(cube_model_loc, 1, GL_FALSE, model)
    #     glUniformMatrix4fv(lightModel_loc, 1, GL_FALSE, model)
    #     glBindVertexArray(cube_VAO)
    #     glDrawArrays(GL_TRIANGLES, 0, 36)
    #     glBindVertexArray(0)
    # glBindFramebuffer(GL_FRAMEBUFFER, 0)

    # reset viewport
    glViewport(0, 0, SCR_WIDTH, SCR_HEIGHT)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # render Depth map to quad for visual debugging
    glUseProgram(screen_quad_shader)
    glActiveTexture(GL_TEXTURE0)
    glBindTexture(GL_TEXTURE_2D, depthMap)
    # render quad
    glBindVertexArray(quad_VAO)
    # glDrawArrays(GL_TRIANGLES, 0, 6)
    glDrawArrays(GL_TRIANGLE_STRIP, 0, 4)
    glBindVertexArray(0)

    glfw.swap_buffers(window)

glfw.terminate()
