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
    """
    Arcade view that renders and drives the drone-delivery simulation: camera
    control, per-frame drone movement, turn logging, and drawing of hubs,
    connections, drones, and the HUD.
    """
    def __init__(self, main_map: Map) -> None:
        """
        Set up the simulation view: create the camera, center and scale the
        map, initialize turn/delivery counters, pause state, and load the
        display font.
        """
        self.camera = arcade.camera.Camera2D()
        self.main_map = main_map
        super().__init__()
        self.on_next_turn = False
        self.console = Console()
        self.delivered: set[Drone] = set()
        self.cx = int(
            self.width // 2 - ((self.main_map.end.x * 100) // 2)
        )
        self.cy = int(self.height // 2)
        self.camera.position = (self.cx, self.cy)
        self.hub_radius = 30
        self.puase = True
        self.main_map.scale_and_center_hubs(100, self.cx, self.cy)
        self.zoom = 1.0
        self.turns = 0
        self.is_sim_end = False
        arcade.load_font("Monoton-Regular.ttf")
        self.progress_z: float = 0
        self.progress_d: float = 0

    def on_mouse_scroll(
            self,
            x: int,
            y: int,
            scroll_x: int,
            scroll_y: int
            ) -> None:
        """
        Zoom the camera in or out based on scroll input,
        clamped between 0.6x and 5.0x.
        """
        self.zoom += scroll_y * 0.1
        self.zoom = max(0.6, min(5.0, self.zoom))
        self.camera.zoom = self.zoom

    def setup(self) -> None:
        """
        Place all drones on the map at the start hub,
        ready for simulation to begin.
        """
        self.main_map.set_drones()

    def print_turns(self, moved_drones: list[Drone]) -> None:
        """
        Print a rich Panel to the console summarizing which drones moved to
        which hub during the current turn.
        """
        line = "[cyan]"
        for drone in moved_drones:
            if not drone.next or not drone.current:
                continue
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
        """
        Per-frame simulation tick: advance each drone's movement animation;
        once all drones finish their current move, increment the turn counter,
        log the turn, mark drones that reached the goal as delivered, assign
        each idle drone its next hub,
        and check whether the simulation has ended.
        """
        self.progress_z += (delta_time * 2)
        self.progress_d += (delta_time * 4)
        self.progress_z %= 360
        self.progress_d %= 360
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
                    if drone.current and drone.current.is_goal_hub:
                        if drone not in self.delivered:
                            self.delivered.add(drone)
                    if drone.next:
                        drone.finished = False
                        continue
                    next = drone.find_next(self.turns)
                    if next:
                        next.current_drones_count += 1
                        if not drone.current:
                            continue
                        next.connections[drone.current]["on_road"] += 1
                        if drone.current:
                            drone.current.current_drones_count -= 1
                        drone.can_move = True
                        drone.finished = False
                    drone.next = next
                if self.on_next_turn:
                    self.puase = True
                self.is_sim_end = all(
                    drone.current.is_goal_hub
                    for drone in self.main_map.drones if drone.current
                )
                if self.is_sim_end:
                    self.puase = True

    def on_draw(self) -> None:
        """
        Render one frame: background grid, HUD (turn count, delivered count,
        play/pause status), the hub graph (connections and hubs with zone-type
        labels), and each drone at its current animated position.
        """
        self.clear()
        visited = set()
        cx = self.width
        cy = self.height
        color = (240, 198, 162, 80)
        for i in range(0, int(cy) * 2, 60):
            arcade.draw_line(0, i, cx, i, color)
            arcade.draw_line(i, 0, i,  cy, color)

        rect = arcade.rect.XYWH(self.width // 2, self.height - 80, 1900, 100)
        arcade.draw_rect_filled(rect, (106, 90, 205, 200))
        rect = arcade.rect.XYWH(self.width // 2, self.height - 80, 1890, 90)
        arcade.draw_rect_filled(rect, (159, 182, 205, 100))
        arcade.draw_text(
            f"TURNS:   {self.turns}",
            self.width // 2,
            self.height - 78,
            arcade.csscolor.LIGHT_GOLDENROD_YELLOW,
            font_size=35,
            font_name="Monoton",
            anchor_x="center",
            anchor_y="center"
        )
        arcade.draw_text(
            f"DELIVERED:   {len(self.delivered)} / {self.main_map.nb_drones}",
            self.width - 300,
            self.height - 78,
            arcade.csscolor.LIGHT_GOLDENROD_YELLOW,
            font_size=20,
            font_name="Monoton",
            anchor_x="center",
            anchor_y="center"
        )
        arcade.draw_text(
            f"STATUS:   {'PAUSE' if self.puase else 'PLAYING'}",
            300,
            self.height - 78,
            arcade.csscolor.LIGHT_GOLDENROD_YELLOW,
            font_size=20,
            font_name="Monoton",
            anchor_x="center",
            anchor_y="center"
        )
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
            new_r = math.sin(self.progress_z)
            angle = math.radians(50)
            for hub in self.main_map.graph:
                r, g, b = hub.color
                arcade.draw_circle_filled(
                    hub.x,
                    hub.y,
                    (self.hub_radius + 5) + (new_r * 5),
                    (r, g, b, 100),
                    num_segments=100,
                )
                arcade.draw_circle_filled(
                    hub.x, hub.y, self.hub_radius, hub.color, num_segments=100
                )

                dot_x = hub.x + (self.hub_radius + 4) * math.cos(angle)
                dot_y = hub.y + (self.hub_radius + 4) * math.sin(angle)
                r, g, b, _ = arcade.csscolor.ROYAL_BLUE
                arcade.draw_circle_filled(
                    dot_x,
                    dot_y,
                    13,
                    (r, g, b, 100),
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
            new_r = math.sin(self.progress_d)

            for drone in self.main_map.drones:
                angles = [math.radians(angle) for angle in [45, 135, 315, 225]]
                r, g, b = drone.color
                arcade.draw_circle_filled(
                    drone.x,
                    drone.y,
                    15 + (new_r * 5),
                    (r, g, b, 155),
                    num_segments=100
                )
                arcade.draw_circle_outline(
                        drone.x,
                        drone.y,
                        17,
                        (0, 0, 0, 255),
                        border_width=2,
                        num_segments=100
                    )
                for angle_ in angles:
                    dot_x = drone.x + (14) * math.cos(angle_)
                    dot_y = drone.y + (14) * math.sin(angle_)
                    arcade.draw_circle_filled(
                        dot_x,
                        dot_y,
                        8,
                        (r, g, b, 255),
                        num_segments=100
                    )
                    arcade.draw_circle_outline(
                        dot_x,
                        dot_y,
                        10,
                        (0, 0, 0, 255),
                        border_width=2,
                        num_segments=100
                    )
                arcade.draw_circle_filled(
                    drone.x,
                    drone.y,
                    15,
                    (r, g, b, 255),
                    num_segments=100
                )

    def on_mouse_drag(
        self, x: int, y: int, dx: int, dy: int, buttons: int, modifiers: int
    ) -> None:
        """
        Pan the camera by the mouse drag delta.
        """
        self.cx -= dx
        self.cy -= dy
        self.camera.position = (self.cx, self.cy)

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        """
        Handle keyboard shortcuts: Ctrl+R resets the simulation, Right Arrow
        steps forward one turn, and Space toggles play/pause.
        """
        if symbol == arcade.key.R and (modifiers & arcade.key.MOD_CTRL):
            self.main_map.reset()
            self.is_sim_end = False
            self.turns = 0
            self.debug = True
            self.delivered = set()

        if symbol == arcade.key.RIGHT and not self.is_sim_end:
            if not self.on_next_turn:
                self.on_next_turn = True
            if self.puase:
                self.puase = False
        if symbol == arcade.key.SPACE and not self.is_sim_end:
            if self.on_next_turn:
                self.on_next_turn = False
            if self.puase:
                self.puase = False
            else:
                self.puase = True


def main() -> None:
    """
    Program entry point: validate CLI arguments, parse the map file into a Map,
    create the arcade window and SimulationWindow,
    and run the arcade event loop.
    """
    warnings.filterwarnings("ignore")
    if len(sys.argv) != 2:
        console = Console()
        console.print("[red]Error:[/red] Expected exactly one argument.")
        console.print("Usage:   [bold]python fly-in.py <path/to/map>[/bold]")

        sys.exit(1)
    parser = Parser(sys.argv[1])
    main_map = Map(**parser.main_parser())
    window = arcade.Window(width=1920, height=900, fullscreen=True)
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
