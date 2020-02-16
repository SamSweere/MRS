import numpy as np
import math


class Robot:
    def __init__(self, world, start_x, start_y, radius=20,
                 movement_speed=5, angle_speed=(5 * math.pi / 180), n_ray_cast=10,
                 n_sensors=12, max_sensor_length=100):
        self.world = world
        self.x = start_x
        self.y = start_y
        self.radius = radius
        self.movement_speed = 5
        self.n_ray_cast = n_ray_cast  # The amount of raycasts it does
        self.n_sensors = n_sensors  # The amount of sensors used for collecting environment data
        self.max_sensor_length = max_sensor_length

        self.change_angle = 0
        self.speed = 0
        self.angle = np.pi * 5 / 4  # In radians
        self.sensor_data = []

        self.l = 2 * self.radius
        self.vl = 0
        self.vr = 0
        self.v = (self.vr - self.vl / 2)
        self.w = (self.vr - self.vl) / self.l
        self.R, self.icc = self.calculate_icc()


    def calculate_icc(self):
        """Returns the radius and the (x,y) coordinates of the center of rotation"""
        # Calculate the center of rotation, 
        diff = self.vr - self.vl
        R = self.l / 2 * (self.vl + self.vr) / (diff if diff != 0 else 0.0001)  # avoid division by zero
        icc = (
            self.x - R * math.sin(self.angle),
            self.y + R * math.cos(self.angle)
        )
        return R, icc


    def update(self):
        # Get the new center of rotation and speed
        self.R, self.icc = self.calculate_icc()
        self.w = (self.vr - self.vl) / self.l

        # Determine the new angle keep it within 2 pi
        # w is basically theta because we just assume time was 1
        v = (self.vl + self.vr / 2)
        dt = 1
        angle_change = self.w * dt

        # Based on the speed and the angle find the new requested location
        if self.vr == self.vl:
            r_x = self.x + v * math.cos(self.angle)
            r_y = self.y + v * math.sin(self.angle)
        else:
            # TODO: should this move even if vr == vl?
            icc_x = self.icc[0]
            icc_y = self.icc[1]
            r_x = (
                    math.cos(angle_change) * (self.x - icc_x) -
                    math.sin(angle_change) * (self.y - icc_y) +
                    icc_x
            )
            r_y = (
                    math.sin(angle_change) * (self.x - icc_x) +
                    math.cos(angle_change) * (self.y - icc_y) +
                    icc_y
            )

        self.angle = (self.angle + angle_change) % (2 * math.pi)

        print(f"R: {self.R}\t angle: {self.angle}\t icc: {self.icc}, \
        location: ({self.x}, {self.y})")

        # Check for collision, this function also sets the new x and y values
        self.check_collision(r_x, r_y, r_angle)

        # Collects information about the environment, by sending raycasts in all directions
        self.collect_sensor_data()


    def get_icc(self):
        return self.R, self.icc


    def update_old(self):
        """
        old update method
        """

        # Calculate the requested angle
        r_angle = (self.angle + self.change_angle) % (2 * math.pi)

        # Based on the speed and the angle find the new requested location
        r_x = self.x + self.speed * self.movement_speed * math.cos(r_angle)
        r_y = self.y + self.speed * self.movement_speed * math.sin(r_angle)

        # Check for collision, this function also sets the new x and y values
        self.check_collision(r_x, r_y, r_angle)

        # Collects information about the environment, by sending raycasts in all directions
        self.collect_sensor_data()


    def check_collision_edge(self, theta, r_x, r_y, r_angle):
        """
        @param theta: point on the edge in radians
        @param r_x: aspired x position after time step
        @param r_y: aspired y position after time step
        @param r_angle: aspired angle after time step
        """
        raycast_range = 2 * self.movement_speed

        # Start the raycast from edge of the circle
        edge_x = self.x + math.cos(self.angle + theta) * self.radius
        edge_y = self.y + math.sin(self.angle + theta) * self.radius

        edge_r_x = r_x + math.cos(r_angle + theta) * self.radius
        edge_r_y = r_y + math.sin(r_angle + theta) * self.radius
        # print("theta:", theta)
        # print("x:", self.x)
        # print("edge_x:", edge_x)
        # print("edge_r_x:", edge_r_x)

        closest_inter, closest_dist, closest_line = self.world.raycast(edge_x,
            edge_y, (self.angle + theta)%(2*math.pi), raycast_range)
        # print("Inter:", closest_inter, closest_dist)

        # Define a buffer such that the robot is not placed at exactly the wall
        # This would cause it to stop for one frame and then clip through
        buffer = 1#1.0e-10

        if (closest_inter is None):
            return None  # No collision return None
        else:
            # Get the intersect x and y
            inter_x = closest_inter[0]
            inter_y = closest_inter[1]

            # print("self.xy:", self.x, self.y)
            # print("r.xy:", r_x, r_y)
            # print("inter.xy:", inter_x, inter_y)

            collision = False
            #TODO: start with fixing the line intersect here. Make use of the intersected line to do normal calculations

            # Check the four possible directions
            if (edge_x >= inter_x and edge_r_x < inter_x):
                final_x = inter_x + buffer
                collision = True
            elif (edge_x <= inter_x and edge_r_x > inter_x):
                final_x = inter_x - buffer
                collision = True
            else:
                final_x = None

            if (edge_y >= inter_y and edge_r_y < inter_y):
                final_y = inter_y + buffer
                collision = True
            elif (edge_y <= inter_y and edge_r_y > inter_y):
                final_y = inter_y - buffer
                collision = True
            else:
                final_y = None

            if not collision:
                return None

            return final_x, final_y


    def check_collision(self, r_x, r_y, r_angle):
        """
        @param r_x: aspired x position after time step
        @param r_y: aspired y position after time step
        @param r_angle: aspired angle after time step
        """
        n_col_rays = 32  # Ideally powers of 2
        single_beam = False

        if single_beam:
            theta = 0# math.pi/4
            col_ray_angles = [theta]
        else:
            col_ray_angles = np.linspace(0, 2 * math.pi, n_col_rays, endpoint=False)
        
        collision = False
        for theta in col_ray_angles:
            collision_point = self.check_collision_edge(theta, r_x, r_y, r_angle)
            if (collision_point is None):
                continue  # No collision
            else:
                # There is a collision, set the location to the corrected collision location
                print("Collision!")
                collision = True
                if (collision_point[0] is None):
                    # No collision here
                    self.x = r_x
                else:
                    self.x = collision_point[0] - math.cos(self.angle + theta) * self.radius

                if (collision_point[1] is None):
                    # No collision here
                    self.x = r_x
                else:
                    self.y = collision_point[1] - math.sin(self.angle + theta) * self.radius
                break  # We have a collision break out of the loop

        if (not collision):
            # No collision, set the location to the requested values
            self.x = r_x
            self.y = r_y
            self.angle = r_angle


    def collect_sensor_data(self):
        raycast_length = self.radius + self.max_sensor_length
        delta_angle = (math.pi * 2) / self.n_sensors

        self.sensor_data = []
        for sensor_id in range(self.n_sensors):
            # Note the sensor angle is relative to our own angle
            sensor_angle = self.angle + delta_angle * sensor_id

            # Note instead of calculating the position of the sensor
            # We just send a raycast from the center of our agent
            (hit, dist, line) = self.world.raycast(self.x, self.y, sensor_angle, raycast_length)
            dist -= self.radius
            self.sensor_data.append((hit, dist))
