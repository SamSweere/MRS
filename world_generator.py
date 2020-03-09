from simulation.world import World
from simulation.robot import Robot
from simulation.line_wall import LineWall
import numpy as np
import math
import random

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
    
    
class WorldGenerator:
    def __init__(self, width, height, robot_radius, robot_kwargs):
        self.width = width
        self.height = height
        self.robot_radius = robot_radius
        self.robot_args = robot_kwargs
        
    def create_rect_world(self):
        walls = create_rect_walls(self.width / 2, self.height / 2, self.width, self.height)
        
        world = World(walls, self.width, self.height)
        robot = self.__add_random_robot__(world)
        return world, robot
    
    def create_double_rect_world(self):
        outer_walls = create_rect_walls(self.width / 2, self.height / 2, self.width, self.height)
        inner_walls = create_rect_walls(self.width / 2, self.height / 2, self.width / 2, self.height / 2)
        walls = [*outer_walls, *inner_walls]
        
        world = World(walls, self.width, self.height)
        robot = self.__add_random_robot__(world)
        return world, robot
    
    def create_trapezoid_world(self):
        border = create_rect_walls(self.width / 2, self.height / 2, self.width, self.height)
        trapezoid = create_trapezoid_walls(self.width / 2, self.height / 2, self.height, self.width, self.width/ 2)
        walls = [*border, *trapezoid]
        
        world = World(walls, self.width, self.height)
        robot = self.__add_random_robot__(world)
        return world, robot
    
    def create_double_trapezoid_world(self):
        border = create_rect_walls(self.width / 2, self.height / 2, self.width, self.height)
        outer_walls = create_trapezoid_walls(self.width / 2, self.height / 2, self.height, self.width, self.width/ 2)
        inner_walls = create_trapezoid_walls(self.width / 2, self.height / 2, self.height / 2, self.width / 2, self.width / 4)
        walls = [*border, *outer_walls, *inner_walls]
        
        world = World(walls, self.width, self.height)
        robot = self.__add_random_robot__(world)
        return world, robot
    
    def create_star_world(self):
        border = create_rect_walls(self.width / 2, self.height / 2, self.width, self.height)
        star = create_star_walls(self.width / 2, self.height / 2, self.height / 4, self.height / 2)
        walls = [*border, *star]
        
        world = World(walls, self.width, self.height)
        robot = self.__add_random_robot__(world)
        return world, robot
    
    def create_random_world(self):
        world_func = random.choice([
            self.create_rect_world,
            self.create_double_rect_world,
            self.create_trapezoid_world,
            self.create_double_trapezoid_world,
            self.create_star_world
        ])
        
        return world_func()
        
    def __add_random_robot__(self, world):
        min_x = self.robot_radius
        max_x = self.width - self.robot_radius
        min_y = self.robot_radius
        max_y = self.height - self.robot_radius
        
        # Place robot randomly until no collisions occur
        angle = random.uniform(0, 2 * math.pi)
        robot = Robot(0, 0, angle, radius=self.robot_radius, **self.robot_args)
        world.set_robot(robot)
        while True:
            robot.x = random.uniform(min_x, max_x)
            robot.y = random.uniform(min_y, max_y)
            
            collisions = world.circle_collision((robot.x, robot.y), robot.radius)
            if len(collisions) == 0:
                break
        
        return robot