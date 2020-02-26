from simulation.world import World
from simulation.robot import Robot
from simulation.line_wall import LineWall
import numpy as np

def create_rect_walls(x, y, width, height):
    bottomLeft = (x - width / 2, y - height / 2)
    topLeft = (x - width / 2, y + height / 2)
    topRight = (x + width / 2, y + height / 2)
    bottomRight= (x + width / 2, y - height / 2)
    
    return [
        LineWall(bottomLeft, topLeft),
        LineWall(topLeft, topRight),
        LineWall(topRight, bottomRight),
        LineWall(bottomRight, bottomLeft)
    ]
    
class WorldCreator:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        
    def create_rect_world(self):
        walls = create_rect_walls(self.width / 2, self.height / 2, self.width, self.height)
        robot = self.__create_randomly_placed_robot__()
        
        return World(walls, robot, self.width, self.height), robot
    
    def create_double_rect_world(self):
        outer_walls = create_rect_walls(self.width / 2, self.height / 2, self.width, self.height)
        inner_walls = create_rect_walls(self.width / 2, self.height / 2, self.width / 2, self.height / 2)
        walls = [*outer_walls, *inner_walls]
        
        robot = self.__create_randomly_placed_robot__()
        return World(walls, robot, self.width, self.height), robot
        
    def __create_randomly_placed_robot__(self):
        return Robot(self.width / 2, self.height / 2, 1.15*np.pi)