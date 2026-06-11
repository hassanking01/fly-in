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
        if not colors.get(color):
            print(color)
        self.max_drones = max_drones
        self.current_drones_count = 0
        self.cost = float("inf")    
    def __lt__(self, other):
        return self.cost < other.cost
    


class Map:
    def __init__(self,graph: Dict[Hub,List[Hub]], start: Hub, end: Hub, nb_drones: int):
        self.graph = graph
        self.start = start
        self.start.cost = 0
        self.end = end
        self.nb_drones = nb_drones
        self.path = []
        self.drones: List[Drone] = [Drone() for _ in range(self.nb_drones)]
        self.zone_costs = {"normal":2,"priority":1, "restricted": 3}   
    def set_drones(self, zoom , cx, cy):
        for drone in self.drones:
            drone.current = self.start
            drone.x = drone.current.x * zoom + cx
            drone.y = drone.current.y * zoom + cy
             
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
        flag = False
        for drone in self.drones:
            if not flag:
                print(f"drone.x = {drone.x} drone.y = {drone.y} cx = {cx} cy {cy}")
                flag = True
            drone.x += move_x
            drone.y += move_y


    def find_path(self):
        heap = [self.start]
        history = {}
        visited = set()
    
        while heap:
            currnt = heapq.heappop(heap)
            for neighber in self.graph[currnt]:
                if neighber.type == "blocked":
                    continue
                if neighber.cost > currnt.cost + self.zone_costs[neighber.type]:
                    neighber.cost = currnt.cost + self.zone_costs[neighber.type]
                    history[neighber] = currnt
                    heap += [neighber]
            if self.end in self.graph[currnt]:
                break
        currnt = self.end
        while currnt != self.start:
            self.path += [currnt]
            currnt = history[currnt]

        self.path += [currnt]
        self.path = self.path[::-1]
        print([zone.name for zone in self.path])
        for drone in self.drones:
            drone.path = self.path
            drone.current = self.path[0]
            drone.next = self.path[1]
            drone.x = drone.current.x
            drone.y = drone.current.y
            drone.pos = (drone.x, drone.y)





class Drone:
    counter = 1
    def __init__(self):

        self.name = f"D{self.counter}"
        Drone.counter += 1
        self.path: List[Hub] = []
        self.current: Optional[Hub] = None
        self.next: Optional[Hub] = None
        self.next_index = 1
        self.pos = (0,0)
        self.x = 0
        self.y = 0
        self.pos= (0,0)
        self.done_turn = False
        self.color = colors[random.choice(list(colors.keys()))]
        
    def update(self, zoom, cx, cy):
        if self.next_index >= len(self.path):
            return
        nx = ((self.next.x - self.current.x) * 5 ) / 100
        ny = ((self.next.y - self.current.y) * 5 )/ 100
        self.x += nx
        self.y += ny

        if (self.x , self.y) == (self.next.x , self.next.y ):
            self.current = self.next
            self.pos = self.next.pos
            self.next_index += 1
            if self.next_index < len(self.path):
                self.next = self.path[self.next_index]

