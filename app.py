import arcade
import parser
import warnings
from utils import Map, Hub, Drone
import os


class Graph(arcade.Window):
    def __init__(self, main_map: Map):
        self.main_map = main_map
        self.main_map.find_path()
        super().__init__(width=1900, height=1040)
        self.drone_texture = arcade.load_texture(
            "./images/drone.png"
        )
        self.set_location(10,20)
        self.on_next_turn = False
        self.background_color = arcade.csscolor.DARK_GOLDENROD
        self.zoom =  80
        self.cx = self.width // 2 - ((self.main_map.end.x * self.zoom ) // 2)
        self.cy = self.height // 2
        self.hub_radius = 20
        self.puase = True
        self.sec = 0
        self.speed = 2
        self.background = arcade.load_texture("./background.jpg")
        self.main_map.scale_and_center_hubs(self.zoom, self.cx, self.cy, 0 ,0)
        self.turns = 0

    def setup(self):
        self.main_map.set_drones()
    def on_update(self, delta_time):
        if not self.puase:
            all_moved = []
            drones_to_find_next: list[Drone] = []
            for drone in self.main_map.drones:
                if not drone.next:
                    drones_to_find_next += [drone]
                    continue
                all_moved += [drone.finished]
                drone.update()
            is_all_moved = all(all_moved)

            if is_all_moved:
                print("\n", "===" * 20)
                self.turns += 1
                for drone in drones_to_find_next:
                    next = drone.find_next(is_all_moved)
                    if next:
                        if next.current_drones_count < next.max_drones and next.on_road < 1:
                            next.current_drones_count += 1
                            next.on_road += 1
                            drone.current.current_drones_count -= 1
                            drone.can_move = True
                            drone.reserve_spot = True
                            drone.finished = False
                    drone.next = next
                if self.on_next_turn:
                    self.puase = True                
                for key in self.main_map.graph:
                    print(key.name, [drone.name for drone in key.drone_in], key.current_drones_count)
                # for done in self.main_map.drones:
                #     print(done.name , drone.current.name , drone.next.name if drone.next else None)

    def on_draw(self):
        self.clear()
        wrct = arcade.rect.XYWH(self.width // 2 , self.height // 2, 1920, 1080)
        arcade.draw_texture_rect(self.background, wrct)
        arcade.draw_text(f"Truns: {self.turns}", 20 , 1000 , arcade.csscolor.SALMON, font_size=20)
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
            # arcade.draw_text(f"{hub.name} [{hub.max_drones}]", hub.x, hub.y + 20 , arcade.csscolor.ORANGE_RED, width=30)
        for drone in self.main_map.drones:
            arcade.draw_circle_filled(
                drone.x ,
                drone.y,
                10,
                drone.color
                )
                
    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.cx += dx
        self.cy += dy
        self.main_map.scale_and_center_hubs(self.zoom, self.cx, self.cy, dx, dy)

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.R and (modifiers & arcade.key.MOD_CTRL):
            self.main_map.reset()

        if symbol == arcade.key.RIGHT:
            if not self.on_next_turn:
                self.on_next_turn = True
            self.puase = False                
        if symbol == arcade.key.SPACE:
            if self.on_next_turn:
                self.on_next_turn = False
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
