import pyrr
import glfw
import numpy as np
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
from utils.Camera import Camera


WINDOW_RESOLUTION = (1280, 720)


light_vs = """
# version 330
layout(location = 0) in vec3 position;
layout(location = 1) in vec3 normal;

out vec3 Normal;
out vec3 FragPos;

uniform mat4 model;
uniform mat4 projection;
uniform mat4 view;

void main()
{
    gl_Position = projection * view * model * vec4(position, 1.0);
    FragPos = vec3(model * vec4(position, 1.0));
    Normal = mat3(transpose(inverse(model))) * normal;
}
"""

light_fs = """
# version 330
in vec3 FragPos;
in vec3 Normal;

out vec4 color;

uniform vec3 viewPos;
uniform vec3 objectColor;
uniform vec3 lightColor;
uniform vec3 lightPos;

void main()
{
    // ambient
    float ambientStrength = 0.1f;
    vec3 ambient = ambientStrength * lightColor;
    
    // diffuse
    vec3 norm = normalize(Normal);
    vec3 lightDir = normalize(lightPos - FragPos);
    float diff = max(dot(norm, lightDir), 0.0);
    vec3 diffuse = diff * lightColor;
    
    // specular
    float specularStrength = 0.5f;
    vec3 viewDir = normalize(viewPos - FragPos);
    vec3 reflectDir = reflect(-lightDir, norm);
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), 32);
    vec3 specular = specularStrength * spec * lightColor;
    
    vec3 result = (ambient + diffuse + specular) * objectColor;
    color = vec4(result, 1.0f);
}
"""

lamp_vs = """
# version 330
layout(location = 0) in vec3 position;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

void main()
{
    gl_Position = projection * view * model * vec4(position, 1.0);
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


vertices = [
    -0.5, -0.5, -0.5,  0.0,  0.0, -1.0,
    0.5,  -0.5, -0.5,  0.0,  0.0, -1.0,
    0.5,   0.5, -0.5,  0.0,  0.0, -1.0,
    0.5,   0.5, -0.5,  0.0,  0.0, -1.0,
    -0.5,  0.5, -0.5,  0.0,  0.0, -1.0,
    -0.5, -0.5, -0.5,  0.0,  0.0, -1.0,

    -0.5, -0.5,  0.5,  0.0,  0.0,  1.0,
    0.5,  -0.5,  0.5,  0.0,  0.0,  1.0,
    0.5,   0.5,  0.5,  0.0,  0.0,  1.0,
    0.5,   0.5,  0.5,  0.0,  0.0,  1.0,
    -0.5,  0.5,  0.5,  0.0,  0.0,  1.0,
    -0.5, -0.5,  0.5,  0.0,  0.0,  1.0,

    -0.5,  0.5,  0.5, -1.0,  0.0,  0.0,
    -0.5,  0.5, -0.5, -1.0,  0.0,  0.0,
    -0.5, -0.5, -0.5, -1.0,  0.0,  0.0,
    -0.5, -0.5, -0.5, -1.0,  0.0,  0.0,
    -0.5, -0.5,  0.5, -1.0,  0.0,  0.0,
    -0.5,  0.5,  0.5, -1.0,  0.0,  0.0,

    0.5,  0.5,  0.5,  1.0,  0.0,  0.0,
    0.5,  0.5, -0.5,  1.0,  0.0,  0.0,
    0.5, -0.5, -0.5,  1.0,  0.0,  0.0,
    0.5, -0.5, -0.5,  1.0,  0.0,  0.0,
    0.5, -0.5,  0.5,  1.0,  0.0,  0.0,
    0.5,  0.5,  0.5,  1.0,  0.0,  0.0,

    -0.5, -0.5, -0.5,  0.0, -1.0,  0.0,
    0.5,  -0.5, -0.5,  0.0, -1.0,  0.0,
    0.5,  -0.5,  0.5,  0.0, -1.0,  0.0,
    0.5,  -0.5,  0.5,  0.0, -1.0,  0.0,
    -0.5, -0.5,  0.5,  0.0, -1.0,  0.0,
    -0.5, -0.5, -0.5,  0.0, -1.0,  0.0,

    -0.5,  0.5, -0.5,  0.0,  1.0,  0.0,
    0.5,   0.5, -0.5,  0.0,  1.0,  0.0,
    0.5,   0.5,  0.5,  0.0,  1.0,  0.0,
    0.5,   0.5,  0.5,  0.0,  1.0,  0.0,
    -0.5,  0.5,  0.5,  0.0,  1.0,  0.0,
    -0.5,  0.5, -0.5,  0.0,  1.0,  0.0,
]


vertices = np.array(vertices, dtype=np.float32)

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

glEnableVertexAttribArray(0)
glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 4*6, ctypes.c_void_p(0))
glEnableVertexAttribArray(1)
glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 4*6, ctypes.c_void_p(12))

### LIGHT #############################
lamp_VAO = glGenVertexArrays(1)
glBindVertexArray(lamp_VAO)

lamp_VBO = glGenBuffers(1)
glBindBuffer(GL_ARRAY_BUFFER, lamp_VBO)
glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

glEnableVertexAttribArray(0)
glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 4*6, ctypes.c_void_p(0))

glClearColor(0.1, 0.1, 0.1, 1)
glEnable(GL_DEPTH_TEST)

model_loc = glGetUniformLocation(light_shader, "model")
view_loc = glGetUniformLocation(light_shader, "view")
projection_loc = glGetUniformLocation(light_shader, "projection")
object_color_loc = glGetUniformLocation(light_shader, "objectColor")
light_color_loc = glGetUniformLocation(light_shader, "lightColor")
light_pos_loc = glGetUniformLocation(light_shader, "lightPos")
view_pos_loc = glGetUniformLocation(light_shader, "viewPos")

lamp_model_loc = glGetUniformLocation(lamp_shader, "model")
lamp_view_loc = glGetUniformLocation(lamp_shader, "view")
lamp_projection_loc = glGetUniformLocation(lamp_shader, "projection")

lamp_pos_vector = pyrr.Vector3((1.2, 1.0, -2.0))
lamp_pos = pyrr.matrix44.create_from_translation(lamp_pos_vector)
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
    glUniform3f(object_color_loc, 1.0, 0.5, 0.31)
    glUniform3f(light_color_loc, 1.0, 1.0, 1.0)
    glUniform3f(light_pos_loc, *lamp_pos_vector)
    glUniform3f(view_pos_loc, *camera.position)
    glBindVertexArray(box_VAO)
    glDrawArrays(GL_TRIANGLES, 0, 36)

    glUseProgram(lamp_shader)
    glUniformMatrix4fv(lamp_view_loc, 1, GL_FALSE, view)
    glUniformMatrix4fv(lamp_projection_loc, 1, GL_FALSE, projection)
    glUniformMatrix4fv(lamp_model_loc, 1, GL_FALSE, lamp_model)
    glBindVertexArray(lamp_VAO)
    glDrawArrays(GL_TRIANGLES, 0, 36)

    glfw.swap_buffers(window)

glfw.terminate()
