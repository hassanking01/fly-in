from typing import Optional, Dict, List
from colors import colors
import random
import heapq
from error_classes import Grapherror

from pprint import pprint


class Hub:

    def __init__(
            self,
            name: str,
            x: int,
            y: int,
            color: str,
            max_drones: int = 1,
            zone: str = "normal"
            ) -> None:

        self.x = x
        self.y = y
        self.connections: Dict[Hub, dict[str,int]] = {}
        self.pos = (x, y)
        self.name = name
        self.type = zone
        self.color: tuple[int, int, int] = colors.get(
            color,
            (int(0), int(0), int(255))
        )
        self.max_drones = max_drones
        self.current_drones_count = 0
        self.cost = float("inf")
        self.is_goal_hub = False
        self.on_road = 0

    def __lt__(self, other) -> bool:
        return self.cost < other.cost

    def __repr__(self):
        return self.name

class Map:
    def __init__(
            self,
            graph: Dict[Hub, List[Hub]],
            start: Hub,
            end: Hub,
            nb_drones: int
            ) -> None:
        self.graph = graph
        self.start = start
        self.end = end
        self.end.cost = 0
        self.nb_drones = nb_drones
        self.drones: List[Drone] = [Drone() for _ in range(self.nb_drones)]
        self.zone_costs = {"priority": 1, "normal": 2, "restricted": 3}

    def set_drones(self) -> None:
        for drone in self.drones:
            drone.graph = self.graph
            drone.current = self.start
            drone.x = drone.current.x
            drone.y = drone.current.y
            next = drone.find_next()
            drone.can_move = False
            drone.finished = True
            if next:
                next.connections[drone.current]["on_road"] += 1
                next.current_drones_count += 1
                drone.can_move = True
                drone.finished = False
            drone.next = next

    def reset(self) -> None:
        for key in self.graph:
            key.current_drones_count = 0
            key.on_road = 0
        self.start.current_drones_count = self.nb_drones
        self.set_drones()

    def scale_and_center_hubs(
            self,
            zoom: int,
            cx: int,
            cy: int,
            move_x: int,
            move_y: int
            ) -> None:

        for hub in self.graph:
            x, y = hub.pos
            hub.x = x * zoom + cx
            hub.y = y * zoom + cy
        for drone in self.drones:
            drone.x += move_x
            drone.y += move_y

    def compute_costs(self) -> None:
        heap: list[Hub] = [self.end]
        visited: set[Hub] = set([self.end])
        while heap:
            currnt = heapq.heappop(heap)
            for neighber in self.graph[currnt]:
                visited.add(neighber)
                if neighber.type == "blocked":
                    continue
                new_cost = currnt.cost + self.zone_costs[neighber.type]
                if neighber.cost > new_cost:
                    neighber.cost = new_cost
                    heap += [neighber]
        for hub in self.graph:
            if hub not in visited:
                raise Grapherror(
                    f"hub '{hub.name}' at ({hub.x}, {hub.y}) is unreachable — "
                    f"every hub must be connected to the graph"
                )


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

    def find_next(self) -> Optional[Hub]:
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
        random.shuffle(same_cost)
        for hub in same_cost:
            print(hub,"-" * 30,)
            pprint(hub.connections)
            print( self.current,"-" * 30)
            pprint( self.current.connections)

            if (
                hub.cost <= min_cost + 1
                and hub.current_drones_count < hub.max_drones
                and hub.connections[self.current]["on_road"] < self.current.connections[hub]["max_link_capacity"]
                    ):
                return hub
            hub_list.remove(hub)
        for hub in hub_list:
            if (
                hub.cost <= min_cost + 1
                and hub.current_drones_count < hub.max_drones
                and hub.connections[self.current]["on_road"] < self.current.connections[hub]["max_link_capacity"]
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
