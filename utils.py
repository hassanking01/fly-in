from typing import Optional, Dict, List
from colors import colors
import random
import heapq
from error_classes import Grapherror
import sys


class Hub:
    """
    Represents a single hub (node) in the delivery graph:
    its position, display color, drone capacity, current occupancy,
    zone type, and cached pathfinding cost to the end hub.
    """

    def __init__(
        self,
        name: str,
        x: int,
        y: int,
        color: str,
        max_drones: int = 1,
        zone: str = "normal",
    ) -> None:
        """
        Create a hub.

        Args:
        name: Unique identifier for the hub.
        x: X coordinate on the map.
        y: Y coordinate on the map.
        color: Color name used to look up the hub's RGB display color.
        max_drones: Maximum number of drones allowed at the hub simultaneously.
        zone: Zone type
        ('normal', 'priority', 'restricted', 'blocked') affecting traversal cost.
        """

        self.x = x
        self.y = y
        self.connections: Dict[Hub, dict[str, int]] = {}
        self.name = name
        self.type = zone
        self.color: tuple[int, int, int] = colors.get(color, (0, 0, 255))
        self.max_drones = max_drones
        self.current_drones_count = 0
        self.cost = float("inf")
        self.is_goal_hub = False
        self.in_zone = []

    def __lt__(self, other: "Hub") -> bool:
        """
        Compare two hubs by their pathfinding `cost` so Hub instances can be
        ordered/heapified (used by heapq and sorted()).
        """
        return self.cost < other.cost

    # def __str__(self) -> str:
    #     # for index, key in enumerate(self.connections):
    #     #     line = f"{self.name}-{key.name}: {key.connections[self]['on_road']}/{key.connections[self]['max_link_capacity']}"
    #     #     if index <= len(self.connections) - 2:
    #     #         line += " | "
    #     #     connections_ += line
    #     # return f"{self.name}: {self.current_drones_count}/{self.max_drones} <{connections_}>"
    #     return  ""


class Map:
    """
    Holds the full simulation state: the graph of hubs, the start/end hubs,
    the drones, per-zone traversal costs,
    and the logic to validate the graph and compute shortest-path costs to the
    end hub.
    """
    def __init__(
        self, graph: Dict[Hub, List[Hub]], start: Hub, end: Hub, nb_drones: int
    ) -> None:
        """
        Initialize the map: store the graph and endpoints, seed the start hub
        with all drones, create the drone objects, validate that the graph is
        connected and a path exists to the end, and compute each hub's cost.
        """
        self.graph = graph
        self.start = start
        self.start.current_drones_count = nb_drones
        self.end = end
        self.end.cost = 0
        self.nb_drones = nb_drones
        self.drones: List[Drone] = [Drone() for _ in range(self.nb_drones)]
        self.zone_costs = {"priority": 1, "normal": 2, "restricted": 3}
        self.is_end_have_path()
        self.check_disconnected_graph()
        self.compute_costs()

    def set_drones(self) -> None:
        """
        Place every drone at the start hub and compute each drone's
        first move (`next` hub),
        updating hub occupancy and link usage accordingly.
        """
        for drone in self.drones:
            drone.graph = self.graph
            drone.current = self.start
            drone.x = drone.current.x
            drone.y = drone.current.y
            next = drone.find_next(0)
            drone.can_move = False
            drone.finished = True
            if next:
                drone.current.current_drones_count -= 1
                next.connections[drone.current]["on_road"] += 1
                next.current_drones_count += 1
                drone.can_move = True
                drone.finished = False
            drone.next = next

    def reset(self) -> None:
        """
        Reset all hubs and connections to their empty starting state and
        re-place all drones at the start hub,
        restarting the simulation from scratch.
        """
        for hub in self.graph:
            hub.current_drones_count = 0
            for connection in hub.connections:
                hub.connections[connection]["on_road"] = 0
        self.start.current_drones_count = self.nb_drones
        self.set_drones()

    def is_end_have_path(self) -> None:
        """
        Verify the end hub is reachable from the start hub via BFS
        (ignoring blocked hubs);
        raises Grapherror if not.
        """
        queue: list[Hub] = [self.start]
        visited: set[Hub] = set()
        while queue:
            current = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)
            for neighbor in self.graph[current]:
                if neighbor.type == "blocked":
                    continue
                queue += [neighbor]
        if self.end not in visited:
            raise Grapherror(
                0,
                f"No valid path exists from '{self.start}' to '{self.end}'.",
            )

    def check_disconnected_graph(self) -> None:
        """
        Verify every hub is reachable via BFS from the start/end hubs; if a
        hub is disconnected, locate its defining line in the map file and
        raise Grapherror with that line number.
        """
        queue: list[Hub] = [self.start]
        visited: set[Hub] = set([self.end])
        while queue:
            currnt = queue.pop(0)
            if currnt in visited:
                continue
            visited.add(currnt)
            for neighbor in self.graph[currnt]:
                if neighbor in visited:
                    continue
                queue += [neighbor]
        for hub in self.graph:
            if hub not in visited:
                with open(sys.argv[1], "r") as file:
                    for index, line in enumerate(file, start=1):
                        if hub.name not in line:
                            continue
                        raise Grapherror(
                            index,
                            f"hub '{hub.name}' at ({hub.x}, {hub.y})"
                            " is unreachable — "
                            f"every hub must be connected to the graph",
                        )

    def scale_and_center_hubs(
        self,
        zoom: int,
        cx: int,
        cy: int,
    ) -> None:

        for hub in self.graph:
            hub.x = hub.x * zoom + cx
            hub.y = hub.y * zoom + cy

    def compute_costs(self) -> None:
        heap: list[Hub] = [self.end]
        while heap:
            currnt = heapq.heappop(heap)
            for neighber in self.graph[currnt]:
                if neighber.type == "blocked":
                    continue
                new_cost = currnt.cost + self.zone_costs[neighber.type]
                if neighber.cost > new_cost:
                    neighber.cost = new_cost
                    heap += [neighber]


