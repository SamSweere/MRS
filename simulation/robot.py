import numpy as np
import math


class Robot:
    def __init__(self, start_x, start_y, start_angle, radius=20,
                 movement_speed=5, angle_speed=(5 * math.pi / 180), n_ray_cast=10,
                 n_sensors=12, max_sensor_length=100):
        self.x = start_x
        self.y = start_y
        self.radius = radius
        self.movement_speed = 5
        self.n_ray_cast = n_ray_cast
        self.n_sensors = n_sensors  # The amount of sensors used for collecting environment data
        self.max_sensor_length = max_sensor_length

        self.change_angle = 0
        self.speed = 0
        self.angle = start_angle  # In radians
        self.sensor_data = []

        self.l = 2 * self.radius
        self.vl = 0
        self.vr = 0
        self.v = (self.vr - self.vl / 2)
        self.w = (self.vr - self.vl) / self.l
        self.R, self.icc = self.calculate_icc()

    def calculate_icc(self):
        """Returns the radius and the (x,y) coordinates of the center of rotation"""
        # Calculate center of rotation
        diff = self.vr - self.vl
        R = self.l / 2 * (self.vl + self.vr) / (diff if diff != 0 else 0.0001)  # avoid division by zero
        icc = (
            self.x - R * math.sin(self.angle),
            self.y + R * math.cos(self.angle)
        )
        return R, icc

    def update(self, delta_time):
        # Get the new center of rotation and speed
        self.R, self.icc = self.calculate_icc()
        self.w = (self.vr - self.vl) / self.l

        # Determine the new angle keep it within 2 pi
        # w is basically theta because we just assume time was 1
        self.v = (self.vl + self.vr / 2)
        angle_change = self.w * delta_time

        # Based on the speed and the angle find the new requested location
        if (self.vr == self.vl) and (self.vr != 0):
            r_x = self.x + self.v * math.cos(self.angle) * delta_time
            r_y = self.y + self.v * math.sin(self.angle) * delta_time
        else:
            # TODO: should this move even if vr == vl?
            icc_x = self.icc[0]
            icc_y = self.icc[1]
            r_x = (math.cos(angle_change) * (self.x - icc_x) -
                   math.sin(angle_change) * (self.y - icc_y) +
                   icc_x)
            r_y = (math.sin(angle_change) * (self.x - icc_x) +
                   math.cos(angle_change) * (self.y - icc_y) +
                   icc_y)

        r_angle = (self.angle + angle_change) % (2 * math.pi)

        # To test if the speed is right
        self.v_test = math.sqrt((self.x - r_x) ** 2 + (self.y - r_y) ** 2)

        self.check_collision(r_x, r_y, r_angle)
        self.collect_sensor_data()

    def check_collision(self, r_x, r_y, r_angle):
        """
        @param r_x: aspired x position after time step
        @param r_y: aspired y position after time step
        @param r_angle: aspired angle after time step
        """
        collision = self.world.circle_collision((r_x, r_y), self.radius)
        if collision is None:
            # No collision
            self.x = r_x
            self.y = r_y
        else:
            # Slide
            # TODO: handle mutliple collisoins
            self.x = collision[0].x
            self.y = collision[0].y

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
            hit, dist, line = self.world.raycast(self.x, self.y, sensor_angle,
                                                 raycast_length)
            dist -= self.radius
            self.sensor_data.append((hit, dist))
