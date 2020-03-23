import pygame

# Draws a dashed curve
# Works by using the fraction variable to keep track of the dash strokes
# fraction from 0 to 1 means dash
# fraction from 1 to 2 means no dash
def draw_dashed_curve(surf, color, start, end, fraction, width=1, dash_length=10):
    start = pygame.Vector2(start)
    end = pygame.Vector2(end)
    
    delta = end - start
    length = delta.length()
    if length < 0.0000001:
        return fraction + length
    
    new_fraction = fraction + length / dash_length
    slope = delta / length
    if fraction < 1:
        end = start + slope * (length  / dash_length)
        pygame.gfxdraw.line(surf, int(start.x), int(start.y), int(end.x), int(end.y), color)
    elif new_fraction > 2:
        start = start + slope * (fraction - 2)
        pygame.gfxdraw.line(surf, int(start.x), int(start.y), int(end.x), int(end.y), color)
        new_fraction = new_fraction - 2
    
    return new_fraction

class LocalizationPath:
    def __init__(self, game):
        self.game = game
        self.robot = game.robot
        self.localizer = self.robot.localizer
        
        self.path_surface = pygame.Surface((game.screen_width, game.screen_height), pygame.SRCALPHA)
        self.path_color = pygame.Color('orange')
        self.old_pos = (self.localizer.state_mu[0][0], self.localizer.state_mu[1][1])
        self.passed_time = 0
        self.dash_fraction = 0

    def update(self, delta_time):
        new_pos = (self.localizer.state_mu[0][0], self.localizer.state_mu[1][1])
        self.dash_fraction = draw_dashed_curve(surf=self.path_surface, color=self.path_color, start=self.old_pos, end=new_pos,
                                               fraction=self.dash_fraction, width=2)
        self.old_pos = new_pos
        
        # Store the freeze the uncertainty ellipse after a set amount of time
        self.passed_time += delta_time
        if self.passed_time > 2:
            self.__draw_uncertainty_ellipse__(self.path_surface)
            self.passed_time = 0
    
    def draw(self, surface):
        surface.blit(self.path_surface, (0,0), (0,0, self.game.screen_width, self.game.screen_height))
        #self.__draw_uncertainty_ellipse__(surface)
        
    def __draw_uncertainty_ellipse__(self, surface):
        x_mu = self.localizer.state_mu[0][0]
        y_mu = self.localizer.state_mu[1][1]
        x_std = self.localizer.state_std[0,0]
        y_std = self.localizer.state_std[1,1]
        
        pygame.gfxdraw.ellipse(surface, int(x_mu), int(y_mu), int(x_std), int(y_std), self.path_color)