class Drone:
    counter = 1

    def __init__(self) -> None:
        self.name = f"D{self.counter}"
        Drone.counter += 1
        self.current: Optional[Hub] = None
        self.next: Optional[Hub] = None
        self.next_x = 0
        self.next_y = 0
        self.x: float = 0.0
        self.y: float = 0.0
        self.finished = True
        self.first_half = False
        self.can_move = False
        self.color = colors[random.choice(list(colors.keys()))]
        self.graph: Dict[Hub, List[Hub]] = {}
        self.end_hub = None

    def find_next(self, turns: int) -> Optional[Hub]:
        if not self.current:
            return None
        if self.current.is_goal_hub:
            return None
        hub_list = self.graph[self.current][:]
        same_cost: List[Hub] = []
        min_cost = min(hub_list).cost
        hub_list = sorted(hub_list)
        for hub in hub_list:
            if hub.cost == min_cost:
                same_cost += [hub]
        if turns % 2:
            same_cost = same_cost[::-1]
        for hub in same_cost:
            if (
                hub.cost <= min_cost + 1
                and hub.current_drones_count < hub.max_drones
                and hub.connections[self.current]["on_road"]
                < self.current.connections[hub]["max_link_capacity"]
            ):
                return hub
            hub_list.remove(hub)
        for hub in hub_list:
            if (
                hub.cost <= min_cost + 1
                and hub.current_drones_count < hub.max_drones
                and hub.connections[self.current]["on_road"]
                < self.current.connections[hub]["max_link_capacity"]
            ):
                return hub
            if hub.cost > min_cost + 1:
                break
        return None

    def update(self) -> None:
        if (
            not self.next
            or not self.current
            or self.current.is_goal_hub
            or not self.can_move
        ):
            return
        if self.next.type == "restricted":
            if not self.first_half:
                self.next_x = (self.next.x + self.current.x) // 2
                self.next_y = (self.next.y + self.current.y) // 2
            else:
                self.next_x = self.next.x
                self.next_y = self.next.y
        else:
            self.next_x = self.next.x
            self.next_y = self.next.y

        nx = (self.next_x - self.current.x) * 0.05
        ny = (self.next_y - self.current.y) * 0.05
        self.x += nx
        self.y += ny
        if (self.x, self.y) == (self.next_x, self.next_y):
            if self.next.type == "restricted":
                if not self.first_half:
                    self.first_half = True
                else:
                    self.first_half = False
                    self.next.connections[self.current]["on_road"] -= 1
                    self.current = self.next
                    self.can_move = False
                    # self.next = None
            else:
                self.next.connections[self.current]["on_road"] -= 1
                self.current = self.next
                self.can_move = False
                # self.next = None
            self.finished = True
