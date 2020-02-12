"""
Platformer Game
"""
import arcade
from simulation.World import World, create_rect_wall

# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 650
SCREEN_TITLE = "Platformer"


class MyGame(arcade.Window):
    """
    Main application class.
    """

    def __init__(self):

        # Call the parent class and set up the window
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)

    def setup(self):
        """ Set up the game here. Call this function to restart the game. """
        walls = [
            create_rect_wall(SCREEN_WIDTH/2, SCREEN_HEIGHT/2, 100, 50)
        ]
        
        self.world = World(walls)

    def on_draw(self):
        """ Render the screen. """

        arcade.start_render()
        # Code to draw the screen goes here
        for wall in self.world.walls:
            arcade.draw_polygon_filled(wall.points, color=arcade.csscolor.BLACK)
            