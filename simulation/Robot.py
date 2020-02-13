import numpy as np
import math

class Robot:
    def __init__(self, world, start_x, start_y, radius=20, 
                movement_speed=5, angle_speed=(5*math.pi/180), n_ray_cast = 10,
                n_sensors = 12, max_sensor_length = 100):
        self.world = world
        self.x = start_x
        self.y = start_y
        self.radius = radius
        self.movement_speed = 5 
        self.angle_speed = angle_speed # This is in radians
        self.n_ray_cast = n_ray_cast # The amount of raycasts it does
        self.n_sensors = n_sensors # The amount of sensors used for collecting environment data
        self.max_sensor_length = max_sensor_length
        
        self.change_angle = 0
        self.speed = 0
        self.angle = np.pi/4 # In radians
        self.sensor_data = []

        self.l = 2 * self.radius
        self.vl = 1
        self.vr = 1.5
        self.v = (self.vr - self.vl / 2)
        self.w = (self.vr - self.vl) / self.l
        self.R, self.icc = self.calculate_icc()

    def calculate_icc(self):
        # # if self.icc_dist == np.inf:
        # #     icc_dist = 999
        # # else: 
        # icc_dist = self.icc_dist
        # self.icc_dist = np.linalg.norm(np.array([self.x - self.icc[0], self.y - self.icc[1]]))
        # print(f"new icc distance {self.icc_dist}")
        R = 1/2 * (self.vl + self.vr) / max((self.vr - self.vl), 0.0001)  # avoid division by zero
        icc = (self.x - R * math.cos(self.angle), self.y - R * math.sin(self.angle))
        return R, icc


    def new_position(self):
        """use dem slides to get da new positions"""
        # # https://opentextbc.ca/physicstestbook2/chapter/kinematics-of-rotational-motion/
        
        # R = 1/2 * (vl + vr) / (vl - vr)

        # w = (vr -vl) / l

        # vr = w(R + l/2)
        # vl = w(R - l/2)

        # v = (vr + vl) / 2


        # ### forward kinematics
        
        vl, vr = 1, 1
        return vl, vr

    def get_icc(self):
        return self.R, self.icc  
        # if (self.icc[0] != np.inf) and (self.icc[1] != np.inf):
        #     return self.icc, self.icc_dist  
        # else:  # TODO: get rid of this somehow
        #     icc = (400, 325)
        #     icc_dist = np.linalg.norm(np.array([self.x - icc[0], self.y - icc[1]]))
        #     return icc, icc_dist

    def update(self):

        self.R, self.icc = self.calculate_icc()

        self.w = (self.vr - self.vl) / self.l

        self.angle = self.angle + self.w
        
        print(f"R: {self.R}\t angle: {self.angle}\t icc: {self.icc}")

        v = (self.vl + self.vr) / 2
        r_x = self.x + v * math.cos(self.angle)
        r_y = self.y + v * math.sin(self.angle)

        self.check_collision(r_x, r_y)

        self.collect_sensor_data()

    # def update(self):

    #     # Rotate the robot
    #     self.angle = (self.angle + self.change_angle * self.angle_speed) % (2*math.pi)

    #     # Based on the speed and the angle find the new requested location
    #     r_x = self.x + self.speed * self.movement_speed * math.cos(self.angle)
    #     r_y = self.y + self.speed * self.movement_speed * math.sin(self.angle)
        
    #     # Check for collision, this function also sets the new x and y values
    #     self.check_collision(r_x, r_y)   
        
    #     # Collects information about the environment, by sending raycasts in all directions
    #     self.collect_sensor_data()
        

    def check_collision(self, r_x, r_y):
        raycast_range = 200
        closest_inter, closest_dist = self.world.raycast(self.x, self.y, self.angle, raycast_range)    
        # print(closest_inter, closest_dist)

        if(closest_inter is None):
            # No collision, set the new x and y based on the requested values
            self.x = r_x
            self.y = r_y
        else:
            inter_x = closest_inter[0]
            inter_y = closest_inter[1]
            # Check the four looking directions
            if(self.angle >= 0 and self.angle < 0.5*math.pi): 
                if(r_x > inter_x or r_y > inter_y):
                    # Collision move the robot to the point
                    self.x = inter_x
                    self.y = inter_y
                else:
                    # No collision, set the new x and y based on the requested values
                    self.x = r_x
                    self.y = r_y
            elif(self.angle >= 0.5*math.pi and self.angle < math.pi):
                pass
            elif(self.angle >= math.pi and self.angle < 1.5*math.pi):
                pass
            elif(self.angle >= 1.5*math.pi and self.angle < 2*math.pi):
                pass
            else:
                print("Error: something is wrong with the angle of the robot")
                
    def collect_sensor_data(self):
        raycast_length = self.radius + self.max_sensor_length
        delta_angle = (math.pi * 2) / self.n_sensors
        
        self.sensor_data = []
        for sensor_id in range(self.n_sensors):
            # Note the sensor angle is relative to our own angle
            sensor_angle = self.angle + delta_angle * sensor_id
            
            # Note instead of calculating the position of the sensor
            # We just send a raycast from the center of our agent
            (hit, dist) = self.world.raycast(self.x, self.y, sensor_angle, raycast_length)
            dist -= self.radius
            self.sensor_data.append((hit, dist))
            