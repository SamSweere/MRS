import math

class PolygonWall:
    def __init__(self, points):
        self.points = points
        
    def check_line_intercept(self, line_start, line_end):
        """
            Checks if the line intercepts with this Polygon
            Returns the intersection point that is closest to line_start
        """
        closest_inter = None
        closest_dist = 9999999999999.
        for i in range(len(self.points)):
            seg_start = self.points[i]
            seg_end = self.points[(i+1) % len(self.points)]
            
            # Check if the line intersects with our segment
            inter = line_intersect(line_start, line_end, seg_start, seg_end)
            if inter is None:
                continue
            
            # Check if the line intersection is the closest to our line_start
            delta = inter - line_start
            dist = math.sqrt(delta[0] * delta[0] + delta[1] * delta[1])
            if dist < closest_dist:
                closest_inter = inter
                closest_dist = dist
    
        return None if closest_inter is None else (closest_inter, closest_dist);
          
def line_intersect(a1, a2, b1, b2):
    # Check if two lines intersect
    # Taken from https://stackoverflow.com/questions/3746274/line-intersection-with-aabb-rectangle
    # Note index 0 stands for x position and 1 for y position
    b = a2 - a1
    d = b2 - b1
    b_dot_d_perp = b[0] * d[1] - b[1] * d[0];
    
    # Lines are parallel, aka no intersection
    if b_dot_d_perp == 0:
        return None
    
    c = b1 - a1
    t = (c[0] * d[1] - c[1] * d[0]) / b_dot_d_perp
    # Still no intersection
    if t < 0 or t > 1:
        return None
    
    u = (c[0] * b[1] - c[1] * b[0]) / b_dot_d_perp;
    # Still no intersection, stop fucking asking
    if u < 0 or u > 1:
        return None
    
    intersection = a1 + t * b;
    return intersection