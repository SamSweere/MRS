from .PolygonWall import PolygonWall
import numpy as np

class World:
    def __init__(self, walls, robot):
        self.walls = walls
        self.robot = robot

def create_rect_wall(x, y, width, height):
    points = np.array([
        [x - width / 2, y - height / 2],
        [x - width / 2, y + height / 2],
        [x + width / 2, y + height / 2],
        [x + width / 2, y - height / 2]
    ])
    return PolygonWall(points)