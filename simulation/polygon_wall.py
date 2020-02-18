import math
import numpy as np

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
            seg_end = self.points[(i + 1) % len(self.points)]

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

    def check_circle_intercept(self, circle_start, circle_end, radius):
        # Following the guide from: http://ericleong.me/research/circle-line/#moving-circle-and-static-line-segment
        closest_dist = math.inf
        closest_hit = None

        if (circle_start[0] == circle_end[0] and circle_start[1] == circle_end[1]):
            # No movement return None
            return closest_hit

        # Extend the circle_end in the direction of the line
        p = 99e99 # TODO: this number is still  a bit arbitrary

        v = circle_end - circle_start
        u = v/(distance(circle_end, circle_start))
        mv_end = circle_start + p*u

        for i in range(len(self.points)):
            seg_start = self.points[i]
            seg_end = self.points[(i + 1) % len(self.points)]

            # Extend both the segments with the radius for the pole case
            s = seg_end - seg_start
            su = s/(distance(seg_end, seg_start))
            seg_end_ext = seg_end + su * p
            seg_start_ext = seg_start - su * p
            # seg_end_ext = seg_end + su*radius
            # seg_start_ext = seg_start - su*radius

            a = line_intersect(circle_start, mv_end, seg_start_ext, seg_end_ext)
            if a is None:
                continue

            b = closest_point_to_seg(seg_start_ext, seg_end_ext, circle_end)
            b_req = (distance(b, circle_end) < radius and point_on_line(seg_start_ext, seg_end_ext, b))

            c = closest_point_to_seg(circle_start, circle_end, seg_start_ext)
            c_req = distance(c, seg_start_ext) < radius and point_on_line(circle_start, circle_end, c)

            d = closest_point_to_seg(circle_start, circle_end, seg_end_ext)
            d_req = distance(d, seg_end_ext) < radius and point_on_line(circle_start, circle_end, d)

            if not (b_req or c_req or d_req):
                # No intersection possible
                continue
            p1 = closest_point_to_seg(seg_start_ext, seg_end_ext, circle_start)

            if (distance(p1, circle_end) > radius):
                # Not possible
                continue

            ac_dist = distance(circle_start, a)
            plc_dist = distance(circle_start, p1)

            # Calculate the distance we have to move back from a along the v vector
            from_a = radius * (ac_dist / plc_dist)

            # Calculate the slope between c and a
            dx = a[0]-circle_start[0]
            dy = a[1]-circle_start[1]
            if (dx == 0):
                # No movement in the x only change y
                slope = float(dy) * math.inf
            else:
                slope = dy / dx
            theta = math.atan(slope)
            # if(abs(slope) != np.inf):
            # TODO: some weird rounding makes the thing go through
            p2 = np.array([circle_start[0]+(ac_dist - from_a)*math.cos(theta),
                           circle_start[1]+(ac_dist - from_a)*math.sin(theta)])

            pC = closest_point_to_seg(seg_start, seg_end, p2)

            if (not point_on_line(seg_start, seg_end, pC)) or (plc_dist < radius):
                # The point is not on the line, this is a pole or shallow angle scenario
                # Get the point closest to pC
                if distance(seg_start, pC) <= distance(seg_end, pC):
                    # seg_start is closest
                    closest_point = seg_start
                else:
                    # seg_end is closest
                    closest_point = seg_end

                # Check if the closest point is within radius of the final location
                if distance(circle_end, closest_point) > radius:
                    # No collision yet
                    continue

                x = closest_point_to_seg(circle_start, mv_end, closest_point)
                dist_x = distance(x, closest_point)
                # Use pythagoras to find the p2 point
                from_x = math.sqrt(radius ** 2 - dist_x ** 2)
                # Move back along v
                p2 = x - from_x * u

            # p3 = p2 + (p1 - pC)

            # Calculate the distance from p1 to a, this will be used to select which collision is more important
            from_wall = distance(p1, a)

            if (from_wall < closest_dist):
                closest_dist = from_wall
                closest_hit = (p2, plc_dist)

        return closest_hit

def closest_point_to_seg(line_start, line_end, point):
    # Note index 0 stands for x position and 1 for y position
    a1 = line_end[1] - line_start[1]
    b1 = line_start[0] - line_end[0]

    c1 = a1 * line_start[0] + b1 * line_start[1]
    c2 = -b1 * point[0] + a1 * point[1]
    det = a1 * a1 + b1 * b1
    cx = (a1 * c1 - b1 * c2) / det
    cy = (a1 * c2 + b1 * c1) / det

    return np.array([cx, cy])


def distance(point1, point2):
    return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)


def point_on_line(line_start, line_end, point):
    if (distance(line_start, point) + distance(point, line_end) == distance(line_start, line_end)):
        return True
    return False

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
