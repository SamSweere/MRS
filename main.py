from gui.game import MyGame
import arcade

if __name__ == "__main__":
    window = MyGame()
    window.setup()
    arcade.run()