from simulation.PolygonWall import PolygonWall
import numpy as np
import math

class World:
    def __init__(self, walls):
        self.walls = walls
        
    def raycast(self, x, y, angle, max_length):
        # angle is in radians
        # Calculate the start from x and y
        start = np.array([x,y])

        # Calculate the direction from angle
        direction = np.array([math.cos(angle), math.sin(angle)])
        end = start + direction * max_length
        
        closest_inter = None
        closest_dist = max_length
        for wall in self.walls:
            inter, dist = wall.check_line_intercept(start, end)
            
            # Check if the intersection is the closest to our start
            if inter is not None and dist < closest_dist:
                closest_inter = inter
                closest_dist = dist
        
        return closest_inter, closest_dist

def create_rect_wall(x, y, width, height):
    points = np.array([
        [x - width / 2, y - height / 2],
        [x - width / 2, y + height / 2],
        [x + width / 2, y + height / 2],
        [x + width / 2, y - height / 2]
    ])
    return PolygonWall(points)