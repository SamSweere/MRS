from simulation.line_wall import LineWall
from simulation.dustgrid import DustGrid
from pygame.math import Vector2
import numpy as np
import math


class World:
    def __init__(self, walls, robot, width, height):
    	self.walls = walls
    	self.robot = robot
    	self.dustgrid = DustGrid(width, height, 5)
    	
    	# The robot is now part of this world, so make sure he can access it
    	self.robot.world = self

    def update(self, delta_time):
        self.robot.update(delta_time)

    def raycast(self, x, y, angle, max_length):
        # angle is in radians
        # Calculate the start from x and y
        start = Vector2(x, y)

        # Calculate the direction from angle
        direction = Vector2(math.cos(angle), math.sin(angle))
        end = start + direction * max_length

        closest_inter = None
        closest_dist = max_length
        closest_line = None
        for wall in self.walls:
            inter, dist, line = wall.check_line_intercept(start, end)

            # Check if the intersection is the closest to our start
            if (inter is not None) and (dist < closest_dist) and (line is not None):
                closest_inter = inter
                closest_dist = dist
                closest_line = line

        return closest_inter, closest_dist, closest_line

    def circle_collision(self, circle_position, radius):
        collisions = []
        for wall in self.walls:
            intercept = wall.check_circle_intercept(circle_position, radius)
            if intercept is not None:
                collisions.append(intercept)

        # TODO: check for multiple collisions if the new sliding location is not inside another wall
        return collisions if len(collisions) > 0 else None
