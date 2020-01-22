import glfw
import numpy as np
import pyrr
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
from Camera import MyCamera
from ObjLoader import MyObjLoader
from TextureLoader import load_texture


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


def key_callback(window, key, scancode, action, mods):
    last_frame_time = glfw.get_time()
    if key == glfw.KEY_W:
        acceleration_input = 2
        lateral_friction_factor = 10
        backwards_friction_factor = 10

        rightVector = pyrr.vector3.cross(car.headVector, car.upVector)
        lateral_velocity = rightVector * pyrr.vector3.dot(car.velocityVector, rightVector)
        lateral_friction = -lateral_velocity * lateral_friction_factor
        backwards_friction = -car.velocityVector * backwards_friction_factor
        car.velocityVector = car.velocityVector + (backwards_friction + lateral_friction) * (glfw.get_time() - last_frame_time)

        car.accelerationVector = car.headVector * acceleration_input
        car.velocityVector = car.velocityVector + car.accelerationVector * (glfw.get_time() - last_frame_time)
        car.positionVector = car.positionVector + car.velocityVector + (glfw.get_time() - last_frame_time)

    if key == glfw.KEY_S:
        acceleration_input = -2
        lateral_friction_factor = 1000
        backwards_friction_factor = 1000

        rightVector = pyrr.vector3.cross(car.headVector, car.upVector)
        lateral_velocity = rightVector * pyrr.vector3.dot(car.velocityVector, rightVector)
        lateral_friction = -lateral_velocity * lateral_friction_factor
        backwards_friction = -car.velocityVector * backwards_friction_factor
        car.velocityVector = car.velocityVector + (backwards_friction + lateral_friction) * (
                    glfw.get_time() - last_frame_time)

        car.accelerationVector = car.headVector * acceleration_input
        car.velocityVector = car.velocityVector + car.accelerationVector * (glfw.get_time() - last_frame_time)
        car.positionVector = car.positionVector + car.velocityVector + (glfw.get_time() - last_frame_time)
    if key == glfw.KEY_D:
        car.turn_right()
    if key == glfw.KEY_A:
        car.turn_left()


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
glfw.set_key_callback(window, key_callback)
glfw.set_cursor_pos_callback(window, cursor_position_callback)

glfw.make_context_current(window)


class Car:
    def __init__(self):
        self.SPEED = 0.1
        self.TURN_DELTA = np.pi/45
        self.headAngle = 0
        self.headVector = pyrr.Vector3((0, 0, -1))
        self.positionVector = pyrr.Vector3((0, 0, 0))
        self.accelerationVector = pyrr.Vector3((0, 0, 1))
        self.velocityVector = pyrr.Vector3((0, 0, 0))
        self.upVector = pyrr.Vector3((0, 1, 0))
        self.indices, self.buffer = MyObjLoader.load_model('meshes/car.obj')

    def forward(self):
        self.positionVector = self.positionVector + self.headVector * self.SPEED

    def backward(self):
        self.positionVector = self.positionVector - self.headVector * self.SPEED

    def turn_left(self):
        self.headAngle -= self.TURN_DELTA
        rot = pyrr.matrix33.create_from_y_rotation(-self.TURN_DELTA)
        self.headVector = pyrr.Vector3(pyrr.matrix33.apply_to_vector(rot, self.headVector))

    def turn_right(self):
        self.headAngle += self.TURN_DELTA
        rot = pyrr.matrix33.create_from_y_rotation(self.TURN_DELTA)
        self.headVector = pyrr.Vector3(pyrr.matrix33.apply_to_vector(rot, self.headVector))


car = Car()


shader = compileProgram(
    compileShader(vertex_src, GL_VERTEX_SHADER),
    compileShader(fragment_src, GL_FRAGMENT_SHADER)
)

texture = glGenTextures(2)
load_texture("textures/crate.jpg", texture[0])
quad_texture = load_texture("textures/uv_grid.jpg", texture[1])


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

camera = MyCamera()
camera.cameraPosition = pyrr.Vector3((0, 1, 3))

grid_scale = pyrr.matrix44.create_from_scale(pyrr.Vector3((10, 0, 25)))
projection = pyrr.matrix44.create_perspective_projection_matrix(
                45, WINDOW_RESOLUTION[0]/WINDOW_RESOLUTION[1], 0.1, 100)
glUniformMatrix4fv(projection_loc, 1, GL_FALSE, projection)


while not glfw.window_should_close(window):
    glfw.poll_events()
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

    glBindVertexArray(car_VAO)
    glBindTexture(GL_TEXTURE_2D, texture[0])
    car_pos = pyrr.matrix44.create_from_translation(car.positionVector)
    car_rot = pyrr.matrix44.create_from_y_rotation(car.headAngle)
    model = pyrr.matrix44.multiply(car_rot, car_pos)
    glUniformMatrix4fv(model_loc, 1, GL_FALSE, model)

    # set Camera
    camera.cameraPosition = car.positionVector - pyrr.vector3.normalize(car.headVector)*2 + pyrr.Vector3((0, 1, 0))
    camera.viewDirection = pyrr.vector3.normalize(car.positionVector - camera.cameraPosition)
    view = camera.get_world_to_view_matrix()
    glUniformMatrix4fv(view_loc, 1, GL_FALSE, view)

    glDrawArrays(GL_TRIANGLES, 0, len(car.indices))

    glBindVertexArray(quad_VAO)
    glBindTexture(GL_TEXTURE_2D, texture[1])
    glUniformMatrix4fv(model_loc, 1, GL_FALSE, grid_scale)
    glDrawElements(GL_TRIANGLES, len(grid_indices), GL_UNSIGNED_INT, None)

    glfw.swap_buffers(window)

glfw.terminate()
