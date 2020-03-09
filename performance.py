"""Measure performance of our robot"""

from simulation.world_generator import WorldGenerator
import time

def stop_time(world, robot, num_steps=10000):
    start_time = time.time()
    fps_s = time.time()
    for step in range(num_steps):
        robot.update(1000 / 60)

        if(step % 100 == 0):
            fps_e = time.time()
            fps_dif = max(fps_e - fps_s, 1e-10)
            fps = 1.0/(fps_dif / 100)
            print("fps:",fps)
            fps_s = time.time()

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Needed {elapsed_time}s for {num_steps}steps")
    print(f"{num_steps / elapsed_time} steps per second")
    
if __name__ == "__main__":
    WIDTH = 1000
    HEIGHT = 650
    env_params = {
        "env_width": WIDTH,
        "env_height": HEIGHT
    }
    robot_kwargs = {}
    creator = WorldGenerator(WIDTH, HEIGHT, 20, robot_kwargs)
    world, robot = creator.create_random_world()
    
    stop_time(world, robot, num_steps=10000)
    