import pygame
import pygame.gfxdraw
import math
from .fps_counter import FPSCounter
import numpy as np
from gui.dustgrid_sprite import DustGridSprite
from statistics import median


def ti(arr):
    """
    Very short functionname to convert float-arrays to int
    Since pygame doesnt accept floats on its own
    """
    return [int(round(x)) for x in arr]


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

    def __init__(self, env_width, env_height, world, robot):
        self.done = False

        self.env_width = env_width
        self.env_height = env_height
        self.screen_width = env_width
        self.screen_height = env_height
        self.world = world
        self.robot = robot
        self.fps_tracker = FPSCounter()
        self.clock = pygame.time.Clock()
        self.reset = False
        self.v_queue = V_QUEUE()

    def init(self):
        # Initialize pygame and modules that we want to use
        pygame.init()
        pygame.font.init()
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.fps_font = pygame.font.SysFont('Arial', 16)
        self.dust_sprite = DustGridSprite(self.robot, self.world.dustgrid)

    def run(self):
        # Main game loop
        ticks_last_frame = pygame.time.get_ticks()
        while (not self.done and not self.reset):
            self.handle_events()

            # Update
            t = pygame.time.get_ticks()
            delta_time = (t - ticks_last_frame) / 1000.0
            ticks_last_frame = t
            self.update(delta_time)

            self.draw()
            # Pygame uses double buffers
            # This swaps the buffers so everything we've drawn will now show up on the screen
            pygame.display.flip()
            self.fps_tracker.tick()

        pygame.quit()

    def update(self, delta_time):
        self.world.update(delta_time)
        self.dust_sprite.update(delta_time)

    def draw(self):
        self.dust_sprite.draw(self.screen)
        self.__draw_robot__()

        # Draw walls
        for wall in self.world.walls:
            pygame.draw.line(self.screen, pygame.Color('black'), wall.start, wall.end, 1)

        # Draw text displays
        fps = self.fps_tracker.get_fps()
        fps_surface = self.fps_font.render(f"FPS: {fps:3.0f}", False,
                                           pygame.Color('red'))
        self.screen.blit(fps_surface, (30, 20))

        vl_surface = self.fps_font.render(f"Vl: {self.robot.vl}",
                                          False, pygame.Color('red'))
        # print(self.robot.vr)
        # print(self.robot.vl)
        self.screen.blit(vl_surface, (30, 50))
        vr_surface = self.fps_font.render(f"Vr: {self.robot.vr}",
                                          False, pygame.Color('red'))
        self.screen.blit(vr_surface, (30, 70))

        self.v_queue.update(self.robot.v)
        v_surface = self.fps_font.render(f"V: {round(self.v_queue.median() * 500, 1)}",
                                         False, pygame.Color('red'))
        self.screen.blit(v_surface, (30, 90))

        self.screen.blit(v_surface, (30, 90))
        v_test_surface = self.fps_font.render(f"x: {self.robot.x}",
                                              False, pygame.Color('red'))
        self.screen.blit(v_test_surface, (30, 130))

        self.screen.blit(v_surface, (30, 90))
        v_test_surface = self.fps_font.render(f"y: {self.robot.y}",
                                              False, pygame.Color('red'))
        self.screen.blit(v_test_surface, (30, 150))

        self.screen.blit(v_surface, (30, 90))
        v_test_surface = self.fps_font.render(f"angle: {self.robot.angle}",
                                              False, pygame.Color('red'))
        self.screen.blit(v_test_surface, (30, 170))

    def __draw_robot__(self):
        # draw ICC
        R, icc = self.robot.R, self.robot.icc
        if (max(icc) < 10e8 and min(icc) > -10e8):
            # In bounds
            pygame.draw.circle(self.screen, pygame.Color('orange'), ti(icc), 1)

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

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.done = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    self.robot.update_vr(1)
                if event.key == pygame.K_o:
                    self.robot.update_vl(1)
                if event.key == pygame.K_s:
                    self.robot.update_vr(-1)
                if event.key == pygame.K_l:
                    self.robot.update_vl(-1)
                if event.key == pygame.K_SPACE:
                    self.robot.update_vr(1)
                    self.robot.update_vl(1)
                if event.key == pygame.K_x:
                    self.robot.update_vr(0)
                    self.robot.update_vl(0)
                if event.key == pygame.K_r:
                    self.reset = True
