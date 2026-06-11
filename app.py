import arcade
import parser
import warnings
warnings.filterwarnings("ignore")



class Graph(arcade.Window):
    def __init__(self, main_map: parser.Map):
        self.main_map = main_map
        self.main_map.find_path()

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
        self.cx = self.width // 2
        self.cy = self.height // 2 
        self.zoom =  150
        self.main_map.scale_and_center_hubs(self.zoom, self.cx, self.cy)
        self.hub_radius = 20
        self.puase = True
        self.sec = 0
        self.speed = 1
    def setup(self):
        pass
    
    def on_update(self, delta_time):
        self.sec += delta_time
        if self.sec >= self.speed:
            self.sec  = 0         
            if not self.puase:
                for drone in self.main_map.drones:
                    drone.update(self.zoom, self.cx, self.cy)

    def on_draw(self):
        self.clear()
        
        for start in self.main_map.graph:
            for end in self.main_map.graph[start]:
                arcade.draw_line(
                    start.x ,
                    start.y ,
                    end.x ,
                    end.y ,
                    arcade.csscolor.GRAY,
                    3
                )  
        for hub in self.main_map.graph:
            arcade.draw_circle_filled(hub.x , hub.y , self.hub_radius, hub.color)
            arcade.draw_text(hub.name, hub.x , hub.y + 20, arcade.csscolor.DARK_BLUE, anchor_x='center')
        for drone in self.main_map.drones:
            arcade.draw_circle_filled(
                drone.x ,
                drone.y ,
                10,
                drone.color
                )
    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        if scroll_y < 0:
            if self.zoom > 10:
                self.zoom -= 5
                self.hub_radius -= 0.5
        else:
            self.zoom += 5
            if self.hub_radius <20:
                self.hub_radius += 0.5
        self.main_map.scale_and_center_hubs(self.zoom, self.cx, self.cy)
        
    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.cx += dx
        self.cy += dy
        self.main_map.scale_and_center_hubs(self.zoom, self.cx, self.cy)

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.SPACE:
            if self.puase:
                self.puase = False
            else:
                self.puase = True
        if symbol == arcade.key.UP:
            self.speed -= 0.1
        if symbol == arcade.key.DOWN:
            self.speed += 0.1

def main():
    main_map = parser.Map(**parser.main_parser())
    print("\033[H\033[2J")
    window = Graph(main_map)
    window.setup()
    arcade.run()


if __name__=="__main__":
    main()
