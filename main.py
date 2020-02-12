from gui.game import MyGame
import arcade
from simulation.World import World, create_rect_wall
from simulation.Robot import Robot

env_params = {
    "env_width" : 1000,
    "env_height": 650
} 

env_params["walls"] = [create_rect_wall(env_params["env_width"]/2 - 200, 
    env_params["env_height"]/2 - 200, 100, 50)]

env_params["robot"] = Robot(env_params["env_width"]/2, env_params["env_height"]/2)

if __name__ == "__main__":    
    window = MyGame(**env_params)
    arcade.run()