*This project has been created as part of the 42 curriculum by hahchtar.*

# Fly-in

> Drones are interesting.

## Description

**Fly-in** is a Python simulation engine that routes a fleet of autonomous drones from a
**start** zone to an **end** zone through a network of connected zones, while respecting
strict movement, capacity, and timing constraints.

The project takes a custom map file (zones + connections, with optional metadata such as
zone type, color, and capacity) and computes a turn-by-turn schedule that moves every
drone from the start hub to the end hub in the fewest possible simulation turns, while:

- Avoiding zone and connection capacity violations.
- Avoiding collisions and deadlocks between drones.
- Correctly handling zone movement costs (`normal`, `priority`, `restricted`, `blocked`).
- Respecting multi-turn transit rules for `restricted` zones.

The goal of the project is to practice graph modeling, pathfinding/scheduling algorithm
design, and object-oriented Python.
## Features

- Custom parser for the `.txt` map format (zones, connections, metadata, comments).
- Strict validation of the input file with clear, line-level error messages.
- Object-oriented graph model (`Zone`, `Connection`, `Drone`, `Graph`, `Simulation`, ...).
- A multi-drone, capacity-aware pathfinding/scheduling algorithm that:
  - Distributes drones across multiple paths.
  - Makes drones wait strategically when a move is not currently possible.
  - Prevents path conflicts and deadlocks.
- Turn-by-turn simulation engine that outputs movements in the format required by the
  subject (`D<ID>-<zone>` / `D<ID>-<connection>`).
- Visual feedback of the simulation (colored terminal output and/or graphical interface).
- Fully type-safe codebase (`mypy`) and `flake8`-compliant.

## Instructions

### Requirements

- Python 3.10 or later
- `pip` (or `uv` / `pipx`)

### Installation

```bash
make install
```

### Running the simulation

```bash
make run FILE="path/to/map.txt"
```

> Replace `path/to/map.txt` with the path to the map file you want to simulate.

### Linting & type checking

```bash
make lint
```

Runs `flake8 .` and `mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs`.

An optional stricter check is also available:

```bash
make lint-strict
```

Runs `flake8 .` and `mypy . --strict`.

### Cleaning

```bash
make clean
```

Removes temporary files and caches (`__pycache__`, `.mypy_cache`, etc.).

## Map file format

A map is described in a plain text file. Example:

```
nb_drones: 5

start_hub: hub 0 0 [color=green]
end_hub: goal 10 10 [color=yellow]
hub: roof1 3 4 [zone=restricted color=red]
hub: roof2 6 2 [zone=normal color=blue]
hub: corridorA 4 3 [zone=priority color=green max_drones=2]
hub: tunnelB 7 4 [zone=normal color=red]
hub: obstacleX 5 5 [zone=blocked color=gray]

connection: hub-roof1
connection: hub-corridorA
connection: roof1-roof2
connection: roof2-goal
connection: corridorA-tunnelB [max_link_capacity=2]
connection: tunnelB-goal
```

- `zone` types: `normal` (1 turn, default), `priority` (1 turn, preferred), `restricted`
  (2 turns), `blocked` (inaccessible).
- `max_drones` caps how many drones can occupy a zone at once (default `1`).
- `max_link_capacity` caps how many drones can traverse a connection at once (default `1`).
- Lines starting with `#` are treated as comments.

## Algorithm choices & implementation strategy

## Algorithm choices & implementation strategy
 
### Pathfinding — Reverse Dijkstra (cost-to-goal map)
 
Instead of computing a path per drone, the algorithm runs a single **reverse Dijkstra**
pass starting from the **end zone**. This produces a *cost-to-goal* value for every zone
in the graph: the minimum cumulative cost to reach the end zone from that zone.
 
- Every zone is initialized with a cost of `+inf`, except the end zone, which starts at `0`.
- The algorithm relaxes neighbors exactly like a standard Dijkstra, but propagates outward
  from the end zone instead of the start zone — each zone's cost is updated whenever a
  smaller cost is found through one of its neighbors.
- `blocked` zones are skipped entirely and never relaxed, so they are never part of any
  path.
- Edge weights are not the raw subject movement costs, but custom weights chosen to bias
  the search toward the most desirable zones:
  - `priority` → `1`
  - `normal` → `2`
  - `restricted` → `3`
  This keeps the relative ordering the subject asks for (priority is cheapest and
  therefore preferred, restricted is the most expensive and therefore avoided unless
  necessary) while giving Dijkstra a clean integer weight to relax on.
Because this is computed once per map (not once per drone), every drone shares the same
cost-to-goal table and simply "descends the gradient" toward the end zone turn by turn —
there is no need to compute or store a separate path object per drone.
 
### Scheduling — greedy reservation per turn
 
At each simulation turn, drones are resolved using the cost-to-goal table:
 
1. For each drone currently waiting at a zone, look at all of its neighboring zones.
2. Pick the neighbor with the **lowest cost-to-goal** value — this is the zone that gets
   the drone closest to the end zone.
3. Try to **reserve a spot** in that zone for the current turn:
   - If the zone (and the connection leading to it) still has free capacity, the
     reservation succeeds and the drone is scheduled to move there.
   - If the lowest-cost zone is already full for this turn, fall back to the
     **next best option** (cost + 1) and try to reserve there instead.
4. If no neighboring zone can be reserved at all (every candidate is at capacity), the
   drone is flagged to wait: its `next` zone is set to `None` for this turn, and it tries
   again on the following turn.
Reservations are tracked per turn before any drone actually moves, which is what prevents
two drones from being scheduled into the same zone/connection beyond its capacity, and
avoids collisions between drones converging on the same zone.
 
restricted zones are handled as a special case of this reservation step: if a drone's next zone is restricted, it doesn't jump there directly. On the first turn it moves to the midpoint of the connection (logged as occupying the connection itself), and on the following turn it completes the move into the restricted zone. The drone cannot stop or wait at the midpoint — once it commits to the connection, it must arrive at the destination on the next turn, matching the subject's multi-turn movement rule.
 

## Visual representation

The visual feedback is built with **Arcade**, a Python graphical library. A dedicated
`View` renders the zone graph as a set of connected nodes positioned according to their
coordinates, with each zone colored according to its type and state, and connections
drawn as edges between them. At every simulation turn, the drones are redrawn moving
across the graph, animating their transition from one zone to the next so their progress
toward the end zone is visible in real time. A status bar fixed at the top of the window
displays the current simulation state at a glance: whether the simulation is currently
running or paused, the current turn number, and the delivery progress as
`delivered / nb_drones`. Together, this gives an immediate, at-a-glance understanding of
the network topology, drone movement, and overall simulation progress without needing to
read the raw turn-by-turn text output.
 

## Resources

- [Dijkstra's Algorithm — Wikipedia](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm)
- [Dijkstra's Shortest Path Algorithm — GeeksforGeeks](https://www.geeksforgeeks.org/dsa/dijkstras-shortest-path-algorithm-greedy-algo-7/)
- [Dijkstra's Algorithm - youtube 1](https://www.youtube.com/watch?v=bZkzH5x0SKU)
- [Dijkstra's Algorithm - youtube 2](https://www.youtube.com/watch?v=EFg3u_E6eHU&t)
- [Dijkstra's Algorithm - youtube 3](https://www.youtube.com/watch?v=N_N9Ky6tN_s&t=1019s)
- [Dijkstra's Shortest Path Algorithm — w3schools](https://www.w3schools.com/dsa/dsa_algo_graphs_dijkstra.php)

### AI usage

AI assistance was used during this project for:
- making this read me
- how to use arcade
