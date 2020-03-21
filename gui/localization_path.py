import pygame

class LocalizationPath:
    def __init__(self, game):
        self.game = game
        self.robot = game.robot
        self.localizer = self.robot.localizer
        
        self.path_surface = pygame.Surface((game.screen_width, game.screen_height), pygame.SRCALPHA)
        self.path_color = pygame.Color('orange')
        self.old_pos = (self.localizer.state_mu[0], self.localizer.state_mu[1])
        self.passed_time = 0

    def update(self, delta_time):
        new_pos = (self.localizer.state_mu[0], self.localizer.state_mu[1])
        pygame.draw.line(self.path_surface, self.path_color, self.old_pos, new_pos, 1)
        self.old_pos = new_pos
        
        # Store the freeze the uncertainty ellipse after a set amount of time
        self.passed_time += delta_time
        if self.passed_time > 2:
            self.__draw_uncertainty_ellipse__(self.path_surface)
            self.passed_time = 0
    
    def draw(self, surface):
        surface.blit(self.path_surface, (0,0), (0,0, self.game.screen_width, self.game.screen_height))
        
        self.__draw_uncertainty_ellipse__(surface)
        
    def __draw_uncertainty_ellipse__(self, surface):
        x_mu = self.localizer.state_mu[0]
        y_mu = self.localizer.state_mu[1]
        x_std = self.localizer.state_std[0,0]
        y_std = self.localizer.state_std[1,1]
        
        pygame.gfxdraw.ellipse(surface, int(x_mu), int(y_mu), int(x_std), int(y_std), self.path_color)