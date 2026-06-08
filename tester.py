import arcade
import parser
import warnings
warnings.filterwarnings("ignore")



class Graph(arcade.Window):
    def __init__(self, main_map: parser.Map):
        self.main_map = main_map
        super().__init__()
        self.drone_texture = arcade.load_texture(
            "./images/drone.png"
        )
        self.background_color = arcade.csscolor.DARK_RED
        self.drone = arcade.Sprite(self.drone_texture)
        self.drone.center_x = 100
        self.drone.center_y = 100
        self.all_sprites = arcade.SpriteList()
        self.all_sprites.append(self.drone)

        self.testing_text = None
    def setup(self):
        pass

    def on_draw(self):
        self.clear()
        
        for hub in self.main_map.graph:
            arcade.draw_circle_filled(hub.x * 50, hub.y * 150, 20, hub.color)
        self.all_sprites.draw()
        if self.testing_text is not None:
            arcade.draw_text(self.testing_text, self.width // 2 , self.height // 2 , arcade.csscolor.DARK_VIOLET, 30)        
    def on_mouse_press(self, x, y, button, modifiers):
        self.testing_text =  f"({x}, {y})"


def main():
    main_map = parser.Map(**parser.main_parser())
    print("\033[H\033[2J")
    window = Graph(main_map)
    window.setup()
    arcade.run()


if __name__=="__main__":
    main()
