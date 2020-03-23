import numpy as np
import math
from simulation.kf_localizer import KFLocalizer


def vel_motion_model(state, action, delta_time):
    x, y, angle = state
    v, w = action

    new_x = x + v * math.cos(angle) * delta_time
    new_y = y + v * math.sin(angle) * delta_time
    new_angle = angle + delta_time * w
    return (new_x, new_y, new_angle)


def triangulate(x1, y1, r1, x2, y2, r2, x3, y3, r3):
    # Using formula from:
    A = -2 * x1 + 2 * x2
    B = -2 * y1 + 2 * y2
    C = r1 ** 2 - r2 ** 2 - x1 ** 2 + x2 ** 2 - y1 ** 2 + y2 ** 2
    D = -2 * x2 + 2 * x3
    E = -2 * y2 + 2 * y3
    F = r2 ** 2 - r3 ** 2 - x2 ** 2 + x3 ** 2 - y2 ** 2 + y3 ** 2

    if (E * A - B * D) == 0.0:
        # Two points lie on each others line, return None
        # TODO: this is solvable, just not with this method
        return None

    x = (C * E - F * B) / (E * A - B * D)
    y = (C * D - A * F) / (B * D - A * E)

    return x, y


class Robot:
    def __init__(self, start_x, start_y, start_angle, scenario, collision, radius=20,
                 max_v=100, v_step=10, n_sensors=12, max_sensor_length=100, omni_sensor_range=150):
        self.x = start_x
        self.y = start_y
        self.scenario = scenario
        self.collision = collision
        self.radius = radius
        self.max_v = max_v
        self.angle = start_angle  # In radians

        if scenario == "evolutionary":
            self.motion_model = "diff_drive"
        elif scenario == "localization":
            self.omni_sensor_range = omni_sensor_range
            self.motion_model = "vel_drive"
            self.beacons = []  # beacons have format (beacon, distance)
            # Initialize localization
            state_mu = (self.x, self.y, self.angle)
            state_std = np.identity(3) * 0.01
            motion_noise = np.identity(3)
            motion_noise[0, 0] *= 0.002  # x
            motion_noise[1, 1] *= 0.004  # y
            motion_noise[2, 2] *= 0.001  # angle

            self.sensor_noise = np.identity(3)
            self.sensor_noise[0, 0] *= 10.0  # x
            self.sensor_noise[1, 1] *= 10.0  # y
            self.sensor_noise[2, 2] *= 0.1  # angle

            print(motion_noise)
            self.localizer = KFLocalizer(state_mu=state_mu, state_std=state_std, motion_model=vel_motion_model,
                                         motion_noise=motion_noise, sensor_noise=self.sensor_noise)


            # # Define variables fot the predicted location
            # self.p_x = self.x
            # self.p_y = self.y
            # self.p_angle = self.angle
            # Define the standard deviations for the localization errors

        else:
            raise NameError("Invalid scenario name")

        if self.motion_model == "diff_drive":
            self.v_step = v_step
            self.n_sensors = n_sensors  # The amount of sensors used for collecting environment data
            self.max_sensor_length = max_sensor_length
            self.sensor_data = []

            self.l = 2 * self.radius
            self.vl = 0
            self.vr = 0
            self.velocity = (self.vr - self.vl / 2)
            self.w = (self.vr - self.vl) / self.l
            self.R, self.icc = self.calculate_icc()

        elif self.motion_model == "vel_drive":
            self.angle_step = 0.20 * math.pi
            self.angle_change = 0
            self.v = 0
            self.v_step = v_step
            self.rotate_left = False
            self.rotate_right = False
            self.pressed_arrows = False



    def update_vr(self, direction):
        # Used in the diff_drive scenario
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
        # Used in the diff_drive scenario
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

    def update_v(self, direction):
        # Used in the vel_drive scenario
        if direction == 0:
            # Stop
            self.v = 0
            return
        if abs(direction) == 1:
            # WSAD keys
            r_v = self.v + direction * self.v_step
        else:
            r_v = direction

        if abs(r_v) > self.max_v:
            # Over max v set to max v
            self.v = r_v / abs(r_v) * self.max_v
        else:
            # within speed limit
            self.v = r_v

    def update_angle(self, direction):
        if direction == 0:
            # Stop
            self.angle_change = 0
            return

        # Used in the vel_drive scenario
        self.angle_change += direction * self.angle_step

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
        # Make use of booleans such that pressing the other direction does not cancel the button press
        if self.rotate_left and self.rotate_right:
            # No change
            self.angle_change = 0
            self.pressed_arrows = True
        elif self.rotate_left:
            self.angle_change = -1
            self.pressed_arrows = True
        elif self.rotate_right:
            self.angle_change = 1
            self.pressed_arrows = True
        else:
            if self.pressed_arrows:
                self.angle_change = 0
                self.pressed_arrows = False

        state = (self.x, self.y, self.angle)
        action = (self.v, self.angle_change)
        return vel_motion_model(state, action, delta_time)

    def update(self, delta_time):
        if self.motion_model == "diff_drive":
            r_x, r_y, r_angle = self.differential_drive(delta_time)
        elif self.motion_model == "vel_drive":
            r_x, r_y, r_angle = self.velocity_based_drive(delta_time)
            self.localizer.predict((self.v, self.angle_change), delta_time)

        # Save the x and y for the speed calculation
        x_tmp = self.x
        y_tmp = self.y

        if self.collision:
            self.check_collision(r_x, r_y, r_angle)
        else:
            # No reason to have the requested location and angle refused
            self.x = r_x
            self.y = r_y
            self.angle = r_angle

        if self.motion_model == "diff_drive":
            self.collect_sensor_data()

        if self.scenario == "localization":
            # Scan for beacons
            # TODO: no error implemented yet, do this in scan for beacons method
            self.beacons = self.scan_for_beacons()
            # Triangulate location if possible
            z = self.location_from_beacons()
            self.localizer.update_z(z, self.sensor_noise)


            # # TODO: only for debugging
            # if z is not None:
            #     # Do something
            #     self.p_x = z[0]
            #     self.p_y = z[1]
            #     self.p_angle = z[2]
            #     pass
            # else:
            #     # Do something else
            #     pass

        # To calculate the actual speed
        self.velocity = math.sqrt((x_tmp - self.x) ** 2 + (y_tmp - self.y) ** 2)

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

    def scan_for_beacons(self):
        beacons_in_range = self.world.get_beacons(self.x, self.y, self.omni_sensor_range)

        for i in range(len(beacons_in_range)):
            error = 0
            # TODO: introduce error here
            beacons_in_range[i] = (beacons_in_range[i][0], beacons_in_range[i][1] + error)

        return beacons_in_range

    def location_from_beacons(self):
        # Estimate the location of the robot from the beacons
        f = []
        for beacon in self.beacons:
            beacon = beacon[0]
            # Note true x and y value of the robot since this is independent on the predicted location
            r = math.sqrt((beacon.x - self.x) ** 2 + (beacon.y - self.y) ** 2)
            # -1 times since our y coordinate system is inverted
            phi = math.atan2(-1 * (beacon.y - self.y), beacon.x - self.x) - self.angle
            f.append((r, phi, beacon.location))

        # From the r and phi get the x and y location, note that in the exercise we are allowed
        # to add the error later

        # TODO: we could get some estimate from 1 beacon, however we would have to use our predicted angle
        got_location = False
        # which is not part of z
        if len(f) >= 3:
            # Three points can lie on the same line, in which case our function cant handle it, try other ways
            shift = 0
            tria_loc = triangulate(f[0 + shift][2][0], f[0 + shift][2][1], f[0 + shift][0],
                                   f[1 + shift][2][0], f[1 + shift][2][1], f[1 + shift][0],
                                   f[2 + shift][2][0], f[2 + shift][2][1], f[2 + shift][0])
            while tria_loc is None and shift + 3 <= len(f):
                shift += 1
                tria_loc = triangulate(f[0 + shift][2][0], f[0 + shift][2][1], f[0 + shift][0],
                                       f[1 + shift][2][0], f[1 + shift][2][1], f[1 + shift][0],
                                       f[2 + shift][2][0], f[2 + shift][2][1], f[2 + shift][0])

            if tria_loc is not None:
                x, y = tria_loc
                # Now that we know the position get the angle, we well only use one beacon for this
                angle = math.atan2(-1 * (self.beacons[0][0].y - y), self.beacons[0][0].x - x) - f[0][1]
                got_location = True

        if got_location:
            # We got the location and angle, add noise
            x += np.random.normal(0, self.sensor_noise[0, 0])
            y += np.random.normal(0, self.sensor_noise[1, 1])
            angle += np.random.normal(0, self.sensor_noise[2, 2])

            return x, y, angle
        else:
            # No location
            return None

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
