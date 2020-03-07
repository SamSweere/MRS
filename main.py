from gui.game import MobileRobotGame
from gui.human_controller import HumanController
from gui.ann_controller import ANNController
from genetic.ANN import ANN
from world_creator import WorldCreator

if __name__ == "__main__":
    use_human_controller = False
    
    # Setup
    WIDTH = 1000
    HEIGHT = 650
    env_params = {
        "env_width": WIDTH,
        "env_height": HEIGHT
    }
    creator = WorldCreator(WIDTH, HEIGHT)
    
    if use_human_controller:
        controller_func = HumanController
    else:
        controller_func = lambda robot: ANNController(robot, ANN.load("./checkpoints/model_99.p"))
    
    # Game loop
    while True:
        world, robot = creator.create_random_world()
        controller = controller_func(robot)
        env_params["world"] = world
        env_params["robot"] = robot
        env_params["robot_controller"] = controller

        game = MobileRobotGame(**env_params)
        game.init()
        game.run()
        
        if not game.reset:
            break
