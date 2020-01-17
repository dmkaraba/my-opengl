import pyrr
import glfw
import numpy as np
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
from utils.Camera import Camera
from utils.TextureLoader import load_texture

# https://github.com/SonarSystems/Modern-OpenGL-Tutorials/tree/master/%5BLIGHTING%5D/%5B14%5D%20Combining%20Directional%2C%20Point%20and%20Spot%20Lights

WINDOW_RESOLUTION = (1280, 720)


light_vs = """
# version 330
layout(location = 0) in vec3 position;
layout(location = 1) in vec3 normal;
layout(location = 2) in vec2 texCoords;

out vec3 Normal;
out vec3 FragPos;
out vec2 TexCoords;

uniform mat4 model;
uniform mat4 projection;
uniform mat4 view;

void main()
{
    gl_Position = projection * view * model * vec4(position, 1.0);
    FragPos = vec3(model * vec4(position, 1.0));
    Normal = mat3(transpose(inverse(model))) * normal;
    TexCoords = texCoords;
}
"""

light_fs = """
#version 330 core

#define NUMBER_OF_POINT_LIGHTS 4

struct Material
{
    sampler2D diffuse;
    sampler2D specular;
    float     shininess;
};

struct DirLight
{
    vec3 direction;

    vec3 ambient;
    vec3 diffuse;
    vec3 specular;
};

struct PointLight
{
    vec3 position;
    
    vec3 ambient;
    vec3 diffuse;
    vec3 specular;
    
    float constant;
    float linear;
    float quadratic;
};

struct SpotLight
{
    vec3 position;
    vec3 direction;
    float cutOff;
    float outerCutOff;
    
    float constant;
    float linear;
    float quadratic;
    
    vec3 ambient;
    vec3 diffuse;
    vec3 specular;
};

in vec3 FragPos;
in vec3 Normal;
in vec2 TexCoords;

out vec4 color;

uniform vec3 viewPos;
uniform Material material;
uniform DirLight dirLight;
uniform SpotLight spotLight;
uniform PointLight pointLights[NUMBER_OF_POINT_LIGHTS];

vec3 CalcDirLight(DirLight light, vec3 normal, vec3 viewDir);
vec3 CalcPointLight(PointLight light, vec3 normal, vec3 fragPos, vec3 viewDir);
vec3 CalcSpotLight(SpotLight light, vec3 normal, vec3 fragPos, vec3 viewDir);

void main()
{
    vec3 norm = normalize(Normal);
    vec3 viewDir = normalize(viewPos - FragPos);
    
    vec3 result = CalcDirLight(dirLight, norm, viewDir);
    
    for (int i=0; i < NUMBER_OF_POINT_LIGHTS; i++)
    {
        result += CalcPointLight(pointLights[i], norm, FragPos, viewDir);
    }
    
    result += CalcSpotLight(spotLight, norm, FragPos, viewDir);
    
    color = vec4(result, 1.0);
}

vec3 CalcDirLight(DirLight light, vec3 normal, vec3 viewDir)
{   
    vec3 lightDir = normalize(-light.direction);
    float diff = max(dot(normal, lightDir), 0.0);
    
    vec3 reflectDir = reflect(-lightDir, normal);
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), material.shininess);
    
    vec3 ambient = light.ambient * vec3(texture(material.diffuse, TexCoords));
    vec3 diffuse = light.diffuse * diff * vec3(texture(material.diffuse, TexCoords));
    vec3 specular = light.specular * spec * vec3(texture(material.specular, TexCoords));
    
    return (ambient + diffuse + specular);
}

vec3 CalcPointLight(PointLight light, vec3 normal, vec3 fragPos, vec3 viewDir)
{
    vec3 lightDir = normalize(light.position - fragPos);
    float diff = max(dot(normal, lightDir), 0.0);
    
    vec3 reflectDir = reflect(-lightDir, normal);
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), material.shininess);
    
    float distance = length(light.position - FragPos);
    float attenuation = 1.0f / (light.constant + light.linear * distance + light.quadratic * (distance * distance));
    
    vec3 ambient = light.ambient * vec3(texture(material.diffuse, TexCoords));
    vec3 diffuse = light.diffuse * diff * vec3(texture(material.diffuse, TexCoords));
    vec3 specular = light.specular * spec * vec3(texture(material.specular, TexCoords));
    
    ambient *= attenuation;
    diffuse *= attenuation;
    specular *= attenuation;

    return (ambient + diffuse + specular);
}

vec3 CalcSpotLight(SpotLight light, vec3 normal, vec3 fragPos, vec3 viewDir)
{
    vec3 lightDir = normalize(light.position - fragPos);
    float diff = max(dot(normal, lightDir), 0.0);
    
    vec3 reflectDir = reflect(-lightDir, normal);
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), material.shininess);
    
    float distance = length(light.position - FragPos);
    float attenuation = 1.0f / (light.constant + light.linear * distance + light.quadratic * (distance * distance));
    
    float theta = dot(lightDir, normalize(-light.direction));
    float epsilon = (light.cutOff - light.outerCutOff);
    float intensity = clamp((theta - light.outerCutOff) / epsilon, 0.0, 1.0);

    vec3 ambient = light.ambient * vec3(texture(material.diffuse, TexCoords));
    vec3 diffuse = light.diffuse * diff * vec3(texture(material.diffuse, TexCoords));
    vec3 specular = light.specular * spec * vec3(texture(material.specular, TexCoords));
    
    ambient *= attenuation * intensity;
    diffuse *= attenuation * intensity;
    specular *= attenuation * intensity;

    return (ambient + diffuse + specular);
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
    -0.5, -0.5, -0.5,  0.0,  0.0, -1.0, 0.0, 0.0,
    0.5,  -0.5, -0.5,  0.0,  0.0, -1.0, 1.0, 0.0,
    0.5,   0.5, -0.5,  0.0,  0.0, -1.0, 1.0, 1.0,
    0.5,   0.5, -0.5,  0.0,  0.0, -1.0, 1.0, 1.0,
    -0.5,  0.5, -0.5,  0.0,  0.0, -1.0, 0.0, 1.0,
    -0.5, -0.5, -0.5,  0.0,  0.0, -1.0, 0.0, 0.0,

    -0.5, -0.5,  0.5,  0.0,  0.0,  1.0, 0.0, 0.0,
    0.5,  -0.5,  0.5,  0.0,  0.0,  1.0, 1.0, 0.0,
    0.5,   0.5,  0.5,  0.0,  0.0,  1.0, 1.0, 1.0,
    0.5,   0.5,  0.5,  0.0,  0.0,  1.0, 1.0, 1.0,
    -0.5,  0.5,  0.5,  0.0,  0.0,  1.0, 0.0, 1.0,
    -0.5, -0.5,  0.5,  0.0,  0.0,  1.0, 0.0, 0.0,

    -0.5,  0.5,  0.5, -1.0,  0.0,  0.0, 1.0, 0.0,
    -0.5,  0.5, -0.5, -1.0,  0.0,  0.0, 1.0, 1.0,
    -0.5, -0.5, -0.5, -1.0,  0.0,  0.0, 0.0, 1.0,
    -0.5, -0.5, -0.5, -1.0,  0.0,  0.0, 0.0, 1.0,
    -0.5, -0.5,  0.5, -1.0,  0.0,  0.0, 0.0, 0.0,
    -0.5,  0.5,  0.5, -1.0,  0.0,  0.0, 1.0, 0.0,

    0.5,   0.5,  0.5,  1.0,  0.0,  0.0, 1.0, 0.0,
    0.5,   0.5, -0.5,  1.0,  0.0,  0.0, 1.0, 1.0,
    0.5,  -0.5, -0.5,  1.0,  0.0,  0.0, 0.0, 1.0,
    0.5,  -0.5, -0.5,  1.0,  0.0,  0.0, 0.0, 1.0,
    0.5,  -0.5,  0.5,  1.0,  0.0,  0.0, 0.0, 0.0,
    0.5,   0.5,  0.5,  1.0,  0.0,  0.0, 1.0, 0.0,

    -0.5, -0.5, -0.5,  0.0, -1.0,  0.0, 0.0, 1.0,
    0.5,  -0.5, -0.5,  0.0, -1.0,  0.0, 1.0, 1.0,
    0.5,  -0.5,  0.5,  0.0, -1.0,  0.0, 1.0, 0.0,
    0.5,  -0.5,  0.5,  0.0, -1.0,  0.0, 1.0, 0.0,
    -0.5, -0.5,  0.5,  0.0, -1.0,  0.0, 0.0, 0.0,
    -0.5, -0.5, -0.5,  0.0, -1.0,  0.0, 0.0, 1.0,

    -0.5,  0.5, -0.5,  0.0,  1.0,  0.0, 0.0, 1.0,
    0.5,   0.5, -0.5,  0.0,  1.0,  0.0, 1.0, 1.0,
    0.5,   0.5,  0.5,  0.0,  1.0,  0.0, 1.0, 0.0,
    0.5,   0.5,  0.5,  0.0,  1.0,  0.0, 1.0, 0.0,
    -0.5,  0.5,  0.5,  0.0,  1.0,  0.0, 0.0, 0.0,
    -0.5,  0.5, -0.5,  0.0,  1.0,  0.0, 0.0, 1.0,
]

cubePositions = [
    pyrr.Vector3((2.0,  5.0,  -15.0)),
    pyrr.Vector3((-1.5, -2.2, -2.5)),
    pyrr.Vector3((-3.8, -2.0, -12.3)),
    pyrr.Vector3((2.4,  -0.4,  2.5)),
    pyrr.Vector3((0.0,  0.0,   0.0)),
    pyrr.Vector3((-1.7, 3.0,  -7.5)),
    pyrr.Vector3((1.3,  -2.0, -2.5)),
    pyrr.Vector3((1.5,  2.0,  -2.5)),
    pyrr.Vector3((1.5,  0.2,  -1.5)),
    pyrr.Vector3((-1.3, 1.0,  -1.0))
]

pointLightPositions = [
    pyrr.Vector3((0.5, -0.4, 0.2)),
    pyrr.Vector3((2.3, -3.3, -4.0)),
    pyrr.Vector3((-4.0, 2.0, -12.0)),
    pyrr.Vector3((0.0, 0.0, -3.0))
]

vertices = np.array(vertices, dtype=np.float32)

camera = Camera(pos=pyrr.Vector3((0, 0, 2)))


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

texture = glGenTextures(2)
load_texture('lightning_test/textures/container.png', texture[0])
load_texture('lightning_test/textures/container_specular.png', texture[1])

### BOX ###############################
box_VAO = glGenVertexArrays(1)
glBindVertexArray(box_VAO)

VBO = glGenBuffers(1)
glBindBuffer(GL_ARRAY_BUFFER, VBO)
glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

glEnableVertexAttribArray(0)
glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, vertices.itemsize * 8, ctypes.c_void_p(0))
glEnableVertexAttribArray(1)
glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, vertices.itemsize * 8, ctypes.c_void_p(12))
glEnableVertexAttribArray(2)
glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, vertices.itemsize * 8, ctypes.c_void_p(24))

### LAMP ##############################
lamp_VAO = glGenVertexArrays(1)
glBindVertexArray(lamp_VAO)

lamp_VBO = glGenBuffers(1)
glBindBuffer(GL_ARRAY_BUFFER, lamp_VBO)
glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

glEnableVertexAttribArray(0)
glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, vertices.itemsize * 8, ctypes.c_void_p(0))

glClearColor(0.1, 0.1, 0.1, 1)
glEnable(GL_DEPTH_TEST)

model_loc = glGetUniformLocation(light_shader, "model")
view_loc = glGetUniformLocation(light_shader, "view")
projection_loc = glGetUniformLocation(light_shader, "projection")
view_pos_loc = glGetUniformLocation(light_shader, "viewPos")

# Directional Light
dirLight_direction_loc = glGetUniformLocation(light_shader, "dirLight.direction")
dirLight_ambient_loc = glGetUniformLocation(light_shader, "dirLight.ambient")
dirLight_diffuse_loc = glGetUniformLocation(light_shader, "dirLight.diffuse")
dirLight_specular_loc = glGetUniformLocation(light_shader, "dirLight.specular")

# Point Light
pointLight_position_loc = list()
pointLight_ambient_loc = list()
pointLight_diffuse_loc = list()
pointLight_specular_loc = list()
pointLight_constant_loc = list()
pointLight_linear_loc = list()
pointLight_quadratic_loc = list()
for i in range(len(pointLightPositions)):
    pointLight_position_loc.append(glGetUniformLocation(light_shader,  f"pointLights[{str(i)}].position"))
    pointLight_ambient_loc.append(glGetUniformLocation(light_shader,   f"pointLights[{str(i)}].ambient"))
    pointLight_diffuse_loc.append(glGetUniformLocation(light_shader,   f"pointLights[{str(i)}].diffuse"))
    pointLight_specular_loc.append(glGetUniformLocation(light_shader,  f"pointLights[{str(i)}].specular"))
    pointLight_constant_loc.append(glGetUniformLocation(light_shader,  f"pointLights[{str(i)}].constant"))
    pointLight_linear_loc.append(glGetUniformLocation(light_shader,    f"pointLights[{str(i)}].linear"))
    pointLight_quadratic_loc.append(glGetUniformLocation(light_shader, f"pointLights[{str(i)}].quadratic"))

# Spot Light
spotLight_position_loc = glGetUniformLocation(light_shader, "spotLight.position")
spotLight_direction_loc = glGetUniformLocation(light_shader, "spotLight.direction")
spotLight_cutOff_loc = glGetUniformLocation(light_shader, "spotLight.cutOff")
spotLight_outerCutOff_loc = glGetUniformLocation(light_shader, "spotLight.outerCutOff")
spotLight_constant_loc = glGetUniformLocation(light_shader, "spotLight.constant")
spotLight_linear_loc = glGetUniformLocation(light_shader, "spotLight.linear")
spotLight_quadratic_loc = glGetUniformLocation(light_shader, "spotLight.quadratic")
spotLight_ambient_loc = glGetUniformLocation(light_shader, "spotLight.ambient")
spotLight_diffuse_loc = glGetUniformLocation(light_shader, "spotLight.diffuse")
spotLight_specular_loc = glGetUniformLocation(light_shader, "spotLight.specular")

# Material
material_diffuse_loc = glGetUniformLocation(light_shader, "material.diffuse")
material_specular_loc = glGetUniformLocation(light_shader, "material.specular")
material_shininess_loc = glGetUniformLocation(light_shader, "material.shininess")

# LAMP
lamp_model_loc = glGetUniformLocation(lamp_shader, "model")
lamp_view_loc = glGetUniformLocation(lamp_shader, "view")
lamp_projection_loc = glGetUniformLocation(lamp_shader, "projection")

lamp_pos = pyrr.matrix44.create_from_translation(pyrr.Vector3((1.2, 1.0, -2.0)))
lamp_scale = pyrr.matrix44.create_from_scale(pyrr.Vector3((0.1, 0.1, 0.1)))
lamp_model = pyrr.matrix44.multiply(lamp_scale, lamp_pos)

projection = pyrr.matrix44.create_perspective_projection_matrix(
                45, WINDOW_RESOLUTION[0]/WINDOW_RESOLUTION[1], 0.1, 100)

glUseProgram(light_shader)

# setting material textures
glUniform1i(material_diffuse_loc,  0)
glUniform1i(material_specular_loc, 1)

while not glfw.window_should_close(window):
    glfw.poll_events()
    move_camera(window)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glUseProgram(light_shader)
    view = camera.get_world_to_view_matrix()

    ### LIGHT #############################
    glUniformMatrix4fv(view_loc, 1, GL_FALSE, view)
    glUniformMatrix4fv(projection_loc, 1, GL_FALSE, projection)
    glUniform3f(view_pos_loc, *camera.position)

    # ============================================================ #
    # Here we set all the uniforms for all types of lights we have #
    # ============================================================ #
    # setting dirLight
    glUniform3f(dirLight_direction_loc, -0.2, -1.0, -0.3)
    glUniform3f(dirLight_ambient_loc, 0.05, 0.05, 0.05)
    glUniform3f(dirLight_diffuse_loc, 1.0, 1.0, 0.8)
    glUniform3f(dirLight_specular_loc, 0.5, 0.5, 0.5)

    # setting pointLight
    for i, p in enumerate(pointLightPositions):
        glUniform3f(pointLight_position_loc[i], *p)
        glUniform3f(pointLight_ambient_loc[i], 0.05, 0.05, 0.05)
        glUniform3f(pointLight_diffuse_loc[i], 0.8, 0.8, 0.8)
        glUniform3f(pointLight_specular_loc[i], 1.0, 1.0, 1.0)
        glUniform1f(pointLight_constant_loc[i], 1)
        glUniform1f(pointLight_linear_loc[i], 0.14)
        glUniform1f(pointLight_quadratic_loc[i], 0.07)

    # setting spot light
    glUniform3f(spotLight_position_loc, *camera.position)
    glUniform3f(spotLight_direction_loc, *camera.front)
    glUniform1f(spotLight_cutOff_loc, np.cos(np.radians(17)))
    glUniform1f(spotLight_outerCutOff_loc, np.cos(np.radians(18)))
    glUniform1f(spotLight_constant_loc, 1)
    glUniform1f(spotLight_linear_loc, 0.09)
    glUniform1f(spotLight_quadratic_loc, 0.032)
    glUniform3f(spotLight_ambient_loc, 0.1, 0.1, 0.1)
    glUniform3f(spotLight_diffuse_loc, 0.8, 0.8, 0.8)
    glUniform3f(spotLight_specular_loc, 1.0, 1.0, 1.0)

    # setting material
    glUniform1f(material_shininess_loc, 32.0)

    # Bind diffuse map
    glActiveTexture(GL_TEXTURE0)
    glBindTexture(GL_TEXTURE_2D, texture[0])
    # Bind specular map
    glActiveTexture(GL_TEXTURE1)
    glBindTexture(GL_TEXTURE_2D, texture[1])

    glBindVertexArray(box_VAO)
    # Draw 10 containers with the same VAO and VBO information; only their world space coordinates differ
    for i, p in enumerate(cubePositions):
        pos = pyrr.matrix44.create_from_translation(p)
        rot = pyrr.matrix44.create_from_axis_rotation(pyrr.Vector3((1.0, 0.3, 0.5)), 0.3 * i)
        model = pyrr.matrix44.multiply(rot, pos)
        glUniformMatrix4fv(model_loc, 1, GL_FALSE, model)
        glDrawArrays(GL_TRIANGLES, 0, 36)
    glBindVertexArray(0)

    # Also draw the lamp object, again binding the appropriate shader
    glUseProgram(lamp_shader)
    glBindVertexArray(lamp_VAO)

    # We now draw as many light bulbs as we have point lights.
    for p in pointLightPositions:
        lamp_pos = pyrr.matrix44.create_from_translation(p)
        lamp_scale = pyrr.matrix44.create_from_scale(pyrr.Vector3((0.1, 0.1, 0.1)))
        lamp_model = pyrr.matrix44.multiply(lamp_scale, lamp_pos)
        glUniformMatrix4fv(lamp_model_loc, 1, GL_FALSE, lamp_model)
        glUniformMatrix4fv(lamp_view_loc, 1, GL_FALSE, view)
        glUniformMatrix4fv(lamp_projection_loc, 1, GL_FALSE, projection)
        glDrawArrays(GL_TRIANGLES, 0, 36)
    glBindVertexArray(0)

    glfw.swap_buffers(window)

glfw.terminate()
