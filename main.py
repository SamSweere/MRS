from gui.game import MobileRobotGame
import performance
from simulation.world import World, create_rect_wall, create_line_wall
from simulation.polygon_wall import PolygonWall
from simulation.robot import Robot
import numpy as np

run_performance_test = False

WIDTH = 1000
HEIGHT = 650
env_params = {
    "env_width" : WIDTH,
    "env_height": HEIGHT
} 

margin = 10

# walls = [
#     # create_line_wall((500,-100),(500,20000))
#     create_line_wall((0,100),(1000,100))
# ]

# walls = [
#     create_line_wall((500,100),(500,300))
# ]

# walls = [
#     create_rect_wall(490,
#         200, 20, 200),
# ]

# walls = [
#     create_rect_wall(600,200, 200, 200),
# ]

walls = [
    create_rect_wall(env_params["env_width"]/2 + 50,
        env_params["env_height"]/2 - 100, 100, 50),
    create_rect_wall(env_params["env_width"]/2 - 50,
        env_params["env_height"]/2 - 100, 150, 100),
]

border_left = PolygonWall(np.array([
    [margin, margin],
    [margin, HEIGHT-margin*2],
    [margin*2, HEIGHT-margin*2],
    [margin*2, margin]
]))
walls.append(border_left)

border_right = PolygonWall(np.array([
    [WIDTH-margin*2, margin],
    [WIDTH-margin*2, HEIGHT-margin*2],
    [WIDTH-margin, HEIGHT-margin*2],
    [WIDTH-margin, margin]
]))
walls.append(border_right)

border_bottom = PolygonWall(np.array([
    [margin, HEIGHT-margin*2],
    [margin, HEIGHT-margin],
    [WIDTH-margin, HEIGHT-margin],
    [WIDTH-margin, HEIGHT-margin*2],
]))
walls.append(border_bottom)

border_top = PolygonWall(np.array([
    [margin, margin],
    [margin, margin*2],
    [WIDTH-margin, margin*2],
    [WIDTH-margin, margin],
]))
walls.append(border_top)


if __name__ == "__main__":
    reset = True
    while reset:
        world = World(walls)
        robot = Robot(world, 620, 145, 2.847)
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