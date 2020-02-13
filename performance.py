from simulation.World import World, create_rect_wall
from simulation.Robot import Robot
import time

def stop_time(world, robot, num_steps=10000):
    start_time = time.time()
    for step in range(num_steps):
        robot.update()
        
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Needed {elapsed_time}s for {num_steps}steps")
    print(f"{num_steps / elapsed_time} steps per second")
    