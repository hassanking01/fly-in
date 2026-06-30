import arcade
from parser import Parser
import warnings
from utils import Map, Drone
from error_classes import ParserError, Grapherror, Errors
import math
import sys
from rich.panel import Panel
from rich.console import Console
from rich.traceback import install


install()


class SimulationWindow(arcade.View):
    def __init__(self, main_map: Map) -> None:
        self.camera = arcade.camera.Camera2D()
        self.main_map = main_map
        super().__init__()
        self.on_next_turn = False
        self.console = Console()
        self.zoom = 100
        self.cx = self.width // 2 - ((self.main_map.end.x * self.zoom) // 2)
        self.cy = self.height // 2
        self.camera.position = (self.cx, self.cy)
        self.hub_radius = 30
        self.puase = True
        self.background = arcade.load_texture("./background.jpg")
        self.main_map.scale_and_center_hubs(self.zoom, self.cx, self.cy)
        self.turns = 0
        self.is_sim_end = False
        self.current_zoom = 1.0
        self.debug = False

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        self.current_zoom += scroll_y * 0.1
        self.current_zoom = max(0.6, min(5.0, self.current_zoom))
        self.camera.zoom = self.current_zoom

    def setup(self) -> None:
        self.main_map.set_drones()

    def print_turns(self, moved_drones: list[Drone]):
        line = "[cyan]"
        for drone in moved_drones:
            if drone.next.type == "restricted" and drone.first_half:
                line += f"{drone.name}-{drone.current.name}-{drone.next.name} "
                continue
            else:
                line += f"{drone.name}-{drone.next.name} "
            drone.next = None
        line += "[/cyan]"
        panel = Panel(
            line,
            title=f"[bold yellow]TURN {self.turns}[/bold yellow]",
            border_style="red",
        )
        self.console.print(panel)

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
                self.turns += 1
                self.print_turns(moved_drones[::-1])
                for drone in self.main_map.drones:
                    if drone.next:
                        drone.finished = False
                        continue
                    next = drone.find_next(self.turns)
                    if next:
                        next.current_drones_count += 1
                        next.connections[drone.current]["on_road"] += 1
                        if drone.current:
                            drone.current.current_drones_count -= 1
                        drone.can_move = True
                        drone.finished = False
                    drone.next = next
                if self.on_next_turn:
                    self.puase = True
                self.is_sim_end = all(
                    drone.current.is_goal_hub for drone in self.main_map.drones
                )

    def on_draw(self) -> None:
        self.clear()
        wrct = arcade.rect.XYWH(self.width // 2, self.height // 2, 1920, 1080)
        arcade.draw_texture_rect(self.background, wrct)
        arcade.draw_text(
            f"Turns: {self.turns}",
            0,
            0,
            arcade.csscolor.SALMON,
            font_size=20,
            font_name="Black Ops One",
        )
        visited = set()
        with self.camera.activate():
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
                        5,
                    )
                    visited.add(key)
            for hub in self.main_map.graph:
                arcade.draw_circle_filled(
                    hub.x,
                    hub.y,
                    self.hub_radius + 4,
                    arcade.csscolor.DARK_GRAY,
                    num_segments=100,
                )
                arcade.draw_circle_filled(
                    hub.x,
                    hub.y,
                    self.hub_radius,
                    hub.color,
                    num_segments=100
                )
                angle = math.radians(50)

                dot_x = hub.x + (self.hub_radius + 4) * math.cos(angle)
                dot_y = hub.y + (self.hub_radius + 4) * math.sin(angle)
                arcade.draw_circle_filled(
                    dot_x,
                    dot_y,
                    13,
                    arcade.csscolor.DARK_GRAY,
                    num_segments=100
                )
                arcade.draw_circle_filled(
                    dot_x,
                    dot_y,
                    10,
                    arcade.csscolor.ROYAL_BLUE,
                    num_segments=100
                )
                arcade.draw_text(
                    f"{hub.type[0].upper()}",
                    dot_x - 1,
                    dot_y + 1,
                    arcade.csscolor.DARK_RED,
                    9,
                    font_name="JetBrains Mono",
                    anchor_x="center",
                    anchor_y="center",
                )
            for drone in self.main_map.drones:
                arcade.draw_circle_filled(
                    drone.x, drone.y, 10, drone.color, num_segments=100
                )

    def on_mouse_drag(
        self, x: int, y: int, dx: int, dy: int, buttons: int, modifiers: int
    ) -> None:
        self.cx -= dx
        self.cy -= dy
        self.camera.position = (self.cx, self.cy)

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        if symbol == arcade.key.R and (modifiers & arcade.key.MOD_CTRL):
            self.main_map.reset()
            self.is_sim_end = False
            self.turns = 0
            self.debug = True

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
    if len(sys.argv) != 2:
        console = Console()
        console.print("[red]Error:[/red] Expected exactly one argument.")
        console.print("Usage:   [bold]python fly-in.py <path/to/map>[/bold]")

        sys.exit(1)
    parser = Parser(sys.argv[1])
    main_map = Map(**parser.main_parser())
    window = arcade.Window(width=1920, height=1010)
    game = SimulationWindow(main_map)
    game.setup()
    window.show_view(game)
    arcade.run()


if __name__ == "__main__":

    try:
        main()
    except ParserError as e:
        Errors.display_error(e, sys.argv[1])
    except Grapherror as e:
        Errors.display_error(e, sys.argv[1])
    except Exception as e:
        Errors.display_error(e)
    except KeyboardInterrupt:
        print("""
 ▄████  ▄████▄ ▄████▄ ████▄  █████▄ ██  ██ ██████
██  ▄▄▄ ██  ██ ██  ██ ██  ██ ██▄▄██  ▀██▀  ██▄▄
 ▀███▀  ▀████▀ ▀████▀ ████▀  ██▄▄█▀   ██   ██▄▄▄▄
""")
