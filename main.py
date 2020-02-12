from gui.game import MyGame
import arcade
from simulation.World import World, create_rect_wall
from simulation.Robot import Robot

env_params = {
    "env_width" : 1000,
    "env_height": 650
} 

walls = [create_rect_wall(env_params["env_width"]/2 - 200, 
    env_params["env_height"]/2 - 200, 100, 50), create_rect_wall(env_params["env_width"]/2 - 280, 
    env_params["env_height"]/2 - 200, 150, 100)]

if __name__ == "__main__":
    world = World(walls)
    robot = Robot(world, env_params["env_width"]/2, env_params["env_height"]/2)
    env_params["world"] = world
    env_params["robot"] = robot

    window = MyGame(**env_params)
    arcade.run()