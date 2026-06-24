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
        self.connections: Dict[Hub, int] = {}
        self.pos = (x, y)
        self.name = name
        self.type = zone
        self.color = colors["blue"] if not colors.get(color) else colors[color]
        self.max_drones = max_drones
        self.current_drones_count = 0
        self.cost = float("inf")
        self.is_goal_hub = False
        self.on_road = 0
        self.drone_in = []
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
            self.start.drone_in += [drone]
            next = drone.find_next()
            if next:
                next.current_drones_count += 1
                drone.can_move = True
                drone.reserve_spot = True
                drone.finished = False
            drone.next = next 
    def reset(self):
        for drone in self.drones:
            drone.current = self.start
            drone.x = drone.current.x
            drone.y = drone.current.y
            drone.next = None
            drone.can_move = False
        for key in self.graph:
            key.current_drones_count = 0
        self.start.current_drones_count = self.nb_drones
                     
    def scale_and_center_hubs(self, zoom, cx, cy, move_x , move_y):
        for hub in self.graph:
            x,y = hub.pos
            hub.x  = x * zoom + cx
            hub.y =  y * zoom + cy
        # i dont do the same logic with drone's because the move
        for drone in self.drones:
            drone.x += move_x
            drone.y += move_y


    def find_path(self):
        heap = [self.end]
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
    def __init__(self):

        self.name = f"D{self.counter}"
        Drone.counter += 1
        self.current: Optional[Hub] = None
        self.next: Optional[Hub] = None
        self.next_x = 0
        self.next_y = 0
        self.x = 0
        self.y = 0
        self.finished = True
        self.first_half = False
        self.can_move = False
        self.color = colors[random.choice(list(colors.keys()))]
        self.graph: Dict[Hub, List[Hub]] = {}
        self.end_hub = None

    def find_next(self) -> Optional[Hub]:
        if self.current.is_goal_hub:
            return None
        
        hub_list = self.graph[self.current][:]
        same_cost: List[Hub] = []
        min_cost = min(hub_list).cost
    
        hub_list = sorted(hub_list)
        for hub in hub_list:
            if hub.cost == min_cost:
                same_cost  += [hub]
        random.shuffle(same_cost)
        for hub in same_cost:
            if hub.cost <= min_cost + 1 and  hub.current_drones_count < hub.max_drones and hub.on_road < self.current.connections[hub] :
                return hub
            hub_list.remove(hub)
        for hub in hub_list:
            if hub.cost <= min_cost + 1 and  hub.current_drones_count < hub.max_drones and hub.on_road < self.current.connections[hub]:
                return hub
            if hub.cost > min_cost + 1:
                break
        return None 

    def update(self):
        if not self.next or self.current.is_goal_hub or not self.can_move:
            return 
        if self.next.type == "restricted":
            if not self.first_half:
                self.next_x = (self.next.x + self.current.x ) // 2
                self.next_y = (self.next.y + self.current.y ) // 2
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
        if (self.x , self.y) == (self.next_x , self.next_y ):
            if self.next.type == "restricted":
                if not self.first_half:
                    self.first_half = True
                else:
                    self.first_half = False
                    self.next.on_road -= 1
                    self.current = self.next
                    self.can_move = False
                    self.next = None
            else:
                self.next.on_road -= 1
                self.current = self.next
                self.can_move = False
                self.next = None   
            self.finished = True         
