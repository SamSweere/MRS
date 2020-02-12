"""
Platformer Game
"""
import arcade
import math
from simulation.World import World, create_rect_wall
from simulation.Robot import Robot

# Constants
SCREEN_TITLE = "Platformer"

MOVEMENT_SPEED = 5
ANGLE_SPEED = 5 # This is in degrees

class MyGame(arcade.Window):
    """
    Main application class.
    """

    def __init__(self, environment_width, environment_height):
        self.SCREEN_WIDTH = environment_width
        self.SCREEN_HEIGHT = environment_height

        # Call the parent class and set up the window
        super().__init__(self.SCREEN_WIDTH, self.SCREEN_HEIGHT, SCREEN_TITLE)

        arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)

    def setup(self):
        """ Set up the game here. Call this function to restart the game. """
        walls = [
            create_rect_wall(self.SCREEN_WIDTH/2 - 200 , self.SCREEN_HEIGHT/2 - 200, 100, 50)
        ]
        self.robot = Robot(self.SCREEN_WIDTH/2, self.SCREEN_HEIGHT/2)
        self.world = World(walls, self.robot)

    def on_draw(self):
        """ Render the screen. """

        arcade.start_render()
        
        for wall in self.world.walls:
            arcade.draw_polygon_filled(wall.points, color=arcade.csscolor.BLACK)
            
        self.__draw_robot__()

    def on_update(self, delta_time):
        """ Movement and game logic """

        # Call the updates of all the moving parts
        self.robot.update()
        
    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """

        # Forward/back
        if key == arcade.key.UP:
            self.robot.speed = MOVEMENT_SPEED
        elif key == arcade.key.DOWN:
            self.robot.speed = -MOVEMENT_SPEED

        # Rotate left/right
        elif key == arcade.key.LEFT:
            self.robot.change_angle += ANGLE_SPEED
        elif key == arcade.key.RIGHT:
            self.robot.change_angle -= ANGLE_SPEED

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key. """

        if key == arcade.key.UP or key == arcade.key.DOWN:
            self.robot.speed = 0
        elif key == arcade.key.LEFT or key == arcade.key.RIGHT:
            self.robot.change_angle = 0

    def __draw_robot__(self):       
        # Draw the shape of the robot as an circle with an line marking its rotation
        old_x = self.robot.radius
        old_y = 0

        angle_rad = math.radians(self.robot.angle)

        rotated_x = self.robot.x + math.cos(angle_rad) * old_x - math.sin(angle_rad) * old_y
        rotated_y = self.robot.y + math.sin(angle_rad) * old_x + math.cos(angle_rad) * old_y
        
        arcade.draw_circle_outline(self.robot.x, self.robot.y, self.robot.radius, color=arcade.csscolor.BLACK)
        arcade.draw_line(self.robot.x, self.robot.y, rotated_x, rotated_y, color=arcade.csscolor.BLACK)
        
        
            