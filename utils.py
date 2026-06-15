from typing import Optional, Dict, List
from colors import colors
import random
import heapq


class Hub:

    def __init__(
            self,
            name: str,
            x: int,
            y: int,
            color: Optional[str] = None,
            max_drones: int = 1,
            zone: str="normal"
        ) -> None:
        self.x = x
        self.y = y
        self.pos = (x, y)
        self.name = name
        self.type = zone
        self.color = colors["blue"] if not colors.get(color) else colors[color]
        self.max_drones = max_drones
        self.current_drones_count = 0
        self.cost = float("inf")
        self.is_goal_hub = False
    def __lt__(self, other):
        return self.cost < other.cost
    


class Map:
    def __init__(self,graph: Dict[Hub,List[Hub]], start: Hub, end: Hub, nb_drones: int):
        self.graph = graph
        self.start = start
        self.end = end
        self.end.cost = 0
        self.nb_drones = nb_drones
        self.drones: List[Drone] = [Drone() for _ in range(self.nb_drones)]
        self.zone_costs = {"normal":2,"priority":1, "restricted": 3}   

    def set_drones(self):
        for drone in self.drones:
            drone.graph = self.graph
            drone.current = self.start
            drone.x = drone.current.x 
            drone.y = drone.current.y

    def reset(self):
        for drone in self.drones:
            drone.current = self.start
            drone.x = drone.current.x
            drone.y = drone.current.y
            drone.next = None
            drone.can_move = False
            drone.reserve_spot = False
        for key in self.graph:
            key.current_drones_count = 0             
    def scale_and_center_hubs(self, zoom, cx, cy, move_x , move_y):
        queue = [self.start]
        visited = set()
        while queue:
            current = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)
            x,y = current.pos
            current.x  = x * zoom + cx
            current.y =  y * zoom + cy
            for hub in self.graph[current]:
                if hub not in visited:
                    queue += [hub] 
        # i dont do the same logic with drone's because the move
        for drone in self.drones:
            drone.x += move_x
            drone.y += move_y


    def find_path(self):
        heap = [self.end]
        history = {}


        while heap:
            currnt = heapq.heappop(heap)
            for neighber in self.graph[currnt]:
                if neighber.type == "blocked":
                    continue
                if neighber.cost > currnt.cost + self.zone_costs[neighber.type]:
                    neighber.cost = currnt.cost + self.zone_costs[neighber.type]
                    history[neighber] = currnt
                    heap += [neighber]





class Drone:
    counter = 1
    def __init__(self):

        self.name = f"D{self.counter}"
        Drone.counter += 1
        self.current: Optional[Hub] = None
        self.next: Optional[Hub] = None
        self.x = 0
        self.y = 0
        self.can_move = False
        self.reserve_spot = False
        self.color = colors[random.choice(list(colors.keys()))]
        self.graph: Dict[Hub, List[Hub]] = {}
    def find_next(self):
        hub_list = self.graph[self.current][:]
        min_cost = min(hub_list)
        if min_cost.current_drones_count < min_cost.max_drones:
            return min_cost
        else:

            old_min = min_cost
            hub_list.remove(min_cost)
            if not hub_list:
                return None
            min_cost = min(hub_list)
            if min_cost.cost == old_min.cost:
                return min_cost
            elif min_cost == old_min.cost + 1:
                return min_cost
        return None 

        
    def update(self):
        if self.current.is_goal_hub or not self.can_move:
            return
        nx = ((self.next.x - self.current.x) * 50 ) / 100
        ny = ((self.next.y - self.current.y) * 50 )/ 100
        self.x += nx
        self.y += ny

        if (self.x , self.y) == (self.next.x , self.next.y ):
            self.current = self.next
            self.current.current_drones_count -= 1
            self.next = self.find_next()
            self.can_move = False
            self.reserve_spot = False

