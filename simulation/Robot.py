import numpy as np

class Robot:
    def __init__(self, start_x, start_y, radius=20):
        self.x = start_x
        self.y = start_y
        self.radius = radius
        
        self.angle = 0