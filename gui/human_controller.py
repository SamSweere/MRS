import math

import pygame
import numpy as np

class HumanController:
    def __init__(self, robot, scenario):
        self.robot = robot
        self.scenario = scenario
        
    def update(self, delta_time):
        pass
                    
    def handle_events(self, events):
        for event in events:
            if self.scenario == "evolutionary":
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
            elif self.scenario == "localization":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_w or event.key == pygame.K_UP:
                        # Set a big number, will be limited by max v
                        self.robot.update_v(1000)
                    if event.key == pygame.K_s or event.key == pygame.K_DOWN:
                        self.robot.update_v(-1000)
                    if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                        self.robot.rotate_left = True
                        # self.robot.update_angle(-1)
                    if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                        self.robot.rotate_right = True
                        # self.robot.update_angle(1)
                if event.type == pygame.KEYUP:
                    # Stop
                    if event.key == pygame.K_w or event.key == pygame.K_UP:
                        self.robot.update_v(0)
                    if event.key == pygame.K_s or event.key == pygame.K_DOWN:
                        self.robot.update_v(0)
                    if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                        self.robot.rotate_left = False
                        # self.robot.update_angle(0)
                    if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                        self.robot.rotate_right = False
                        # self.robot.update_angle(0)