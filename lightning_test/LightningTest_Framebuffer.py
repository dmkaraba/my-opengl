import pyrr
import glfw
import numpy as np
from OpenGL.GL import *
from utils.Camera import Camera
from utils.TextureLoader import load_texture, create_2D_texture
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

quad_vectices = [
   -1.0,  1.0, 0.0, 1.0,
   -1.0, -1.0, 0.0, 0.0,
    1.0, -1.0, 1.0, 0.0,
   -1.0,  1.0, 0.0, 1.0,
    1.0, -1.0, 1.0, 0.0,
    1.0,  1.0, 1.0, 1.0
]

cube_vertices = np.array(cube_vertices, dtype=np.float32)
quad_vectices = np.array(quad_vectices, dtype=np.float32)

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
shader = ShaderLoader('lightning_test/shaders/screen_quad.vs', 'lightning_test/shaders/screen_quad.fs')
screen_quad_shader = shader.get_compiled_shader()

# ============================================================ #
#                   Loading textures                           #
# ============================================================ #
textureID = glGenTextures(2)
load_texture('lightning_test/textures/container.png', textureID[0])
load_texture('lightning_test/textures/container_specular.png', textureID[1])

# ============================================================ #
#                Framebuffer configuration                     #
# ============================================================ #
fbo = glGenFramebuffers(1)
glBindFramebuffer(GL_FRAMEBUFFER, fbo)

# Creating a texture
textureColorBuffer = glGenTextures(1)
create_2D_texture(textureColorBuffer, SCR_WIDTH, SCR_HEIGHT)
glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, textureColorBuffer, 0)

# Or creating RenderBuffer
rbo = glGenRenderbuffers(1)
glBindRenderbuffer(GL_RENDERBUFFER, rbo)
glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH24_STENCIL8, SCR_WIDTH, SCR_HEIGHT)
glBindRenderbuffer(GL_RENDERBUFFER, 0)
glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_STENCIL_ATTACHMENT, GL_RENDERBUFFER, rbo)

if glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE:
    print("ERROR::FRAMEBUFFER:: Framebuffer is not complete!")
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
#       Setup screen quad Vertex Array Object (VAO)            #
# ============================================================ #
quad_VAO = glGenVertexArrays(1)
glBindVertexArray(quad_VAO)

VBO = glGenBuffers(1)
glBindBuffer(GL_ARRAY_BUFFER, VBO)
glBufferData(GL_ARRAY_BUFFER, quad_vectices.nbytes, quad_vectices, GL_STATIC_DRAW)

glEnableVertexAttribArray(0)
glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, quad_vectices.itemsize * 4, ctypes.c_void_p(0))
glEnableVertexAttribArray(1)
glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, quad_vectices.itemsize * 4, ctypes.c_void_p(8))


cube_model_loc = glGetUniformLocation(cube_shader, "model")
cube_view_loc = glGetUniformLocation(cube_shader, "view")
cube_projection_loc = glGetUniformLocation(cube_shader, "projection")
cube_texture1_loc = glGetUniformLocation(cube_shader, "texture1")
screenTexture_loc = glGetUniformLocation(screen_quad_shader, "screenTexture")

# ============================================================ #
#                   Shader configuration                       #
# ============================================================ #
glUseProgram(cube_shader)
glUniform1i(cube_texture1_loc, 0)
glUseProgram(screen_quad_shader)
glUniform1i(screenTexture_loc, 0)

while not glfw.window_should_close(window):
    glfw.poll_events()
    move_camera(window)

    # bind to framebuffer and draw scene as we normally would to color texture
    glBindFramebuffer(GL_FRAMEBUFFER, fbo)
    glEnable(GL_DEPTH_TEST)
    glClearColor(0.1, 0.1, 0.1, 1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glUseProgram(cube_shader)
    model = pyrr.matrix44.create_from_translation(pyrr.Vector3((0, 0, 0)))
    view = camera.get_world_to_view_matrix()
    projection = pyrr.matrix44.create_perspective_projection_matrix(45, SCR_WIDTH / SCR_HEIGHT, 0.1, 100)

    glUniformMatrix4fv(cube_view_loc, 1, GL_FALSE, view)
    glUniformMatrix4fv(cube_projection_loc, 1, GL_FALSE, projection)

    glBindVertexArray(cube_VAO)
    glActiveTexture(GL_TEXTURE0)
    glBindTexture(GL_TEXTURE_2D, textureID[0])

    for i, p in enumerate(cubePositions):
        pos = pyrr.matrix44.create_from_translation(pyrr.Vector3(p))
        rot = pyrr.matrix44.create_from_axis_rotation(pyrr.Vector3((1.0, 0.3, 0.5)), 0.3 * i)
        model = pyrr.matrix44.multiply(rot, pos)
        glUniformMatrix4fv(cube_model_loc, 1, GL_FALSE, model)
        glDrawArrays(GL_TRIANGLES, 0, 36)

    # now bind back to default framebuffer and draw
    # a quad plane with the attached framebuffer color texture
    glBindFramebuffer(GL_FRAMEBUFFER, 0)
    glDisable(GL_DEPTH_TEST)
    glClearColor(1.0, 1.0, 1.0, 1.0)
    glClear(GL_COLOR_BUFFER_BIT)

    glUseProgram(screen_quad_shader)
    glBindVertexArray(quad_VAO)
    glBindTexture(GL_TEXTURE_2D, textureColorBuffer)
    glDrawArrays(GL_TRIANGLES, 0, 6)

    glfw.swap_buffers(window)

glfw.terminate()
