from parser import Map, main_parser, Hub, Drone
import pygame
pygame.init()
text = pygame.font.SysFont("Arial", 20)


camera_x = 400
camera_y = 300

dragging = False
last_mouse_pos = (0, 0)
turns = 0
def draw_hub(main_map: Map, screen, camera_x, camera_y):
    global text
    for key in main_map.graph:
                # img = text.render(
                #     key.name,
                #     True,
                #     (255,255,255,)
                # )
                # screen.blit(img,(key.x * 50 + camera_x , (key.y * 100 + camera_y) - 40 ) )
                pygame.draw.circle(
                    screen,
                    key.color,
                    (key.x * 50 + camera_x , key.y * 100 + camera_y ),
                    20
                )
def draw_coonnections(main_map: Map, screen,  camera_x, camera_y):
    visited = set()
    lines = []
    stack = [main_map.start]
    while stack:
        current = stack.pop()
        if current in visited:
            continue
        visited.add(current)
        for neighber in main_map.graph[current]:
            lines += [((current.x * 50 + camera_x, current.y * 100 + camera_y), (neighber.x * 50 + camera_x, neighber.y * 100 + camera_y) )]
            stack += [neighber]
    for line in lines:
        start, end = line
        pygame.draw.line(screen, (255, 255, 255), start, end, width=5)

def draw_drones(map: Map, screen, clock):
    global camera_y, dragging, camera_x, last_mouse_pos, turns, text 
    count = 0
    drones_to_move: list[Drone] = []
    for drone in map.drones:
        if drone.path[drone.next].current_drones_count == drone.path[drone.next].max_drones:
            continue
        drone.path[drone.next].current_drones_count += 1
        count += 1
        drone.pos = pygame.Vector2(drone.path[drone.current].x * 50 ,drone.path[drone.current].y * 100 )
        drones_to_move += [drone]
    while count != 0:
        screen.fill((4, 4, 80))
        img = text.render(
            f"turns: {turns}",
            True,
            (255,255,255,)
        )
        screen.blit(img,(40, 0 ) )

        draw_coonnections(map, screen, camera_x, camera_y)
        draw_hub(map , screen, camera_x, camera_y)

        for drone in drones_to_move:
            t = pygame.Vector2(drone.path[drone.next].x* 50 ,drone.path[drone.next].y* 100 ) - drone.pos
          
            if t.length() > 1:
                drone.pos += t.normalize() * 1
            else:
                if not drone.done_turn:
                    count -= 1
                    drone.done_turn = True
            for event in pygame.event.get():

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1: 
                        dragging = True
                        last_mouse_pos = event.pos

                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        dragging = False

                elif event.type == pygame.MOUSEMOTION:
                    if dragging:
                        dx = event.pos[0] - last_mouse_pos[0]
                        dy = event.pos[1] - last_mouse_pos[1]

                        camera_x += dx
                        camera_y += dy
                        last_mouse_pos = event.pos
            r = pygame.Rect(drone.pos[0] - 20 / 2 + camera_x, drone.pos[1] - 20 / 2 + camera_y, 20, 20)
            
            pygame.draw.rect(screen, (0 , 255, 255),r)

        clock.tick(60)
        pygame.display.flip()
    turns += 1
    for drone in drones_to_move:
        drone.current = drone.next
        drone.path[drone.current].current_drones_count -= 1
        if drone.next + 1 < len(drone.path):
            drone.next += 1
        drone.done_turn = False





def main():
    global last_mouse_pos, camera_x, camera_y, dragging, text
    try:
        result = main_parser()
        main_map = Map(**result)
        screen = pygame.display.set_mode((1080, 780))
        running = True
        clock = pygame.time.Clock()
        points = [
            (0, 0),
            (1, 0),
            (2, 0),
            (3, 1),
            (4, 2),
        ]
        main_map.find_path()
        while running:
            screen.fill((4, 4, 80))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # left click
                        dragging = True
                        last_mouse_pos = event.pos

                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        dragging = False

                elif event.type == pygame.MOUSEMOTION:
                    if dragging:
                        dx = event.pos[0] - last_mouse_pos[0]
                        dy = event.pos[1] - last_mouse_pos[1]

                        camera_x += dx
                        camera_y += dy
                        last_mouse_pos = event.pos

            img = text.render(
            f"turns: {turns}",
            True,
            (255,255,255,)
            )
            screen.blit(img,(40, 0 ) )

            draw_drones(main_map, screen, clock)                
            clock.tick(60)
            pygame.display.flip()


    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()