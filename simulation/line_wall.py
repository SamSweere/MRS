import math
import numpy as np
from pygame.math import Vector2

class LineWall:
    def __init__(self, start, end):
        self.start = Vector2(start)
        self.end = Vector2(end)
        
    def get_closest_point(self, point):
        """
            Finds the closest point on this line to the given point
        """
        point = Vector2(point)
        
        seg_v = self.end - self.start
        pt_v = point - self.start
        if seg_v.length() <= 0:
            raise ValueError("Invalid segment length")
            
        seg_v_unit = seg_v.normalize()
        proj = pt_v.dot(seg_v_unit)
        if proj <= 0:
            return self.start
        elif proj >= seg_v.length():
            return self.end
        
        proj_v = seg_v_unit * proj
        closest = proj_v + self.start
        
        return closest
    
    def check_circle_intercept(self, circle_pos, radius):
        """
            Finds one point on this line that is overlapping with the circles circumference
        """
        circle_pos = Vector2(circle_pos)
        closest = self.get_closest_point(circle_pos)
        dist_v = circle_pos - closest
        if dist_v.length() >= radius:
            return None
        if dist_v.length() <= 0:
            raise ValueError("Circle's center is exactly on the wall")
            
        offset = dist_v / dist_v.length() * (radius / dist_v.length())
        return offset

    def check_line_intercept(self, line_start, line_end):
        """
            Checks if the line intercepts with this Polygon
            Returns the intersection point that is closest to line_start
        """
        line_start = Vector2(line_start)
        line_end = Vector2(line_end)

        # Check if the line intersects with our segment
        inter = line_intersect(line_start, line_end, self.start, self.end)
        if inter is None:
            return None, math.inf, None

        # Check if the line intersection is the closest to our line_start
        delta = inter - line_start
        distance = math.sqrt(delta[0] * delta[0] + delta[1] * delta[1])
        closest_line = (self.start, self.end)

        return inter, distance, closest_line

def line_intersect(a1, a2, b1, b2):
    """
    @param a1: start of line 1
    @param a2: end of line 1
    @param b1: start of line 2
    @param b2: end of line 2
    """
    # Check if two lines intersect
    # Taken from https://stackoverflow.com/questions/3746274/line-intersection-with-aabb-rectangle
    b = a2 - a1
    d = b2 - b1
    b_dot_d_perp = b.x * d.y - b.y * d.x

    # Lines are parallel, aka no intersection
    if b_dot_d_perp == 0:
        return None

    c = b1 - a1
    t = (c.x * d.y - c.y * d.x) / b_dot_d_perp
    # Still no intersection
    if t < 0 or t > 1:
        return None

    u = (c.x * b.y - c.y * b.x) / b_dot_d_perp
    # Still no intersection
    if u < 0 or u > 1:
        return None

    intersection = a1 + t * b
    return intersection
