import pyrr
import numpy as np


class Camera:
    def __init__(self, pos=pyrr.Vector3((0.0, 0.0, 0.0))):
        self.SENSITIVITY = 0.5
        self.SPEED = 0.15
        self.position = pos
        self.front = pyrr.Vector3((0, 0, -1))
        self.up = pyrr.Vector3((0, 1, 0))
        # self.old_mouse_position = np.array([1280/2, 720/2])
        self.upVector = pyrr.Vector3((0, 1, 0))
        self.strafeDirection = pyrr.Vector3((1, 0, 0))
        self.first_mouth = True
        self.pitch = 0
        self.yaw = -90
        self.lastX = 0
        self.lastY = 0

    def get_world_to_view_matrix(self):  # eye, target, up
        return pyrr.matrix44.create_look_at(
            self.position,
            self.position + self.front,
            self.upVector
        )

    def mouth_update(self, xpos, ypos):
        """
        self.strafeDirection = pyrr.vector3.normalise(np.cross(self.front, self.upVector))
        x_delta, y_delta = (new_mouse_position - np.array([1280 / 2, 720 / 2])) * self.ROTATIONAL_SPEED
        rx = R.from_rotvec(-y_delta * self.strafeDirection)
        ry = R.from_rotvec(-x_delta * self.upVector)
        self.front = pyrr.Vector3(ry.apply(rx.apply(self.front)))
        self.old_mouse_position = new_mouse_position
        """

        if self.first_mouth:
            self.lastX = xpos
            self.lastY = ypos
            self.first_mouth = False
        x_delta = xpos - self.lastX
        y_delta = self.lastY - ypos
        self.lastX = xpos
        self.lastY = ypos
        x_delta *= self.SENSITIVITY
        y_delta *= self.SENSITIVITY

        self.yaw += x_delta
        self.pitch += y_delta

        if self.pitch > 89:
            self.pitch = 89
        if self.pitch < -89:
            self.pitch = -89

        direction = pyrr.Vector3()
        direction.x = np.cos(np.radians(self.yaw)) * np.cos(np.radians(self.pitch))
        direction.y = np.sin(np.radians(self.pitch))
        direction.z = np.sin(np.radians(self.yaw)) * np.cos(np.radians(self.pitch))
        self.front = direction

        self.strafeDirection = pyrr.Vector3(pyrr.vector3.normalise(pyrr.vector3.cross(self.up, self.front)))
        self.upVector = pyrr.Vector3(pyrr.vector3.cross(self.front, self.strafeDirection))

    def move_forward(self):
        self.position = self.position + self.SPEED * self.front

    def move_backward(self):
        self.position = self.position - self.SPEED * self.front

    def strafe_left(self):
        # self.position = self.position - self.SPEED * self.strafeDirection
        self.position = \
            self.position - pyrr.vector3.normalise(pyrr.vector3.cross(self.front, self.upVector)) * self.SPEED

    def strafe_right(self):
        # self.position = self.position + self.SPEED * self.strafeDirection
        self.position = \
            self.position + pyrr.vector3.normalise(pyrr.vector3.cross(self.front, self.upVector)) * self.SPEED

    def move_up(self):
        self.position = self.position + self.SPEED * self.upVector

    def move_down(self):
        self.position = self.position - self.SPEED * self.upVector