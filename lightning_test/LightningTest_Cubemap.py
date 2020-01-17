import pyrr
import glfw
import numpy as np
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
from utils.Camera import Camera
from utils.TextureLoader import load_texture, load_cubemap
from utils.ObjLoader import MyObjLoader

WINDOW_RESOLUTION = (1280, 720)

cube_vs = """
# version 330
layout(location = 0) in vec3 position;
layout(location = 1) in vec2 texCoords;

out vec2 TexCoords;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

void main()
{
    gl_Position = projection * view * model * vec4(position, 1.0);
    TexCoords = vec2(texCoords.s, 1.0 - texCoords.t);
}
"""

cube_fs = """
#version 330 core
in vec2 TexCoords;
out vec4 color;

uniform sampler2D texture1;

void main()
{
    color = texture(texture1, TexCoords);
}
"""

sphere_vs = """
# version 330
layout(location = 0) in vec3 position;
layout(location = 1) in vec2 texCoords;

out vec2 TexCoords;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

void main()
{
    gl_Position = projection * view * model * vec4(position, 1.0);
    TexCoords = vec2(texCoords.s, 1.0 - texCoords.t);
}
"""

sphere_fs = """
#version 330 core
in vec2 TexCoords;
out vec4 color;

uniform sampler2D texture1;

void main()
{
    color = texture(texture1, TexCoords);
}
"""

skybox_vs = """
# version 330
layout(location = 0) in vec3 position;
out vec3 TexCoords;

uniform mat4 projection;
uniform mat4 view;

void main()
{
    TexCoords = position;
    vec4 pos = projection * view * vec4(position, 1.0);
    gl_Position = pos.xyww;
}
"""

skybox_fs = """
#version 330 core
in vec3 TexCoords;
out vec4 color;

uniform samplerCube skybox;

void main()
{
    color = texture(skybox, TexCoords);
}
"""


cube_vertices = [
    -0.5, -0.5, -0.5, 0.0, 0.0,
    0.5,  -0.5, -0.5, 1.0, 0.0,
    0.5,   0.5, -0.5, 1.0, 1.0,
    0.5,   0.5, -0.5, 1.0, 1.0,
    -0.5,  0.5, -0.5, 0.0, 1.0,
    -0.5, -0.5, -0.5, 0.0, 0.0,

    -0.5, -0.5,  0.5, 0.0, 0.0,
    0.5,  -0.5,  0.5, 1.0, 0.0,
    0.5,   0.5,  0.5, 1.0, 1.0,
    0.5,   0.5,  0.5, 1.0, 1.0,
    -0.5,  0.5,  0.5, 0.0, 1.0,
    -0.5, -0.5,  0.5, 0.0, 0.0,

    -0.5,  0.5,  0.5, 1.0, 0.0,
    -0.5,  0.5, -0.5, 1.0, 1.0,
    -0.5, -0.5, -0.5, 0.0, 1.0,
    -0.5, -0.5, -0.5, 0.0, 1.0,
    -0.5, -0.5,  0.5, 0.0, 0.0,
    -0.5,  0.5,  0.5, 1.0, 0.0,

    0.5,   0.5,  0.5, 1.0, 0.0,
    0.5,   0.5, -0.5, 1.0, 1.0,
    0.5,  -0.5, -0.5, 0.0, 1.0,
    0.5,  -0.5, -0.5, 0.0, 1.0,
    0.5,  -0.5,  0.5, 0.0, 0.0,
    0.5,   0.5,  0.5, 1.0, 0.0,

    -0.5, -0.5, -0.5, 0.0, 1.0,
    0.5,  -0.5, -0.5, 1.0, 1.0,
    0.5,  -0.5,  0.5, 1.0, 0.0,
    0.5,  -0.5,  0.5, 1.0, 0.0,
    -0.5, -0.5,  0.5, 0.0, 0.0,
    -0.5, -0.5, -0.5, 0.0, 1.0,

    -0.5,  0.5, -0.5, 0.0, 1.0,
    0.5,   0.5, -0.5, 1.0, 1.0,
    0.5,   0.5,  0.5, 1.0, 0.0,
    0.5,   0.5,  0.5, 1.0, 0.0,
    -0.5,  0.5,  0.5, 0.0, 0.0,
    -0.5,  0.5, -0.5, 0.0, 1.0,
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

camera = Camera(pyrr.Vector3((0, 0, 4)))


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
    glfw.set_cursor_pos(window, WINDOW_RESOLUTION[0] / 2, WINDOW_RESOLUTION[1] / 2)


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

cube_shader = compileProgram(compileShader(cube_vs, GL_VERTEX_SHADER), compileShader(cube_fs, GL_FRAGMENT_SHADER))
skybox_shader = compileProgram(compileShader(skybox_vs, GL_VERTEX_SHADER), compileShader(skybox_fs, GL_FRAGMENT_SHADER))


# ============================================================ #
#                   Loading textures                           #
# ============================================================ #
textureID = glGenTextures(2)
load_texture('lightning_test/textures/container.png', textureID[0])

cubemap_images = [
    'lightning_test/textures/skybox1/right.tga',
    'lightning_test/textures/skybox1/left.tga',
    'lightning_test/textures/skybox1/top.tga',
    'lightning_test/textures/skybox1/bottom.tga',
    'lightning_test/textures/skybox1/back.tga',
    'lightning_test/textures/skybox1/front.tga',
]
cubemapTexture = load_cubemap(cubemap_images, textureID[1])

obj_indices, obj_buffer = MyObjLoader.load_model('lightning_test/meshes/sphere.obj')


# ============================================================ #
#             Setup OBJ file Vertex Array Object               #
# ============================================================ #
obj_VAO = glGenVertexArrays(1)
glBindVertexArray(obj_VAO)

VBO = glGenBuffers(1)
glBindBuffer(GL_ARRAY_BUFFER, VBO)
glBufferData(GL_ARRAY_BUFFER, obj_buffer.nbytes, obj_buffer, GL_STATIC_DRAW)

glEnableVertexAttribArray(0)
glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, obj_buffer.itemsize * 8, ctypes.c_void_p(0))
glEnableVertexAttribArray(1)
glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, obj_buffer.itemsize * 8, ctypes.c_void_p(12))

