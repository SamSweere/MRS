from gui.game import MobileRobotGame
import performance
from simulation.world import World
from simulation.line_wall import LineWall
from simulation.robot import Robot
from world_creator import WorldCreator, create_rect_walls
import numpy as np

run_performance_test = False

WIDTH = 1000
HEIGHT = 650
env_params = {
    "env_width": WIDTH,
    "env_height": HEIGHT
}

margin = 10

if __name__ == "__main__":
    reset = True
    while reset:
        creator = WorldCreator(WIDTH, HEIGHT)
        world, robot = creator.create_random_world()
        env_params["world"] = world
        env_params["robot"] = robot

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
