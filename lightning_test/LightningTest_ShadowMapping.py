import glfw
from OpenGL.GL import *
import numpy as np
import pyrr
from utils.Camera import Camera
from utils.Shader import ShaderLoader
from utils.TextureLoader import load_texture, create_2D_texture_depth


SCR_WIDTH = 1280
SCR_HEIGHT = 720

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

plane_vertices = [
    -10.0, 0.0,  10.0, 0.0, 0.0,
    -10.0, 0.0, -10.0, 0.0, 2.0,
     10.0, 0.0,  10.0, 2.0, 0.0,
     10.0, 0.0,  10.0, 2.0, 0.0,
    -10.0, 0.0, -10.0, 0.0, 2.0,
     10.0, 0.0, -10.0, 2.0, 2.0
]
plane_vertices = np.array(plane_vertices, dtype=np.float32)

cubePositions = [
    (0.0,  0.0,  0.0),
    (2.0,  5.0,  -15.0),
    (-1.5, -2.2, -2.5),
    # (-3.8, -2.0, -12.3),
    (2.4,  -0.4, 2.5),
    (-1.7, 3.0,  -7.5),
    (1.3,  -2.0, -2.5),
    (1.5,  2.0,  -2.5),
    (1.5,  0.2,  -1.5),
    (-1.3, 1.0,  -1.0),
]

shader = ShaderLoader('lightning_test/shaders/cube.vs', 'lightning_test/shaders/cube.fs')
cube_shader = shader.get_compiled_shader()
shader = ShaderLoader('lightning_test/shaders/simple_depth.vs', 'lightning_test/shaders/simple_depth.fs')
simple_depth_shader = shader.get_compiled_shader()
shader = ShaderLoader('lightning_test/shaders/screen_quad.vs', 'lightning_test/shaders/screen_quad.fs')
debug_depth_quad_shader = shader.get_compiled_shader()

# load textures
textureID = glGenTextures(2)
load_texture('lightning_test/textures/container.png', textureID[0])


def render_cube(cube_vao=None):
    # initialize cube if necessary
    if not cube_vao:
        vertices = [
            -0.5, -0.5, -0.5, 0.0, 0.0, 0.0, 0.0, -1.0,
            0.5, -0.5, -0.5, 1.0, 0.0, 0.0, 0.0, -1.0,
            0.5, 0.5, -0.5, 1.0, 1.0, 0.0, 0.0, -1.0,
            0.5, 0.5, -0.5, 1.0, 1.0, 0.0, 0.0, -1.0,
            -0.5, 0.5, -0.5, 0.0, 1.0, 0.0, 0.0, -1.0,
            -0.5, -0.5, -0.5, 0.0, 0.0, 0.0, 0.0, -1.0,

            -0.5, -0.5, 0.5, 0.0, 0.0, 0.0, 0.0, 1.0,
            0.5, -0.5, 0.5, 1.0, 0.0, 0.0, 0.0, 1.0,
            0.5, 0.5, 0.5, 1.0, 1.0, 0.0, 0.0, 1.0,
            0.5, 0.5, 0.5, 1.0, 1.0, 0.0, 0.0, 1.0,
            -0.5, 0.5, 0.5, 0.0, 1.0, 0.0, 0.0, 1.0,
            -0.5, -0.5, 0.5, 0.0, 0.0, 0.0, 0.0, 1.0,

            -0.5, 0.5, 0.5, 1.0, 0.0, -1.0, 0.0, 0.0,
            -0.5, 0.5, -0.5, 1.0, 1.0, -1.0, 0.0, 0.0,
            -0.5, -0.5, -0.5, 0.0, 1.0, -1.0, 0.0, 0.0,
            -0.5, -0.5, -0.5, 0.0, 1.0, -1.0, 0.0, 0.0,
            -0.5, -0.5, 0.5, 0.0, 0.0, -1.0, 0.0, 0.0,
            -0.5, 0.5, 0.5, 1.0, 0.0, -1.0, 0.0, 0.0,

            0.5, 0.5, 0.5, 1.0, 0.0, 1.0, 0.0, 0.0,
            0.5, 0.5, -0.5, 1.0, 1.0, 1.0, 0.0, 0.0,
            0.5, -0.5, -0.5, 0.0, 1.0, 1.0, 0.0, 0.0,
            0.5, -0.5, -0.5, 0.0, 1.0, 1.0, 0.0, 0.0,
            0.5, -0.5, 0.5, 0.0, 0.0, 1.0, 0.0, 0.0,
            0.5, 0.5, 0.5, 1.0, 0.0, 1.0, 0.0, 0.0,

            -0.5, -0.5, -0.5, 0.0, 1.0, 0.0, -1.0, 0.0,
            0.5, -0.5, -0.5, 1.0, 1.0, 0.0, -1.0, 0.0,
            0.5, -0.5, 0.5, 1.0, 0.0, 0.0, -1.0, 0.0,
            0.5, -0.5, 0.5, 1.0, 0.0, 0.0, -1.0, 0.0,
            -0.5, -0.5, 0.5, 0.0, 0.0, 0.0, -1.0, 0.0,
            -0.5, -0.5, -0.5, 0.0, 1.0, 0.0, -1.0, 0.0,

            -0.5, 0.5, -0.5, 0.0, 1.0, 0.0, 1.0, 0.0,
            0.5, 0.5, -0.5, 1.0, 1.0, 0.0, 1.0, 0.0,
            0.5, 0.5, 0.5, 1.0, 0.0, 0.0, 1.0, 0.0,
            0.5, 0.5, 0.5, 1.0, 0.0, 0.0, 1.0, 0.0,
            -0.5, 0.5, 0.5, 0.0, 0.0, 0.0, 1.0, 0.0,
            -0.5, 0.5, -0.5, 0.0, 1.0, 0.0, 1.0, 0.0,
        ]
        vertices = np.array(vertices, dtype=np.float32)

        cube_vao = glGenVertexArrays(1)
        cube_vbo = glGenBuffers(1)
        # fill buffer
        glBindBuffer(GL_ARRAY_BUFFER, cube_vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
        # link vertex attributes
        glBindVertexArray(cube_vao)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, vertices.itemsize * 8, ctypes.c_void_p(0))
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, vertices.itemsize * 8, ctypes.c_void_p(12))
        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, vertices.itemsize * 8, ctypes.c_void_p(20))
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

    # render Cube
    glBindVertexArray(cube_vao)
    glDrawArrays(GL_TRIANGLES, 0, 36)
    glBindVertexArray(0)