# ============================================================ #
#               Setup Cube Vertex Array Object                 #
# ============================================================ #
box_VAO = glGenVertexArrays(1)
glBindVertexArray(box_VAO)

VBO = glGenBuffers(1)
glBindBuffer(GL_ARRAY_BUFFER, VBO)
glBufferData(GL_ARRAY_BUFFER, cube_vertices.nbytes, cube_vertices, GL_STATIC_DRAW)

glEnableVertexAttribArray(0)
glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, cube_vertices.itemsize * 5, ctypes.c_void_p(0))
glEnableVertexAttribArray(1)
glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, cube_vertices.itemsize * 5, ctypes.c_void_p(12))


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

cube_texture_loc = glGetUniformLocation(cube_shader, "texture1")
cube_model_loc = glGetUniformLocation(cube_shader, "model")
cube_view_loc = glGetUniformLocation(cube_shader, "view")
cube_projection_loc = glGetUniformLocation(cube_shader, "projection")
material_diffuse_loc = glGetUniformLocation(cube_shader, "texture1")
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
    glUseProgram(cube_shader)
    # Bind Textures using textureIDs
    glActiveTexture(GL_TEXTURE0)
    glBindTexture(GL_TEXTURE_2D, textureID[0])
    glUniform1i(cube_texture_loc, 0)

    # Pass the matrices to the shader
    model = pyrr.matrix44.create_from_translation(pyrr.Vector3((0, 0, 0)))
    view = camera.get_world_to_view_matrix()
    glUniformMatrix4fv(cube_model_loc, 1, GL_FALSE, model)
    glUniformMatrix4fv(cube_view_loc, 1, GL_FALSE, view)
    glUniformMatrix4fv(cube_projection_loc, 1, GL_FALSE, projection)

    glBindVertexArray(box_VAO)
    glDrawArrays(GL_TRIANGLES, 0, 36)
    glBindVertexArray(0)

    # ============================================================ #
    #                       Draw an OBJ                            #
    # ============================================================ #
    model = pyrr.matrix44.create_from_translation(pyrr.Vector3((2, 0, 0)))
    view = camera.get_world_to_view_matrix()
    glUniformMatrix4fv(cube_model_loc, 1, GL_FALSE, model)
    glUniformMatrix4fv(cube_view_loc, 1, GL_FALSE, view)
    glUniformMatrix4fv(cube_projection_loc, 1, GL_FALSE, projection)
    glBindVertexArray(obj_VAO)
    glDrawArrays(GL_TRIANGLES, 0, len(obj_indices))
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
