from gui.game import MyGame
import arcade

environment_params = {
        "environment_width" : 1000,
        "environment_height": 650
    }    

if __name__ == "__main__":    
    window = MyGame(**environment_params)
    window.setup()
    arcade.run()