def render_quad(quad_vao=None):
    # initialize cube if necessary
    if not quad_vao:
        vertices = [
            -1.0,  1.0, 0.0, 0.0, 1.0,
            -1.0, -1.0, 0.0, 0.0, 0.0,
             1.0,  1.0, 0.0, 1.0, 1.0,
             1.0, -1.0, 0.0, 1.0, 0.0,
        ]
        vertices = np.array(vertices, dtype=np.float32)

        quad_vao = glGenVertexArrays(1)
        quad_vbo = glGenBuffers(1)
        # fill buffer
        glBindBuffer(GL_ARRAY_BUFFER, quad_vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
        # link vertex attributes
        glBindVertexArray(quad_vao)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, vertices.itemsize * 5, ctypes.c_void_p(0))
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, vertices.itemsize * 5, ctypes.c_void_p(12))
        # glBindBuffer(GL_ARRAY_BUFFER, 0)
        # glBindVertexArray(0)

    # render Quad
    glBindVertexArray(quad_vao)
    glDrawArrays(GL_TRIANGLE_STRIP, 0, 4)
    glBindVertexArray(0)


# ============================================================ #
#                  configure depth map FBO                     #
# ============================================================ #
SHADOW_WIDTH = 1024
SHADOW_HEIGHT = 1024
depthMapFBO = glGenFramebuffers(1)
# create depth texture
depthMap = glGenTextures(1)
glBindTexture(GL_TEXTURE_2D, depthMap)
glTexImage2D(GL_TEXTURE_2D, 0, GL_DEPTH_COMPONENT, SHADOW_WIDTH, SHADOW_HEIGHT, 0, GL_DEPTH_COMPONENT, GL_FLOAT, None)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
# attach depth texture as FBO's depth buffer
glBindFramebuffer(GL_FRAMEBUFFER, depthMapFBO)
glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_TEXTURE_2D, depthMap, 0)
glDrawBuffer(GL_NONE)
glReadBuffer(GL_NONE)
glBindFramebuffer(GL_FRAMEBUFFER, 0)

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


glUseProgram(cube_shader)
glClearColor(0, 0.1, 0.1, 1)   # DO WE NEED IT ???
glEnable(GL_DEPTH_TEST)

cube_model_loc = glGetUniformLocation(cube_shader, 'model')
cube_view_loc = glGetUniformLocation(cube_shader, 'view')
cube_projection_loc = glGetUniformLocation(cube_shader, 'projection')
cube_lightSpaceMatrix_loc = glGetUniformLocation(cube_shader, 'lightSpaceMatrix')
cube_diffuseTexture_loc = glGetUniformLocation(cube_shader, 'diffuseTexture')
cube_shadowMap_loc = glGetUniformLocation(cube_shader, 'shadowMap')
cube_lightPos_loc = glGetUniformLocation(cube_shader, 'lightPos')
cube_viewPos_loc = glGetUniformLocation(cube_shader, 'viewPos')
light_model_loc = glGetUniformLocation(simple_depth_shader, 'model')
light_spaceMatrix_loc = glGetUniformLocation(simple_depth_shader, 'lightSpaceMatrix')
debugPlane_screenTexture_loc = glGetUniformLocation(debug_depth_quad_shader, 'screenTexture')

