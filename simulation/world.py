from simulation.polygon_wall import PolygonWall
from simulation.dustgrid import DustGrid
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
        start = np.array([x, y])

        # Calculate the direction from angle
        direction = np.array([math.cos(angle), math.sin(angle)])
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

    def circle_collision(self, c_pos, r_pos, radius):
        # Input is tuples has to be numpy arrays
        c_pos = np.array([c_pos[0], c_pos[1]])
        r_pos = np.array([r_pos[0], r_pos[1]])

        closest_dist = math.inf
        closest_hit = None

        for wall in self.walls:
            hit = wall.check_circle_intercept(c_pos, r_pos, radius)
            if not hit is None:
                dist = hit[1]
                if(dist < closest_dist):
                    closest_hit = hit[0]
                    closest_dist = dist
            # if not hit is None:
            #     print("Hit!")
            #     print(hit)
        return closest_hit


def create_rect_wall(x, y, width, height):
    points = np.array([
        [x - width / 2, y - height / 2],
        [x - width / 2, y + height / 2],
        [x + width / 2, y + height / 2],
        [x + width / 2, y - height / 2]
    ])
    return PolygonWall(points)


def create_line_wall(point1, point2):
    points = np.array([
        [point1[0], point1[1]],
        [point2[0], point2[1]]
    ])
    return PolygonWall(points)
