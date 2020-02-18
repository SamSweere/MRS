import pygame
import pygame.gfxdraw
import math
from .fps_counter import FPSCounter
import numpy as np

def ti(arr):
    """
    Very short functionname to convert float-arrays to int
    Since pygame doesnt accept floats on its own
    """
    return [int(round(x)) for x in arr]


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
        self.reset = False
        

    def init(self):
        # Initialize pygame and modules that we want to use
        pygame.init()
        pygame.font.init()        
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.fps_font = pygame.font.SysFont('Arial', 16)
    

    def run(self):
        # Main game loop
        ticks_last_frame = pygame.time.get_ticks()
        while (not self.done and not self.reset):
            self.handle_events()
            
            # Update
            t = pygame.time.get_ticks()
            deltaTime = (t - ticks_last_frame) / 1000.0
            ticks_last_frame = t
                
            self.update(deltaTime)
            
            self.screen.fill(pygame.Color('white'))
            self.draw()
            # Pygame uses double buffers
            # This swaps the buffers so everything we've drawn will now show up on the screen
            pygame.display.flip()            
            self.fps_tracker.tick()

        pygame.quit()

            
    def update(self, delta_time):
        self.robot.update(delta_time)
    
    def draw(self):
        self.__draw_robot__()
        
        for wall in self.world.walls:  # Draw walls
            if(len(wall.points) == 2):
                # This is a line
                pygame.draw.line(self.screen, pygame.Color('black'), wall.points[0], wall.points[1], 1)
            else:
                # This is a polygon
                pygame.draw.polygon(self.screen, pygame.Color('black'), wall.points)
        
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
        v_surface = self.fps_font.render(f"V: {self.robot.v}",
                                          False, pygame.Color('red'))
        self.screen.blit(v_surface, (30, 90))
        v_test_surface = self.fps_font.render(f"V_abs: {self.robot.v_test}",
                                         False, pygame.Color('red'))
        self.screen.blit(v_test_surface, (30, 110))

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
        if(max(icc) < 10e8 and min(icc) > -10e8):
            # In bounds
            pygame.draw.circle(self.screen, pygame.Color('green'), ti(icc), 1)

        # Draw sensors
        for hit, dist in self.robot.sensor_data:
            if hit is None:
                continue
            pygame.gfxdraw.line(self.screen, *ti((self.robot.x, self.robot.y)), *ti(hit), pygame.Color('red'))

        # Draw the shape of the robot as an circle with an line marking its rotation
        rotated_x = self.robot.x + math.cos(self.robot.angle) * (self.robot.radius - 1)
        rotated_y = self.robot.y + math.sin(self.robot.angle) * (self.robot.radius - 1)
        
        pygame.gfxdraw.filled_circle(self.screen, *ti((self.robot.x, self.robot.y)), self.robot.radius, pygame.Color('lightblue'))
        pygame.gfxdraw.line(self.screen, *ti((self.robot.x, self.robot.y)), *ti((rotated_x, rotated_y)), pygame.Color('black'))
        pygame.gfxdraw.circle(self.screen, *ti((self.robot.x, self.robot.y)), self.robot.radius, pygame.Color('black'))
        
    
    def handle_events(self):
        speed = 10
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.done = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    self.robot.vr += speed
                if event.key == pygame.K_o:
                    self.robot.vl += speed
                if event.key == pygame.K_s:
                    self.robot.vr += -speed
                if event.key == pygame.K_l:
                    self.robot.vl += -speed
                if event.key == pygame.K_SPACE:
                    self.robot.vr += speed
                    self.robot.vl += speed
                if event.key == pygame.K_x:
                    self.robot.vr = 0
                    self.robot.vl = 0
                if event.key == pygame.K_r:
                    self.reset = True
            