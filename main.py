from gui.game import MobileRobotGame
import performance
from simulation.world import World, create_rect_walls
from simulation.line_wall import LineWall
from simulation.robot import Robot
from world_creator import WorldCreator
import numpy as np

run_performance_test = False

WIDTH = 1000
HEIGHT = 650
env_params = {
    "env_width" : WIDTH,
    "env_height": HEIGHT
} 

margin = 10

walls = [
    *create_rect_walls(env_params["env_width"]/2 + 50,
        env_params["env_height"]/2 - 100, 100, 50),
    *create_rect_walls(env_params["env_width"]/2 - 50,
        env_params["env_height"]/2 - 100, 150, 100),
    *create_rect_walls(WIDTH / 2, HEIGHT / 2, WIDTH, HEIGHT)
]


if __name__ == "__main__":
    reset = True
    while reset:
        robot = Robot(620, 100, 1.15*np.pi)
        world = World(walls, robot, WIDTH, HEIGHT)
        env_params["world"] = world
        env_params["robot"] = robot
        
        # ToDo Enable later when everything works correctly
        #creator = WorldCreator(WIDTH, HEIGHT)
        #world, robot = creator.create_star_world()
        #env_params["world"] = world
        #env_params["robot"] = robot

        if not run_performance_test:
            game = MobileRobotGame(**env_params)
            game.init()
            game.run()
            if game.reset:
                reset = True
            else:
                reset = False
        else:
            performance.stop_time(world, robot, num_steps=10000)
            reset = False