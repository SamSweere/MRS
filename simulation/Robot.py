import numpy as np
import math

class Robot:
    def __init__(self, world, start_x, start_y, radius=20, 
                movement_speed=5, angle_speed=(5*math.pi/180), n_ray_cast = 10):
        self.world = world
        self.x = start_x
        self.y = start_y
        self.radius = radius
        self.movement_speed = 5 
        self.angle_speed = angle_speed # This is in radians
        self.n_ray_cast = n_ray_cast # The amount of raycasts it does
        
        self.change_angle = 0
        self.speed = 0
        self.angle = 0 # In radians

    def update(self):
        # Rotate the robot
        self.angle += self.change_angle * self.angle_speed

        # Based on the speed and the angle find the new requested location
        r_x = self.x + self.speed * self.movement_speed * math.cos(self.angle)
        r_y = self.y + self.speed * self.movement_speed * math.sin(self.angle)
        
        # Check for collision, this function also sets the new x and y values
        self.check_collision(r_x, r_y)       
        

    def check_collision(self, r_x, r_y):
        raycast_range = 200
        closest_inter, closest_dist = self.world.raycast(self.x, self.y, self.angle, raycast_range)    
        print(closest_inter, closest_dist)

        if(closest_inter == None):
            # No collision, set the new x and y based on the requested values
            self.x = r_x
            self.y = r_y
        # elif()
        