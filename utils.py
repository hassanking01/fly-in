from typing import Optional, Dict, List
from colors import colors
import random
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
        self.name = name
        self.type = zone
        self.color = colors["blue"] if not colors.get(color) else colors[color]
        if not colors.get(color):
            print(color)
        self.max_drones = max_drones
        self.current_drones_count = 0
class Map:
    def __init__(self,graph: Dict[Hub,List[Hub]], start: Hub, end: Hub, nb_drones: int):
        self.graph = graph
        self.start = start
        self.end = end
        self.nb_drones = nb_drones
        self.path = []
        self.drones: List[Drone] = [Drone() for _ in range(self.nb_drones)]
    def find_path(self):
        from collections import deque
        import heapq
        stack = [self.start]
        stack = deque(stack)
        history = {}
        visited = set()

        while stack:
            currnt = stack.popleft()
            if currnt in visited:
                continue
            visited.add(currnt)
            for neighber in self.graph[currnt]:
                if neighber not in visited:
                    history[neighber] = currnt
                    stack += [neighber]
            if self.end in self.graph[currnt]:
                break
        currnt = self.end
        while currnt != self.start:
            self.path += [currnt]
            currnt = history[currnt]

        self.path += [currnt]
        self.path = self.path[::-1]
        for drone in self.drones:
            drone.path = self.path
            drone.pos = (drone.path[0].x, drone.path[0].y)

class Drone:
    counter = 1
    def __init__(self):
        self.name = f"D{self.counter}"
        Drone.counter += 1
        self.path: List[Hub] = []
        self.current = 0
        self.next = 1
        self.pos = (0,0)
        self.done_turn = False
        self.color = colors[random.choice(list(colors.keys()))]
        