glUseProgram(cube_shader)
glUniform1i(cube_diffuseTexture_loc, 0)
glUniform1i(cube_shadowMap_loc, 1)
glUseProgram(debug_depth_quad_shader)
glUniform1i(debugPlane_screenTexture_loc, 0)

light_pos = pyrr.Vector3((-2.0, 4.0, -1.0))

while not glfw.window_should_close(window):
    # 1. render depth of scene to texture (from light's perspective)
    lightProjection = pyrr.matrix44.create_orthogonal_projection(-10.0, 10.0, -10.0, 10.0, 1.0, 7.5)
    lightView = pyrr.matrix44.create_look_at(
        light_pos, pyrr.Vector3((0.0, 0.0, 0.0)), pyrr.Vector3((0.0, 1.0, 0.0)))
    lightSpaceMatrix = pyrr.matrix44.multiply(lightView, lightProjection)
    # render scene from light's point of view
    glUseProgram(simple_depth_shader)
    glUniformMatrix4fv(light_spaceMatrix_loc, 1, GL_FALSE, lightSpaceMatrix)

    glViewport(0, 0, SHADOW_WIDTH, SHADOW_HEIGHT)
    glBindFramebuffer(GL_FRAMEBUFFER, depthMapFBO)
    glClear(GL_DEPTH_BUFFER_BIT)
    glActiveTexture(GL_TEXTURE0)
    glBindTexture(GL_TEXTURE_2D, textureID[0])

    # render_scene()
    # floor
    glBindVertexArray(plane_VAO)
    model = pyrr.matrix44.create_from_translation(pyrr.Vector3((0, -5, 0)))
    glUniformMatrix4fv(light_model_loc, 1, GL_FALSE, model)
    glDrawArrays(GL_TRIANGLES, 0, 6)
    # cubes
    for i, p in enumerate(cubePositions):
        pos = pyrr.matrix44.create_from_translation(pyrr.Vector3(p))
        rot = pyrr.matrix44.create_from_axis_rotation(pyrr.Vector3((1.0, 0.3, 0.5)), 0.3 * i)
        model = pyrr.matrix44.multiply(rot, pos)
        glUniformMatrix4fv(light_model_loc, 1, GL_FALSE, model)
        render_cube()
    # end of render_scene()

    glBindFramebuffer(GL_FRAMEBUFFER, 0)

    # reset viewport
    glViewport(0, 0, SCR_WIDTH, SCR_HEIGHT)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    # 2. render scene as normal using the generated depth/shadow map
    glUseProgram(cube_shader)
    view = camera.get_world_to_view_matrix()
    projection = pyrr.matrix44.create_perspective_projection_matrix(45, SCR_WIDTH / SCR_HEIGHT, 0.1, 100)
    glUniformMatrix4fv(cube_model_loc, 1, GL_FALSE, view)
    glUniformMatrix4fv(cube_projection_loc, 1, GL_FALSE, projection)
    # set light uniforms
    glUniform3fv(cube_viewPos_loc, 1, GL_FALSE, pyrr.Vector3(camera.position))
    glUniform3fv(cube_lightPos_loc, 1, GL_FALSE, light_pos)
    glUniformMatrix4fv(cube_lightSpaceMatrix_loc, 1, GL_FALSE, lightSpaceMatrix)
    glActiveTexture(GL_TEXTURE0)
    glBindTexture(GL_TEXTURE_2D, textureID[0])
    glActiveTexture(GL_TEXTURE1)
    glBindTexture(GL_TEXTURE_2D, depthMap)

    # render_scene()
    # floor
    glBindVertexArray(plane_VAO)
    model = pyrr.matrix44.create_from_translation(pyrr.Vector3((0, -5, 0)))
    glUniformMatrix4fv(cube_model_loc, 1, GL_FALSE, model)
    glDrawArrays(GL_TRIANGLES, 0, 6)
    # cubes
    for i, p in enumerate(cubePositions):
        pos = pyrr.matrix44.create_from_translation(pyrr.Vector3(p))
        rot = pyrr.matrix44.create_from_axis_rotation(pyrr.Vector3((1.0, 0.3, 0.5)), 0.3 * i)
        model = pyrr.matrix44.multiply(rot, pos)
        glUniformMatrix4fv(cube_model_loc, 1, GL_FALSE, model)
        render_cube()
    # end of render_scene()

    # render Depth map to quad for visual debugging
    glUseProgram(debug_depth_quad_shader)
    glActiveTexture(GL_TEXTURE0)
    glBindTexture(GL_TEXTURE_2D, depthMap)
    render_quad()

    # glfw: swap buffers and poll IO events (keys pressed/released, mouse moved etc.)
    glfw.swap_buffers(window)
    glfw.poll_events()

glfw.terminate()
