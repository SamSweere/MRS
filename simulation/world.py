from simulation.line_wall import LineWall
from simulation.dustgrid import DustGrid
from pygame.math import Vector2
import numpy as np
import math


class World:
    def __init__(self, walls, width, height):
    	self.walls = walls
    	self.dustgrid = DustGrid(width, height, 5)

    def set_robot(self, robot):
        self.robot = robot
        # The robot is now part of this world, so make sure he can access it
        self.robot.world = self

    def update(self, delta_time):
        self.robot.update(delta_time)
        self.dustgrid.clean_circle_area(self.robot.x, self.robot.y, self.robot.radius)

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
        circle_position = Vector2(circle_position)

        collisions = []
        # prev_intercept = False
        for wall in self.walls:
            offset = wall.check_circle_intercept(circle_position, radius)
            if offset is not None:
                collisions.append((wall, offset))
            
        return collisions
    
    def slide_collision(self, circle_position, r_circle_position, radius):
        circle_position = Vector2(circle_position)
        r_circle_position = Vector2(r_circle_position)
        
        collisions = self.circle_collision(r_circle_position, radius)
        if len(collisions) == 0:
            return None

        # Check if the slide locations do not cause interceptions, take the first slide location that did not cause
        # an intercept
        for wall, offset in collisions:
            slide_loc = wall.calculate_sliding(r_circle_position, radius)
            
            free_from_all = True
            for wall in self.walls:
                intercept = wall.check_circle_intercept(slide_loc, radius)
                if intercept:
                    # Not free from all walls
                    free_from_all = False

            if free_from_all:
                # This slide position is free from all walls
                return slide_loc

        # At this point all the slide positions are behind walls, return the old location
        return circle_position
