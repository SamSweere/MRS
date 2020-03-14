import numpy as np
import math


class Robot:
    def __init__(self, start_x, start_y, start_angle, scenario, radius=20,
                 max_v=100, v_step=10, n_sensors=12, max_sensor_length=100):
        self.x = start_x
        self.y = start_y
        self.scenario = scenario
        if scenario == "evolutionary":
            self.motion_model = "diff_drive"
        elif scenario == "localization":
            self.motion_model = "vel_drive"
        else:
            raise NameError("Invalid scenario name")

        self.radius = radius
        self.max_v = max_v
        self.angle = start_angle  # In radians

        if self.motion_model == "diff_drive":
            self.v_step = v_step
            self.n_sensors = n_sensors  # The amount of sensors used for collecting environment data
            self.max_sensor_length = max_sensor_length
            self.sensor_data = []


            self.l = 2 * self.radius
            self.vl = 0
            self.vr = 0
            self.v = (self.vr - self.vl / 2)
            self.w = (self.vr - self.vl) / self.l
            self.R, self.icc = self.calculate_icc()

    def update_vr(self, direction):
        if direction == 0:
            # Stop
            self.vr = 0
            return

        r_vr = self.vr + direction * self.v_step

        if -self.max_v <= r_vr <= self.max_v:
            self.vr = r_vr
        else:
            # Over speed limit
            pass

    def update_vl(self, direction):
        if direction == 0:
            # Stop
            self.vl = 0
            return

        r_vl = self.vl + direction * self.v_step

        if -self.max_v <= r_vl <= self.max_v:
            self.vl = r_vl
        else:
            # Over speed limit
            pass

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

    def differential_drive(self, delta_time):
        # Get the new center of rotation and speed
        self.R, self.icc = self.calculate_icc()
        self.w = (self.vr - self.vl) / self.l

        # Determine the new angle keep it within 2 pi
        # w is basically theta because we just assume time was 1
        angle_change = self.w * delta_time

        # Based on the speed and the angle find the new requested location
        if (self.vr == self.vl) and (self.vr != 0):
            r_x = self.x + self.vr * math.cos(self.angle) * delta_time
            r_y = self.y + self.vr * math.sin(self.angle) * delta_time
        else:
            icc_x = self.icc[0]
            icc_y = self.icc[1]
            r_x = (math.cos(angle_change) * (self.x - icc_x) -
                   math.sin(angle_change) * (self.y - icc_y) +
                   icc_x)
            r_y = (math.sin(angle_change) * (self.x - icc_x) +
                   math.cos(angle_change) * (self.y - icc_y) +
                   icc_y)

        r_angle = (self.angle + angle_change) % (2 * math.pi)

        return r_x, r_y, r_angle

    def velocity_based_drive(self, delta_time):

        r_x = 12
        r_y = 12
        r_angle = 12

        return r_x, r_y, r_angle

    def update(self, delta_time):

        if self.motion_model == "diff_drive":
            r_x, r_y, r_angle = self.differential_drive(delta_time)
        elif self.motion_model == "vel_drive":
            r_x, r_y, r_angle = self.velocity_based_drive(delta_time)

        # Save the x and y for the speed calculation
        x_tmp = self.x
        y_tmp = self.y

        self.check_collision(r_x, r_y, r_angle)

        if self.motion_model == "diff_drive":
            self.collect_sensor_data()

        # To calculate the actual speed
        self.v = math.sqrt((x_tmp - self.x) ** 2 + (y_tmp - self.y) ** 2)

    def check_collision(self, r_x, r_y, r_angle):
        """
        @param r_x: aspired x position after time step
        @param r_y: aspired y position after time step
        @param r_angle: aspired angle after time step
        """
        collision = self.world.slide_collision((self.x, self.y), (r_x, r_y), self.radius)
        if collision is None:
            # No collision
            self.x = r_x
            self.y = r_y
        else:
            # Slide
            self.x = collision.x
            self.y = collision.y

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
