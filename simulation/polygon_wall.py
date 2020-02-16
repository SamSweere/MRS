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
        closest_dist_sqrd = math.inf
        closest_line = None

        for i in range(len(self.points)):
            seg_start = self.points[i]
            seg_end = self.points[(i+1) % len(self.points)]
            
            # Check if the line intersects with our segment
            inter = line_intersect(line_start, line_end, seg_start, seg_end)
            if inter is None:
                continue
            
            # Check if the line intersection is the closest to our line_start
            delta = inter - line_start
            dist_sqrd = delta[0] * delta[0] + delta[1] * delta[1]
            if dist_sqrd < closest_dist_sqrd:
                closest_inter = inter
                closest_dist_sqrd = dist_sqrd
                closest_line = (seg_start, seg_end)
    
        return closest_inter, math.sqrt(closest_dist_sqrd), closest_line
    
    def get_closest_point(self, point):
        closest_point = None
        closest_dist_sqrd = math.inf
        for i in range(len(self.points)):
            seg_start = self.points[i]
            seg_end = self.points[(i+1) % len(self.points)]
            
            closest_segment_point = closest_point_to_seg(seg_start, seg_end, point)
            delta = point - closest_segment_point
            dist_sqrd = delta[0] * delta[0] + delta[1] * delta[1]
            if dist_sqrd < closest_dist_sqrd:
                closest_point = closest_segment_point
                closest_dist_sqrd = dist_sqrd
        
        return closest_point
            
          
def closest_point_to_seg(line_start, line_end, point):
    # Note index 0 stands for x position and 1 for y position
    a1 = line_end[1] - line_start[1]
    b1 = line_start[0] - line_end[0]
    
    c1 = a1 * line_start[0] + b1 * line_start[1]
    c2 = -b1 * point[0] + a1 * point[1]
    det = a1 * a1 + b1 * b1
    cx = (a1 * c1 - b1 * c2) / det
    cy = (a1 * c2 + b1 * c1) / det
    
    return (cx, cy)
    
def line_intersect(a1, a2, b1, b2):
    """
    @param a1: start of line 1
    @param a2: end of line 1
    @param b1: start of line 2
    @param b2: end of line 2
    """
    # Check if two lines intersect
    # Taken from https://stackoverflow.com/questions/3746274/line-intersection-with-aabb-rectangle
    # Note index 0 stands for x position and 1 for y position
    b = a2 - a1
    d = b2 - b1
    b_dot_d_perp = b[0] * d[1] - b[1] * d[0]
    
    # Lines are parallel, aka no intersection
    if b_dot_d_perp == 0:
        return None
    
    c = b1 - a1
    t = (c[0] * d[1] - c[1] * d[0]) / b_dot_d_perp
    # Still no intersection
    if t < 0 or t > 1:
        return None
    
    u = (c[0] * b[1] - c[1] * b[0]) / b_dot_d_perp
    # Still no intersection
    if u < 0 or u > 1:
        return None
    
    intersection = a1 + t * b
    return intersection