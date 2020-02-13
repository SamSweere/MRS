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
        # Calculate the center of rotation, 
        # Returns the radius and the (x,y) coordinates of the center of rotation
        R = 1/2 * (self.vl + self.vr) / max((self.vr - self.vl), 0.0001)  # avoid division by zero
        icc = (self.x - R * math.cos(self.angle), self.y - R * math.sin(self.angle))
        return R, icc

    def get_icc(self):
        return self.R, self.icc

    def update(self):
        # Get the new center of rotation and speed
        self.R, self.icc = self.calculate_icc()
        self.w = (self.vr - self.vl) / self.l

        # Determine the new angle
        self.angle = self.angle + self.w
        
        print(f"R: {self.R}\t angle: {self.angle}\t icc: {self.icc}")

        # Based on the speed and the angle find the new requested location
        v = (self.vl + self.vr) / 2
        r_x = self.x + v * math.cos(self.angle)
        r_y = self.y + v * math.sin(self.angle)

        # Check for collision, this function also sets the new x and y values
        self.check_collision(r_x, r_y) 

        # Collects information about the environment, by sending raycasts in all directions
        self.collect_sensor_data()

    def update_old(self):
        """
        old update method
        """

        # Rotate the robot
        self.angle = (self.angle + self.change_angle * self.angle_speed) % (2*math.pi)

        # Based on the speed and the angle find the new requested location
        r_x = self.x + self.speed * self.movement_speed * math.cos(self.angle)
        r_y = self.y + self.speed * self.movement_speed * math.sin(self.angle)
        
        # Check for collision, this function also sets the new x and y values
        self.check_collision(r_x, r_y)   
        
        # Collects information about the environment, by sending raycasts in all directions
        self.collect_sensor_data()
        

    def check_collision(self, r_x, r_y):
        raycast_range = 200
        closest_inter, closest_dist = self.world.raycast(self.x, self.y, self.angle, raycast_range)    
        print("Inter:",closest_inter, closest_dist)

        # Define a buffer such that the robot is not placed at exactly the wall
        buffer = 1

        if(closest_inter is None):
            # No collision, set the new x and y based on the requested values
            self.x = r_x
            self.y = r_y
        else:
            # Get the intersect x and y
            inter_x = closest_inter[0]
            inter_y = closest_inter[1]

            print("self.xy:",self.x, self.y)
            print("r.xy:",r_x,r_y)
            print("inter.xy:",inter_x, inter_y)

            # Check the four looking directions
            if(self.x >= inter_x and r_x < inter_x): 
                # Collision, move the robot to the collision x point plus some buffer
                # TODO: this is a bit more complex
                print("Collision!")
                self.x = inter_x + buffer             
            elif(self.x <= inter_x and r_x > inter_x):
                # Collision, move the robot to the collision x point plus some buffer
                # TODO: this is a bit more complex
                print("Collision!")
                self.x = inter_x - buffer
            else:
                # No collision with x, set the location to the requested x location
                self.x = r_x

            if(self.y >= inter_y and r_y < inter_y):
                # Collision, move the robot to the collision y point plus some buffer
                # TODO: this is a bit more complex
                print("Collision!")
                self.y = inter_y + buffer 
            elif(self.y <= inter_y and r_y > inter_y):
                # Collision, move the robot to the collision y point plus some buffer
                # TODO: this is a bit more complex
                print("Collision!")
                self.y = inter_y - buffer
            else:
                # No collision with y, set the location to the requested y location
                self.y = r_y
            
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
            