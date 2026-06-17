import arcade
import parser
import warnings
from utils import Map, Hub, Drone
import os


class Graph(arcade.Window):
    def __init__(self, main_map: Map):
        self.main_map = main_map
        self.main_map.find_path()

        super().__init__(width=1920, height=1010)
        self.drone_texture = arcade.load_texture(
            "./images/drone.png"
        )
        self.background_color = arcade.csscolor.DARK_GOLDENROD
        self.drone = arcade.Sprite(self.drone_texture)
        self.drone.center_x = 100
        self.drone.center_y = 100
        self.all_sprites = arcade.SpriteList()
        self.all_sprites.append(self.drone)
        self.cx = self.width // 2
        self.cy = self.height // 2

        # TODO remove this is just for debugging and uncomment the real cx cy
        # self.cx = ((self.width // 2) // 2) // 2
        # self.cy = ((self.height // 2 ) // 2) 
        # self.set_location(900  , 0)

        self.zoom =  150
        self.hub_radius = 20
        self.puase = True
        self.sec = 0
        self.speed = 2
        self.background = arcade.load_texture("./background.jpg")
        self.main_map.scale_and_center_hubs(self.zoom, self.cx, self.cy, 0 ,0)
        self.turns = 0

    def setup(self):
        self.main_map.set_drones(all_moved=True)
    def on_update(self, delta_time):
        if not self.puase:
            all_moved = []
            drones_to_find_next: list[Drone] = []
            for drone in self.main_map.drones:

                if drone.next:
                    if drone.next.current_drones_count < drone.next.max_drones:
                        drone.can_move = True
                        if not drone.reserve_spot:
                            drone.finished = False
                            drone.current.current_drones_count -= 1
                            drone.next.current_drones_count += 1
                            drone.reserve_spot = True
                else:
                    drones_to_find_next += [drone]
                    continue
                all_moved += [drone.finished]
                drone.update()
            is_all_moved = all(all_moved)

            if is_all_moved:
                print("\n", "===" * 20)
                for drone in drones_to_find_next:
                    next = drone.find_next(is_all_moved)
                    if next:
                        if next.current_drones_count < next.max_drones:
                            next.current_drones_count += 1
                            drone.current.current_drones_count -= 1
                            drone.can_move = True
                            drone.reserve_spot = True
                            drone.finished = False
                        else:
                            next = None
                    drone.next = next
                # self.puase = True
                for key in self.main_map.graph:
                    print(key.name, [drone.name for drone in key.drone_in], key.current_drones_count)
                for done in self.main_map.drones:
                    print(done.name , drone.current.name , drone.next.name if drone.next else None)

    def on_draw(self):
        self.clear()
        wrct = arcade.rect.XYWH(self.width // 2 , self.height // 2, 1920, 1080)
        arcade.draw_texture_rect(self.background, wrct)
        for start in self.main_map.graph:
            for end in self.main_map.graph[start]:
                arcade.draw_line(
                    int(start.x) ,
                    int(start.y) ,
                    int(end.x) ,
                    int(end.y) ,
                    arcade.csscolor.DARK_GRAY,
                    5
                )
        for hub in self.main_map.graph:
            arcade.draw_circle_filled(int(hub.x) , int(hub.y) , self.hub_radius + 4, arcade.csscolor.DARK_GRAY)
            arcade.draw_circle_filled(int(hub.x) , int(hub.y) , self.hub_radius, hub.color)
            label = arcade.Text(f"{hub.name}:{hub.type}", int(hub.x), int(hub.y) + 20, arcade.csscolor.DARK_BLUE, anchor_x='center',font_name="Liberation Sans",font_size=10 )
            label.draw()

        for drone in self.main_map.drones:
            arcade.draw_circle_filled(
                drone.x ,
                drone.y,
                10,
                drone.color
                )
            label = arcade.Text(f"{drone.name}", int(drone.x), int(drone.y) - 20, arcade.csscolor.DARK_BLUE, anchor_x='center',font_name="Liberation Sans",font_size=10 )
            label.draw()
        
    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.cx += dx
        self.cy += dy
        self.main_map.scale_and_center_hubs(self.zoom, self.cx, self.cy, dx, dy)

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.R and (modifiers & arcade.key.MOD_CTRL):
            self.main_map.reset()

        if symbol == arcade.key.RIGHT:
            self.puase = False                
        if symbol == arcade.key.SPACE:
            if self.puase:
                self.puase = False
            else:
                self.puase = True
        if symbol == arcade.key.UP:
            self.speed -= 1
        if symbol == arcade.key.DOWN:
            self.speed += 1

def main():
    warnings.filterwarnings("ignore")
    main_map = Map(**parser.main_parser())
    window = Graph(main_map)
    window.setup()
    arcade.run()


if __name__=="__main__":
    main()
