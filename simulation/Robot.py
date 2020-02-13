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
        self.vl = 0
        self.vr = 0
        self.v = (self.vr - self.vl / 2)
        self.w = (self.vr - self.vl) / self.l
        self.R, self.icc = self.calculate_icc()

    def calculate_icc(self):
        """Returns the radius and the (x,y) coordinates of the center of rotation"""
        # Calculate the center of rotation, 
        diff = self.vr - self.vl
        R = 1/2 * (self.vl + self.vr) / (diff if diff != 0 else 0.0001)  # avoid division by zero
        icc = (self.x - R * math.sin(self.angle), self.y + R * math.cos(self.angle))
        return R, icc

    def get_icc(self):
        return self.R, self.icc

    def update(self):
        # TODO: why does it not move the right way initially

        # TODO: turning on the spot currently not working :O

        # Get the new center of rotation and speed
        self.R, self.icc = self.calculate_icc()
        self.w = (self.vr - self.vl) / self.l

        # Determine the new angle keep it within 2 pi
        # w is basically theta because we just assume time was 1
        v = (self.vl + self.vr / 2)
        dt = 1
        if v != 0:
            angle_change = self.w * dt * v
        else:  # we want to be able to rotate on the spot
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

        self.angle = (self.angle + angle_change) % (2*math.pi)
        
        print(f"R: {self.R}\t angle: {self.angle}\t icc: {self.icc}, location: ({self.x}, {self.y})")

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
        

    def check_collision_edge(self, theta, r_x, r_y):
        # Check the collision for on point on the edge of the circle
        # theta is the point on the edge in radians
        raycast_range = 2*self.movement_speed

        # Start the raycast from edge of the circle
        edge_x = self.x + math.cos(self.angle + theta)*self.radius
        edge_y = self.y + math.sin(self.angle + theta)*self.radius

        edge_r_x = r_x + math.cos(self.angle + theta)*self.radius
        edge_r_y = r_y + math.sin(self.angle + theta)*self.radius
        print("theta:",theta)
        print("x:",self.x)
        print("edge_x:",edge_x)
        print("edge_r_x:",edge_r_x)
        
        closest_inter, closest_dist = self.world.raycast(edge_x, edge_y, self.angle + theta, raycast_range)    
        print("Inter:",closest_inter, closest_dist)

        if closest_inter is None:
            return None

        # Define a buffer such that the robot is not placed at exactly the wall
        # This would cause it to stop for one frame and then clip through
        buffer = 1.0e-10

        # Get the intersect x and y
        inter_x = closest_inter[0]
        inter_y = closest_inter[1]

        print("self.xy:", self.x, self.y)
        print("r.xy:", r_x, r_y)
        print("inter.xy:", inter_x, inter_y)

        final_x = None
        final_y = None

        # Check the four possible directions
        if(edge_x >= inter_x and edge_r_x < inter_x): 
            # Collision, move the robot to the collision x point plus some buffer
            # TODO: this is a bit more complex
            print("Collision!")
            self.x = inter_x + self.radius + buffer             
        elif(edge_x <= inter_x and edge_r_x > inter_x):
            # Collision, move the robot to the collision x point plus some buffer
            # TODO: this is a bit more complex
            print("Collision!")
            self.x = inter_x - self.radius - buffer
        else:
            # Get the intersect x and y
            inter_x = closest_inter[0]
            inter_y = closest_inter[1]

            print("self.xy:",self.x, self.y)
            print("r.xy:",r_x,r_y)
            print("inter.xy:",inter_x, inter_y)

            final_x = None
            final_y = None

            # Check the four looking directions
            if(edge_x >= inter_x and edge_r_x < inter_x): 
                # Collision, move the robot to the collision x point plus some buffer
                final_x = inter_x + buffer             
            elif(edge_x <= inter_x and edge_r_x > inter_x):
                # Collision, move the robot to the collision x point plus some buffer
                final_x = inter_x - buffer
            else:
                # No collision with x, set the location to the requested x location of the edge
                final_x = None

            if(edge_y >= inter_y and edge_r_y < inter_y):
                # Collision, move the robot to the collision y point plus some buffer
                final_y = inter_y + buffer 
            elif(edge_y <= inter_y and edge_r_y > inter_y):
                # Collision, move the robot to the collision y point plus some buffer
                final_y = inter_y - buffer
            else:
                # No collision with y, set the location to the requested y location of the edge
                final_y = None

            if(final_x is None and final_y is None):
                # No collision
                return None
            
            # We have a collision
            # Return the collision points with the correct buffer
            return (final_x, final_y)


    def check_collision(self, r_x, r_y):
        n_col_rays = 8 # Ideally powers of 2

        col_ray_angles = np.linspace(0, 2*math.pi, 8, endpoint=False)
        collision = False

        for theta in col_ray_angles:
        # theta = math.pi/4
            collision_point = self.check_collision_edge(theta, r_x, r_y)
            if(collision_point is None):
                # No collision
                continue 
            else:
                # There is a collision, set the location to the corrected collision location
                print("Collision!")
                collision = True
                if(collision_point[0] is None):
                    # No collision here
                    self.x = r_x
                else:
                    self.x = collision_point[0] - math.cos(self.angle + theta)*self.radius
                
                if(collision_point[1] is None):
                    # No collision here
                    self.x = r_x
                else:
                    self.y = collision_point[1] - math.sin(self.angle + theta)*self.radius
                
                # We have a collision break out of the loop
                break

        if(not collision):
            # No collision, set the location to the requested values
            self.x = r_x
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
            