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

        precision = 10000000

        if (circle_start[0] == circle_end[0] and circle_start[1] == circle_end[1]):
            # No movement return None
            return closest_hit

        # Extend the circle_end in the direction of the line
        p = 1000  # TODO: this number is still  a bit arbitrary
        # slope = dy/dx
        # dx = circle_end[0] - circle_start[0]
        # dy = circle_end[1] - circle_start[1]
        # if (dx == 0):
        #     # No movement in the x only change y
        #     mv_end = np.array([circle_end[0], circle_end[1] + p * math.copysign(1, dy)])
        # else:
        #     slope = dy / dx
        #     mv_end = np.array([circle_end[0] + p * math.cos(slope), circle_end[1] + p * math.sin(slope)])

        v = circle_end - circle_start
        u = v/(distance(circle_end, circle_start))
        mv_end = circle_start + p*u

        for i in range(len(self.points)):
            seg_start = self.points[i]
            seg_end = self.points[(i + 1) % len(self.points)]

            a = line_intersect(circle_start, mv_end, seg_start, seg_end)
            if a is None:
                continue

            b = closest_point_to_seg(seg_start, seg_end, circle_end)
            b_req = (distance(b, circle_end) < radius and point_on_line(seg_start, seg_end, b))

            c = closest_point_to_seg(circle_start, circle_end, seg_start)
            c_req = distance(c, seg_start) < radius and point_on_line(circle_start, circle_end, c)

            d = closest_point_to_seg(circle_start, circle_end, seg_end)
            d_req = distance(d, seg_end) < radius and point_on_line(circle_start, circle_end, d)

            if not (b_req or c_req or d_req):
                # No intersection possible
                continue
            p1 = closest_point_to_seg(seg_start, seg_end, circle_start)

            if (distance(p1, circle_end) > radius):
                # Not possible
                continue
            ac_dist = math.ceil((distance(circle_start, a)*precision)/precision)
            plc_dist = math.ceil((distance(circle_start, p1)*precision)/precision)
            # v_dist = distance(circle_start, circle_end)
            # ac = circle_start - a
            # p1c = circle_start - p1
            # ac_norm = math.sqrt(ac[0] * ac[0] + ac[1] * ac[1])
            # p1c_norm = math.sqrt(p1c[0] * p1c[0] + p1c[1] * p1c[1])
            # circle_dir = circle_end - circle_start
            # circle_dir_norm = math.sqrt(circle_dir[0] * circle_dir[0] + circle_dir[1] * circle_dir[1])
            from_a = radius * (ac_dist / plc_dist)

            # Calculate the slope between c and a
            dx = a[0]-circle_start[0]
            dy = a[1]-circle_start[1]
            if (dx == 0):
                # No movement in the x only change y
                slope = dy * math.inf
            else:
                slope = dy / dx
            theta = math.atan(slope)
            # if(abs(slope) != np.inf):
            p2 = np.array([circle_start[0]+(ac_dist - from_a)*math.cos(theta),
                           circle_start[1]+(ac_dist - from_a)*math.sin(theta)])
            # else:
            #     # Vertical line
            #     p2 s= np.array([a[0], a - math.copysign(1, slope)])

            # p2 =
            # p2 = a - radius * (ac_dist / plc_dist) * (circle_dir / circle_dir_norm)

            # if distance(p2, a) >= radius:
            #     # No collision
            #     continue

            print("Hit!")
            print(p2)

            # diff = circle_start - p2
            # p2_norm_sqrd = (diff[0] ** 2 + diff[1] ** 2)
            # if p2_norm_sqrd < closest_dist_sqrd:
            # closest_dist_sqrd = distance(p2, circle_start)
            from_wall = distance(p1, a)
            v_dist = distance(circle_start, circle_end)
            # if(from_wall > v_dist+radius):
            #     # Impossible continue
            #     continue

            # TODO: remove this
            return p2

            if (from_wall < closest_dist):
                closest_dist = from_wall
                closest_hit = p2

        return closest_hit

    # def get_closest_point(self, point):
    #     closest_point = None
    #     closest_dist_sqrd = math.inf
    #     for i in range(len(self.points)):
    #         seg_start = self.points[i]
    #         seg_end = self.points[(i+1) % len(self.points)]
    #
    #         closest_segment_point = closest_point_to_seg(seg_start, seg_end, point)
    #         delta = point - closest_segment_point
    #         dist_sqrd = delta[0] * delta[0] + delta[1] * delta[1]
    #         if dist_sqrd < closest_dist_sqrd:
    #             closest_point = closest_segment_point
    #             closest_dist_sqrd = dist_sqrd
    #
    #     return closest_point


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


def distance(point1, point2):
    return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)


def point_on_line(line_start, line_end, point):
    dx = line_end[0] - line_start[0]
    dy = line_end[1] - line_start[1]
    if (dx == 0):
        # No movement in the x only change y
        if (point[0] == line_start[0]):
            return True
    else:
        slope = dy / dx
        # c = y - slope*x
        c = line_start[1] - slope * line_start[0]
        margin = 0.00001
        if (slope * point[0] + c < point[1] + margin and slope * point[0] + c > point[1] - margin):
            # Point on line
            return True

    return False


def line_intersect(a1, a2, b1, b2):
    """
    @param a1: start of line 1
    @param a2: end of line 1
    @param b1: start of line 2
    @param b2: end of line 2
    from: http://ericleong.me/research/circle-line/#moving-circle-and-static-line-segment
    """

    A1 = a2[1] - a1[1]
    B1 = a1[0] - a2[0]
    C1 = A1 * a1[0] + B1 * a1[1]
    A2 = b2[1] - b1[1]
    B2 = b1[0] - b2[0]
    C2 = A2 * b1[0] + B2 * b1[1]
    det = A1 * B2 - A2 * B1
    if (det != 0):
        x = (B2 * C1 - B1 * C2) / det
        y = (A1 * C2 - A2 * C1) / det
        if (x >= min(a1[0], a2[0]) and x <= max(a1[0], a2[0])
                and x >= min(b1[0], b2[0]) and x <= max(b1[0], b2[0])
                and y >= min(a1[1], a2[1]) and y <= max(a1[1], a2[1])
                and y >= min(b1[1], b2[1]) and y <= max(b1[1], b2[1])):
            # Intersection
            return (x, y)

    return None

# def line_intersect(a1, a2, b1, b2):
#     """
#     @param a1: start of line 1
#     @param a2: end of line 1
#     @param b1: start of line 2
#     @param b2: end of line 2
#     """
#     # Check if two lines intersect
#     # Taken from https://stackoverflow.com/questions/3746274/line-intersection-with-aabb-rectangle
#     # Note index 0 stands for x position and 1 for y position
#     b = a2 - a1
#     d = b2 - b1
#     b_dot_d_perp = b[0] * d[1] - b[1] * d[0]
#
#     # Lines are parallel, aka no intersection
#     if b_dot_d_perp == 0:
#         return None
#
#     c = b1 - a1
#     t = (c[0] * d[1] - c[1] * d[0]) / b_dot_d_perp
#     # Still no intersection
#     if t < 0 or t > 1:
#         return None
#
#     u = (c[0] * b[1] - c[1] * b[0]) / b_dot_d_perp
#     # Still no intersection
#     if u < 0 or u > 1:
#         return None
#
#     intersection = a1 + t * b
#     return intersection
