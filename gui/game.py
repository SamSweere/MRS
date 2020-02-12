"""
Platformer Game
"""
import arcade
import numpy as np
from simulation import World

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
        # self.world = 

    def on_draw(self):
        """ Render the screen. """

        arcade.start_render()
        arcade.draw_polygon_filled(np.array([[20,20],[30,30],[20,30]]), color=arcade.csscolor.BLACK)
        # Code to draw the screen goes here
