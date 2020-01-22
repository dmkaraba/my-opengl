import pyrr
import numpy as np
from utils.ObjLoader import MyObjLoader


class Car:
    def __init__(self):
        self.reverse = False
        self.acceleration = 1100
        self.damping_acceleration = 500
        self.speed = 0.0
        self.max_speed = 0.2
        self.steer_strength = np.pi/45
        self.steer_angle = 0.0
        self.headVector = pyrr.Vector3((np.sin(self.steer_angle), 0, -np.cos(self.steer_angle)))
        self.position = pyrr.Vector3((0, 0, 0))
        self.upVector = pyrr.Vector3((0, 1, 0))
        self.indices, self.buffer = MyObjLoader.load_model('race_game/meshes/car.obj')
        self.texture_path = 'race_game/textures/car.png'

    def turn_left(self):
        self.steer_angle -= self.steer_strength
        self.headVector = pyrr.vector3.normalize(pyrr.Vector3((np.sin(self.steer_angle), 0, -np.cos(self.steer_angle))))

    def turn_right(self):
        self.steer_angle += self.steer_strength
        self.headVector = pyrr.vector3.normalize(pyrr.Vector3((np.sin(self.steer_angle), 0, -np.cos(self.steer_angle))))

