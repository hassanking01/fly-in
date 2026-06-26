import arcade
import parser
import warnings
from utils import Map, Drone
from error_classes import ParserError, Grapherror


class SimulationWindow(arcade.Window):
    def __init__(self, main_map: Map) -> None:
        self.main_map = main_map
        self.main_map.compute_costs()
        super().__init__(width=1900, height=1040)
        self.set_location(10, 20)
        self.on_next_turn = False
        self.zoom = 120
        self.cx = self.width // 2 - ((self.main_map.end.x * self.zoom) // 2)
        self.cy = self.height // 2
        self.hub_radius = 20
        self.puase = True
        self.background = arcade.load_texture("./background.jpg")
        self.main_map.scale_and_center_hubs(self.zoom, self.cx, self.cy, 0, 0)
        self.turns = 0
        self.is_sim_end = False

    def setup(self) -> None:
        self.main_map.set_drones()

    def on_update(self, delta_time: float) -> None:
        if not self.puase and not self.is_sim_end:
            all_moved: list[bool] = []
            moved_drones: list[Drone] = []
            for drone in self.main_map.drones:
                all_moved += [drone.finished]
                if drone.finished and drone.next:
                    moved_drones += [drone]
                drone.update()
            if all(all_moved):
                moved_drones = moved_drones[::-1]
                for drone in moved_drones:
                    print(f"{drone.name}-{drone.next.name}", end=" ")
                    if (
                        drone.next.type == "restricted"
                        and drone.first_half
                    ):
                        continue
                    drone.next = None
                print()
                self.turns += 1
                for drone in self.main_map.drones:
                    if drone.next:
                        drone.finished = False
                        continue
                    next = drone.find_next()
                    if next:
                        next.current_drones_count += 1
                        next.on_road += 1
                        if drone.current:
                            drone.current.current_drones_count -= 1
                        drone.can_move = True
                        drone.finished = False
                    drone.next = next
                if self.on_next_turn:
                    self.puase = True
                if all(
                    d.current == self.main_map.end
                    for d in self.main_map.drones
                ):
                    self.is_sim_end = True

    def on_draw(self) -> None:
        self.clear()
        wrct = arcade.rect.XYWH(self.width // 2, self.height // 2, 1920, 1080)
        arcade.draw_texture_rect(self.background, wrct)
        # arcade.draw_text(
        #     f"Turns: {self.turns}",
        #     20,
        #     1000,
        #     arcade.csscolor.SALMON,
        #     font_size=20
        # )
        visited = set()
        for start in self.main_map.graph:
            for end in self.main_map.graph[start]:
                if start.name > end.name:
                    key = f"{start.name}-{end.name}"
                else:
                    key = f"{end.name}-{start.name}"
                if key in visited:
                    continue
                arcade.draw_line(
                    int(start.x),
                    int(start.y),
                    int(end.x),
                    int(end.y),
                    arcade.csscolor.DARK_GRAY,
                    5
                )
                visited.add(key)
        for hub in self.main_map.graph:
            arcade.draw_circle_filled(
                int(hub.x),
                int(hub.y),
                self.hub_radius + 4,
                arcade.csscolor.DARK_GRAY
            )
            arcade.draw_circle_filled(
                hub.x,
                hub.y,
                self.hub_radius,
                hub.color
            )
        for drone in self.main_map.drones:
            arcade.draw_circle_filled(
                drone.x,
                drone.y,
                10,
                drone.color
                )

    def on_mouse_drag(
            self,
            x: int,
            y: int,
            dx: int,
            dy: int,
            buttons: int,
            modifiers: int
            ) -> None:
        self.cx += dx
        self.cy += dy
        self.main_map.scale_and_center_hubs(
            self.zoom,
            self.cx,
            self.cy,
            dx,
            dy
        )

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        if symbol == arcade.key.R and (modifiers & arcade.key.MOD_CTRL):
            self.main_map.reset()
            self.is_sim_end = False
            self.turns = 0

        if symbol == arcade.key.RIGHT:
            if not self.on_next_turn:
                self.on_next_turn = True
            if self.puase:
                self.puase = False
        if symbol == arcade.key.SPACE:
            if self.on_next_turn:
                self.on_next_turn = False
            if self.puase:
                self.puase = False
            else:
                self.puase = True


def main() -> None:
    warnings.filterwarnings("ignore")
    main_map = Map(**parser.main_parser())
    window = SimulationWindow(main_map)
    window.setup()
    arcade.run()


if __name__ == "__main__":
    try:
        main()
    except ParserError as e:
        print(e)
    except Grapherror as e:
        print(e)
    except Exception as e:
        print(e)
    except KeyboardInterrupt:
        print("""
 ▄████  ▄████▄ ▄████▄ ████▄  █████▄ ██  ██ ██████
██  ▄▄▄ ██  ██ ██  ██ ██  ██ ██▄▄██  ▀██▀  ██▄▄
 ▀███▀  ▀████▀ ▀████▀ ████▀  ██▄▄█▀   ██   ██▄▄▄▄
""")
