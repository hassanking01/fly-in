from parser import Map, main_parser, Hub, Drone, colors 
import pygame



class Graphics:
    def __init__(self, width=1080, height=720, main_map: Map= None):
        self.width = width
        self.height = height
        self.camera_x = width // 2
        self.camera_y = height // 2
        self.dragging = False
        self.last_mouse_pos = (0,0)
        self.turns = 0
        self.is_over = False
        self.main_map = main_map
        pygame.init()
        self.text = pygame.font.SysFont("Arial", 20)
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.main_map.find_path()
        self.running = True
        self.speed = 1
        self.old_speed = self.speed
        self.flag = False
    def draw_hub(self):
        for key in self.main_map.graph:
                    nb_drones_text = self.text.render(f"{key.current_drones_count}", True, (255,100,250))
                    self.screen.blit(nb_drones_text, (key.x * 50 + self.camera_x , key.y * 100 + self.camera_y + 20))
                    old = self.text.bold

                    self.text.bold = 10
                    type_ = self.text.render(f"{key.type}", True, (255,100,250))
                    self.text.bold = old
                    
                    self.screen.blit(type_, (key.x * 50 + self.camera_x , key.y * 100 + self.camera_y + 40))
                    pygame.draw.circle(
                        self.screen,
                        key.color,
                        (key.x * 50 + self.camera_x , key.y * 100 + self.camera_y ),
                        20
                    )
    def draw_coonnections(self):
        visited = set()
        lines = []
        stack = [self.main_map.start]
        while stack:
            current = stack.pop()
            if current in visited:
                continue
            visited.add(current)
            for neighber in self.main_map.graph[current]:
                lines += [((current.x * 50 + self.camera_x, current.y * 100 + self.camera_y), (neighber.x * 50 + self.camera_x, neighber.y * 100 + self.camera_y) )]
                stack += [neighber]
        for line in lines:
            start, end = line
            pygame.draw.line(self.screen, (255, 255, 255), start, end, width=5)
    def get_drone_coordinates(self,drone: Drone):
        return (drone.pos[0] - 20 / 2 + self.camera_x, drone.pos[1] - 20 / 2 + self.camera_y) 
    def draw_drones(self):
        count = 0
        drones_to_move: list[Drone] = []
        for drone in self.main_map.drones:
            if drone.path[drone.next].current_drones_count == drone.path[drone.next].max_drones and drone.path[drone.next] != self.main_map.end :
                continue
            if drone.path[drone.current] != self.main_map.end: 
                drone.path[drone.next].current_drones_count += 1
            count += 1
            drone.pos = pygame.Vector2(drone.path[drone.current].x * 50 ,drone.path[drone.current].y * 100 )
            drones_to_move += [drone]
        while count != 0:
            self.screen.fill((4, 4, 80))
            img = self.text.render(
                f"turns: {self.turns}",
                True,
                (255,255,255,)
            )
            self.screen.blit(img,(40, 0 ) )

            self.draw_coonnections()
            self.draw_hub()

            for drone in drones_to_move:
                target = pygame.Vector2(drone.path[drone.next].x* 50 ,drone.path[drone.next].y* 100 )
                t = target - drone.pos
                distance = t.length()
                if distance > 0:
                    if distance <= self.speed:
                        drone.pos = target
                    else:

                        drone.pos += (t.normalize() * self.speed)
                    
                else:
                    if not drone.done_turn:
                        count -= 1
                        drone.done_turn = True
                for event in pygame.event.get():
                    
                    if event.type == pygame.QUIT:
                        self.running = False
                        return
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1: 
                            self.dragging = True
                            self.last_mouse_pos = event.pos

                    elif event.type == pygame.MOUSEBUTTONUP:
                        if event.button == 1:
                            self.dragging = False

                    elif event.type == pygame.MOUSEMOTION:
                        if self.dragging:
                            dx = event.pos[0] - self.last_mouse_pos[0]
                            dy = event.pos[1] - self.last_mouse_pos[1]

                            self.camera_x += dx
                            self.camera_y += dy
                            self.last_mouse_pos = event.pos
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_UP:
                            if self.speed < 30:
                                self.speed += 0.5
                        if event.key == pygame.K_DOWN:
                            if self.speed > 1:
                                self.speed -= 0.5
                        if event.key == pygame.K_SPACE:
                            if not self.flag:
                                self.old_speed = self.speed
                                self.speed = 0
                                self.flag = True
                            else:
                                self.speed = self.old_speed    
                                self.flag = False

                drone_x , drone_y = self.get_drone_coordinates(drone)
                drone_name_text = self.text.render(drone.name, True, colors.colors["cement"])
                self.screen.blit(drone_name_text, (drone_x, drone_y - 20))               
                r = pygame.Rect(drone_x, drone_y, 20, 20)



                pygame.draw.rect(self.screen, drone.color ,r)

            self.clock.tick(60)
            pygame.display.flip()
        if not self.is_over:
            self.turns += 1
        for drone in drones_to_move:
            drone.current = drone.next
            if drone.path[drone.current] != self.main_map.end:
                drone.path[drone.current].current_drones_count -= 1

            if drone.next + 1 < len(drone.path):
            
                drone.next += 1
            drone.done_turn = False
        if self.main_map.end.current_drones_count == self.main_map.end.max_drones:
            self.is_over = True


    def main_loop(self):
        while self.running:
            self.screen.fill((4, 4, 80))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    continue
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.dragging = True
                        self.last_mouse_pos = event.pos

                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.dragging = False

                elif event.type == pygame.MOUSEMOTION:
                    if self.dragging:
                        dx = event.pos[0] - self.last_mouse_pos[0]
                        dy = event.pos[1] - self.last_mouse_pos[1]

                        self.camera_x += dx
                        self.camera_y += dy
                        self.last_mouse_pos = event.pos

            img = self.text.render(
            f"turns: {self.turns}",
            True,
            (255,255,255,)
            )
            self.screen.blit(img,(40, 0 ) )

            self.draw_drones()                
            pygame.display.flip()





def main():
    try:
        result = main_parser()
        main_map = Map(**result)
        graphic = Graphics(main_map=main_map)
        graphic.main_loop()
    except Exception as e:
        print(e)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nall done")