from gui.game import MyGame
import arcade
import performance
from simulation.World import World, create_rect_wall
from simulation.Robot import Robot

run_performance_test = False

env_params = {
    "env_width" : 1000,
    "env_height": 650
} 

walls = [
    create_rect_wall(env_params["env_width"]/2 + 50, 
    env_params["env_height"]/2 - 100, 100, 50),
    create_rect_wall(env_params["env_width"]/2 - 50, 
    env_params["env_height"]/2 - 100, 150, 100)
]

if __name__ == "__main__":
    world = World(walls)
    robot = Robot(world, env_params["env_width"]/2, env_params["env_height"]/2)
    env_params["world"] = world
    env_params["robot"] = robot

    if not run_performance_test:
        window = MyGame(**env_params)
        arcade.run()
    else:
        performance.stop_time(world, robot, num_steps=10000)