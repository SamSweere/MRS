import pygame
import numpy as np

class LocalizationPath:
    def __init__(self, game):
        self.game = game
        self.robot = game.robot
        self.localizer = self.robot.localizer
        
        self.path_surface = pygame.Surface((game.screen_width, game.screen_height), pygame.SRCALPHA)
        self.path_color = pygame.Color('orange')
        self.old_pos = (self.localizer.state_mu[0], self.localizer.state_mu[1])

    def update(self, delta_time):
        new_pos = (self.localizer.state_mu[0], self.localizer.state_mu[1])
        pygame.draw.line(self.path_surface, self.path_color, self.old_pos, new_pos, 1)
        self.old_pos = new_pos
    
    def draw(self, surface):
        surface.blit(self.path_surface, (0,0), (0,0, self.game.screen_width, self.game.screen_height))
        self.path_surface.set_at((0,0), pygame.Color('red'))