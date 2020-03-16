import pygame
import pygame.gfxdraw
import math
from .fps_counter import FPSCounter
import numpy as np
from gui.dustgrid_sprite import DustGridSprite
from statistics import median
import time


def ti(arr):
    """
    Very short functionname to convert float-arrays to int
    Since pygame doesnt accept floats on its own
    """
    return np.rint(arr).astype(int).tolist()


class V_QUEUE:
    # Class to get the mean q value for printing
    def __init__(self):
        self.v_queue = list()
        self.v_queue_length = 20

    def median(self):
        if (len(self.v_queue) < 1):
            return 0.0

        return median(self.v_queue)

    def update(self, v):
        self.v_queue.insert(0, v)
        if len(self.v_queue) > self.v_queue_length:
            self.dequeue()

    def dequeue(self):
        if len(self.v_queue) > 0:
            return self.v_queue.pop()
        return ("Queue Empty!")


class MobileRobotGame:

    def __init__(self, env_width, env_height, world, robot, robot_controller, scenario, debug=False):
        self.done = False
        self.debug = debug
        self.scenario = scenario

        self.env_width = env_width
        self.env_height = env_height
        self.screen_width = env_width
        self.screen_height = env_height

        self.world = world
        self.robot = robot
        self.robot_controller = robot_controller
        self.start_time = time.time()

        self.fps_tracker = FPSCounter()
        self.reset = False
        self.v_queue = V_QUEUE()

        if scenario == "evolutionary":
            self.robo_lines = [[self.robot.x, self.robot.y, self.robot.x, self.robot.y]]

        if scenario == "localization":
            self.surface = pygame.Surface((env_width, env_height))
            self.surface.fill(pygame.Color('white'))
            self.robo_lines_color = pygame.Color('black')
            self.robo_line_buffer = (self.robot.x, self.robot.y) # This is an faster implementation


    def init(self):
        # Initialize pygame and modules that we want to use
        pygame.init()
        pygame.font.init()
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.fps_font = pygame.font.SysFont('Arial', 16)
        if self.scenario == "evolutionary":
            self.dust_sprite = DustGridSprite(self.robot, self.world.dustgrid)

    def run(self, snapshot=False, snapshot_dir=""):
        # Main game loop
        ticks_last_frame = pygame.time.get_ticks()
        counter = 0
        while (not self.done and not self.reset):
            self.handle_events()

            # Update
            t = pygame.time.get_ticks()
            delta_time = (t - ticks_last_frame) / 1000.0
            ticks_last_frame = t
            self.update(delta_time)

            if snapshot:
                counter += 1
                if counter > 50000:
                    self.draw()
                    pygame.image.save(self.screen, snapshot_dir)
                    pygame.quit()
                    break
            else:
                self.draw()
            # Pygame uses double buffers
            # This swaps the buffers so everything we've drawn will now show up on the screen
            pygame.display.flip()
            self.fps_tracker.tick()

        pygame.quit()

    def update(self, delta_time):
        self.world.update(delta_time)
        self.robot_controller.update(delta_time)
        if self.scenario == "evolutionary":
            self.dust_sprite.update(delta_time)
            self.robo_lines[-1][-2] = self.robot.x
            self.robo_lines[-1][-1] = self.robot.y
            self.robo_lines.append([self.robot.x, self.robot.y, self.robot.x, self.robot.y])


        if self.scenario == "localization": # Not to break the evolutionary part
            pygame.draw.line(self.surface, self.robo_lines_color, self.robo_line_buffer, (self.robot.x, self.robot.y))
            self.robo_line_buffer = (self.robot.x, self.robot.y)





    def draw(self):
        if self.scenario == "evolutionary":
            self.dust_sprite.draw(self.screen)
        elif self.scenario == "localization":
            # Fix the screen updating
            self.screen.blit(self.surface, (0,0), (0,0, self.screen_width, self.screen_height))
            # Draw the beacon lines
            for beacon in self.robot.beacons:
                pygame.draw.line(self.screen, pygame.Color('orange'), beacon[0].location, (self.robot.x, self.robot.y), 2)

        self.__draw_robot__()

        # Draw walls
        for wall in self.world.walls:
            pygame.draw.line(self.screen, pygame.Color('black'), wall.start, wall.end, 1)

        # Draw beacons
        if self.world.beacons is not None:
            for beacon in self.world.beacons:
                pygame.draw.circle(self.screen, pygame.Color('blue'),
                                   (int(beacon.location[0]),int(beacon.location[1])), 5)

        if self.debug:
            # Draw text displays
            text_y = 20
            elapsed_time = time.time() - self.start_time
            time_surface = self.fps_font.render(time.strftime("%M:%S", time.gmtime(elapsed_time)), False,
                                                pygame.Color('red'))
            self.screen.blit(time_surface, (self.env_width - 60, text_y))

            fps = self.fps_tracker.get_fps()
            fps_surface = self.fps_font.render(f"FPS: {fps:3.0f}", False,
                                               pygame.Color('red'))
            self.screen.blit(fps_surface, (30, text_y))

            text_y += 20

            if self.scenario == "evolutionary":
                vl_surface = self.fps_font.render(f"Vl: {round(self.robot.vl, 2)}",
                                                  False, pygame.Color('red'))
                self.screen.blit(vl_surface, (30, text_y))
                text_y += 20
                vr_surface = self.fps_font.render(f"Vr: {round(self.robot.vr, 2)}",
                                                  False, pygame.Color('red'))
                self.screen.blit(vr_surface, (30, text_y))
                text_y += 20

            self.v_queue.update(self.robot.velocity)
            v_surface = self.fps_font.render(f"V: {round(self.v_queue.median() * 500, 1)}",
                                             False, pygame.Color('red'))
            self.screen.blit(v_surface, (30, text_y))
            text_y += 20

            v_test_surface = self.fps_font.render(f"x: {round(self.robot.x, 2)}",
                                                  False, pygame.Color('red'))
            self.screen.blit(v_test_surface, (30, text_y))
            text_y += 20

            v_test_surface = self.fps_font.render(f"y: {round(self.robot.y, 2)}",
                                                  False, pygame.Color('red'))
            self.screen.blit(v_test_surface, (30, text_y))
            text_y += 20

            v_test_surface = self.fps_font.render(f"angle: {round(self.robot.angle, 2)}",
                                                  False, pygame.Color('red'))
            self.screen.blit(v_test_surface, (30, text_y))
            text_y += 20

    def __draw_robot__(self):
        if self.scenario == "evolutionary":
            # draw ICC
            R, icc = self.robot.R, self.robot.icc
            if (max(icc) < 10e8 and min(icc) > -10e8):
                # In bounds
                pygame.draw.circle(self.screen, pygame.Color('orange'), ti(icc), 5)

            # Draw sensors
            for hit, dist in self.robot.sensor_data:
                if hit is None:
                    continue
                pygame.gfxdraw.line(self.screen, *ti((self.robot.x, self.robot.y)), *ti(hit), pygame.Color('red'))

        # Draw the shape of the robot as an circle with an line marking its rotation
        rotated_x = self.robot.x + math.cos(self.robot.angle) * (self.robot.radius - 1)
        rotated_y = self.robot.y + math.sin(self.robot.angle) * (self.robot.radius - 1)

        pygame.gfxdraw.filled_circle(self.screen, *ti((self.robot.x, self.robot.y)), self.robot.radius,
                                     pygame.Color('lightblue'))
        pygame.gfxdraw.line(self.screen, *ti((self.robot.x, self.robot.y)), *ti((rotated_x, rotated_y)),
                            pygame.Color('black'))
        pygame.gfxdraw.circle(self.screen, *ti((self.robot.x, self.robot.y)), self.robot.radius, pygame.Color('black'))

        if self.scenario == "evolutionary":
            for i in self.robo_lines:
                pygame.gfxdraw.line(self.screen, *ti(i), pygame.Color('black'))

    def handle_events(self):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self.done = True
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.reset = True
                    return
                if event.key == pygame.K_t:
                    self.debug = not self.debug

        self.robot_controller.handle_events(events)
