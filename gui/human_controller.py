import pygame
import numpy as np

class HumanController:
    def __init__(self, robot):
        self.robot = robot
        
    def update(self, delta_time):
        pass
                    
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
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