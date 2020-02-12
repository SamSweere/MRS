import numpy as np
import math

class Robot:
    def __init__(self, start_x, start_y, radius=20, 
                movement_speed=5, angle_speed=5):
        self.x = start_x
        self.y = start_y
        self.radius = radius
        self.movement_speed = 5 
        self.angle_speed = 5 # This is in degrees
        
        self.change_angle = 0
        self.speed = 0
        self.angle = 0 # In degrees

    def update(self):
        # Rotate the robot
        self.angle += self.change_angle * self.angle_speed

        # Convert angle in degrees to radians.
        angle_rad = math.radians(self.angle)

        # Based on the speed and the angle find the new location
        self.x += self.speed * self.movement_speed * math.cos(angle_rad)
        self.y += self.speed * self.movement_speed * math.sin(angle_rad)