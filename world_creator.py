from simulation.world import World
from simulation.robot import Robot
from simulation.line_wall import LineWall
import numpy as np
import math

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
    
def create_trapezoid_walls(x,y, height, bottom_width, top_width):
    leftBottom = (x - bottom_width / 2, y + height / 2)
    leftTop = (x - top_width / 2, y - height / 2)
    rightBottom = (x + bottom_width / 2, y + height / 2)
    rightTop = (x + top_width / 2, y - height / 2)
    
    return [
        LineWall(leftTop, rightTop),
        LineWall(rightTop, rightBottom),
        LineWall(rightBottom, leftBottom),
        LineWall(leftBottom, leftTop)
    ]
    
def create_star_walls(x, y, inner_radius, outer_radius, num_points = 5):
    delta_angle = (math.pi * 2) / (num_points * 2)
    prev_x = x + math.cos(math.pi * 2 - delta_angle) * inner_radius
    prev_y = y + math.sin(math.pi * 2 - delta_angle) * inner_radius
    prev_radius = inner_radius
    curr_radius = outer_radius
    
    walls = []

    for i in range(num_points * 2):
        # Generate a wall
        new_x = x + math.cos(delta_angle * i) * curr_radius
        new_y = y + math.sin(delta_angle * i) * curr_radius
        
        walls.append(LineWall((prev_x, prev_y),(new_x,new_y)))
        prev_x = new_x
        prev_y = new_y
        
        # Swap the radius so we alternate between inner and outer radius
        tmp = curr_radius
        curr_radius = prev_radius
        prev_radius = tmp
        
    return walls
    
    
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
    
    def create_trapezoid_world(self):
        walls = create_trapezoid_walls(self.width / 2, self.height / 2, self.height, self.width, self.width/ 2)
        
        robot = self.__create_randomly_placed_robot__()
        return World(walls, robot, self.width, self.height), robot
    
    def create_double_trapezoid_world(self):
        outer_walls = create_trapezoid_walls(self.width / 2, self.height / 2, self.height, self.width, self.width/ 2)
        inner_walls = create_trapezoid_walls(self.width / 2, self.height / 2, self.height / 2, self.width / 2, self.width / 4)
        walls = [*outer_walls, *inner_walls]
        
        robot = self.__create_randomly_placed_robot__()
        return World(walls, robot, self.width, self.height), robot
    
    def create_star_world(self):
        walls = create_star_walls(self.width / 2, self.height / 2, self.height / 4, self.height / 2)
        
        robot = self.__create_randomly_placed_robot__()
        return World(walls, robot, self.width, self.height), robot
        
        
    def __create_randomly_placed_robot__(self):
        return Robot(self.width / 2, self.height / 2, 1.15*np.pi)