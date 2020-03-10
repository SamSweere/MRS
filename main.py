from gui.game import MobileRobotGame
from gui.human_controller import HumanController
from gui.ann_controller import ANNController
from genetic.ANN import ANN
from simulation.world_generator import WorldGenerator
import argparse
import os

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--human", action="store_true", default=False,
                        help="manual robot control")
    parser.add_argument("--model_name", default="model_320.p",
                        help="robot control model name in checkpoints")
    parser.add_argument("--world_name", default="random",
                        help="world name of the environment, options: rect_world, double_rect_world, trapezoid_world, "
                             "double_trapezoid_world, star_world, random")
    parser.add_argument("--snapshot", action="store_true", default=False,
                        help="take a snapshot")
    parser.add_argument("--snapshot_dir", default="_snapshots/latest.png",
                        help="file name for snapshot")
    # TODO: take a snapshot & store
    args = parser.parse_args()

    use_human_controller = args.human

    # set up environment
    WIDTH = 400
    HEIGHT = 400
    env_params = {"env_width": WIDTH, "env_height": HEIGHT}
    robot_kwargs = {"n_sensors": 12}
    world_generator = WorldGenerator(WIDTH, HEIGHT, 20, args.world_name)

    if use_human_controller:
        controller_func = HumanController
    else:
        model_path = os.path.join("_checkpoints", args.model_name)
        controller_func = lambda robot: ANNController(
            robot, ANN.load(model_path))

    # Game loop
    while True:
        world, robot = world_generator.create_world(random_robot=True)

        controller = controller_func(robot)
        env_params["world"] = world
        env_params["robot"] = robot
        env_params["robot_controller"] = controller

        game = MobileRobotGame(**env_params)
        game.init()
        game.run()

        if not game.reset:
            break
