from gui.game import MobileRobotGame
from gui.human_controller import HumanController
from gui.ann_controller import ANNController
from genetic.ANN import ANN
from world_generator import WorldGenerator

if __name__ == "__main__":
    use_human_controller = False
    
    # Setup
    WIDTH = 500
    HEIGHT = 325
    env_params = {
        "env_width": WIDTH,
        "env_height": HEIGHT
    }
    robot_kwargs = {
        "n_sensors": 6
    }
    world_generator = WorldGenerator(WIDTH, HEIGHT, 20, robot_kwargs)
    
    if use_human_controller:
        controller_func = HumanController
    else:
        controller_func = lambda robot: ANNController(
            robot, ANN.load("./checkpoints/model_180.p"))
    
    # Game loop
    while True:
        world, robot = world_generator.create_rect_world(random_robot=False)
        controller = controller_func(robot)
        env_params["world"] = world
        env_params["robot"] = robot
        env_params["robot_controller"] = controller

        game = MobileRobotGame(**env_params)
        game.init()
        game.run()
        
        if not game.reset:
            break
