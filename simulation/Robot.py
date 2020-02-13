import numpy as np
import math

class Robot:
    def __init__(self, start_x, start_y, radius=20):
        self.x = start_x
        self.y = start_y
        self.radius = radius
        
        self.change_angle = 0
        self.speed = 0
        self.angle = 0 # In degrees

    def new_position(self):
        """use dem slides to get da new positions"""
        # # https://opentextbc.ca/physicstestbook2/chapter/kinematics-of-rotational-motion/
        
        # R = 1/2 * (vl + vr) / (vl - vr)

        # w = (vr -vl) / l

        # vr = w(R + l/2)
        # vl = w(R - l/2)

        # v = (vr + vl) / 2


        # ### forward kinematics
        
        vl, vr = 1, 1
        return vl, vr

    def update(self):
        # Rotate the robot
        self.angle += self.change_angle

        # Convert angle in degrees to radians.
        angle_rad = math.radians(self.angle)

        # Based on the speed and the angle find the new location
        self.x += self.speed * math.cos(angle_rad)
        self.y += self.speed * math.sin(angle_rad)