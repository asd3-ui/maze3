import math
import heapq
import pygame


class Player3D:
    def __init__(self, start_x, start_y):
        self.x = float(start_x) + 0.5
        self.y = float(start_y) + 0.5
        self.angle = 0.0
        self.speed = 2.2
        self.rot_speed = 2.5

    def _move_axis(self, nx, ny, dungeon_map):
        radius = 0.18
        if self._is_open(nx + math.copysign(radius, nx - self.x) if nx != self.x else nx,
                         self.y, dungeon_map):
            self.x = nx
        if self._is_open(self.x, ny + math.copysign(radius, ny - self.y) if ny != self.y else ny,
                         dungeon_map):
            self.y = ny

    @staticmethod
    def _is_open(x, y, dungeon_map):
        row, col = int(y), int(x)
        return 0 <= row < len(dungeon_map) and 0 <= col < len(dungeon_map[0]) and dungeon_map[row][col] == 0

    def move(self, direction, dt, dungeon_map):
        if not direction:
            return
        distance = self.speed * dt * max(-1, min(1, direction))
        nx = self.x + math.cos(self.angle) * distance
        ny = self.y + math.sin(self.angle) * distance
        self._move_axis(nx, ny, dungeon_map)

    def rotate(self, direction, dt):
        self.angle = (self.angle + direction * self.rot_speed * dt) % (2 * math.pi)

    def move_forward(self, dungeon_map):
        self.move(1, 1 / 30, dungeon_map)

    def move_backward(self, dungeon_map):
        self.move(-1, 1 / 30, dungeon_map)

    def rotate_left(self):
        self.rotate(-1, 1 / 30)

    def rotate_right(self):
        self.rotate(1, 1 / 30)


class Enemy3D:
    def __init__(self, start_x, start_y, speed=1.0):
        self.x = float(start_x) + 0.5
        self.y = float(start_y) + 0.5
        self.speed = float(speed)
        self.path = []
        self.recalc_timer = 0.0

    @staticmethod
    def _heuristic(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def a_star(self, start, goal, dungeon_map):
        start_node = (int(start[1]), int(start[0]))
        goal_node = (int(goal[1]), int(goal[0]))
        rows, cols = len(dungeon_map), len(dungeon_map[0])
        if not (0 <= goal_node[0] < rows and 0 <= goal_node[1] < cols):
            return []
        frontier = [(0, start_node)]
        came_from = {}
        cost = {start_node: 0}
        visited = set()
        while frontier:
            _, current = heapq.heappop(frontier)
            if current in visited:
                continue
            visited.add(current)
            if current == goal_node:
                path = []
                while current in came_from:
                    path.append((current[1] + 0.5, current[0] + 0.5))
                    current = came_from[current]
                return list(reversed(path))
            for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                nxt = (current[0] + dr, current[1] + dc)
                if not (0 <= nxt[0] < rows and 0 <= nxt[1] < cols):
                    continue
                if dungeon_map[nxt[0]][nxt[1]] == 1:
                    continue
                new_cost = cost[current] + 1
                if new_cost < cost.get(nxt, float("inf")):
                    cost[nxt] = new_cost
                    came_from[nxt] = current
                    heapq.heappush(frontier, (new_cost + self._heuristic(nxt, goal_node), nxt))
        return []

    def update_chase(self, player_x, player_y, dungeon_map, dt=1 / 60):
        self.recalc_timer += dt
        if self.recalc_timer >= 0.45 or not self.path:
            self.path = self.a_star((self.x, self.y), (player_x, player_y), dungeon_map)
            self.recalc_timer = 0.0
        if not self.path:
            return
        tx, ty = self.path[0]
        dx, dy = tx - self.x, ty - self.y
        distance = math.hypot(dx, dy)
        step = self.speed * dt
        if distance <= max(step, 0.04):
            self.x, self.y = tx, ty
            self.path.pop(0)
        elif distance:
            self.x += dx / distance * step
            self.y += dy / distance * step


class VirtualJoystick:
    def __init__(self, screen_width, screen_height):
        self.width = screen_width
        self.height = screen_height
        self.active = {}
        self.mouse_position = None
        self.mouse_down = False
        self._layout()

    def _layout(self):
        w, h = self.width, self.height
        size = max(58, min(94, int(min(w, h) * 0.14)))
        margin = max(22, int(size * 0.45))
        y = h - margin - size
        self.forward = pygame.Rect(margin + size, y - size - 12, size, size)
        self.backward = pygame.Rect(margin + size, y, size, size)
        self.left = pygame.Rect(w - margin - size * 2 - 12, y, size, size)
        self.right = pygame.Rect(w - margin - size, y, size, size)
        self.buttons = [self.forward, self.backward, self.left, self.right]

    def _point(self, event):
        if event.type in (pygame.FINGERDOWN, pygame.FINGERMOTION, pygame.FINGERUP):
            return int(event.x * self.width), int(event.y * self.height)
        return event.pos

    def handle_event(self, event):
        if event.type in (pygame.FINGERDOWN, pygame.FINGERMOTION):
            self.active[event.finger_id] = self._point(event)
        elif event.type == pygame.FINGERUP:
            self.active.pop(event.finger_id, None)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.mouse_down, self.mouse_position = True, event.pos
        elif event.type == pygame.MOUSEMOTION and self.mouse_down:
            self.mouse_position = event.pos
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.mouse_down, self.mouse_position = False, None

    def get_action(self):
        points = list(self.active.values())
        if self.mouse_down and self.mouse_position:
            points.append(self.mouse_position)
        move = turn = 0
        for point in points:
            if self.forward.collidepoint(point):
                move = 1
            elif self.backward.collidepoint(point):
                move = -1
            elif self.left.collidepoint(point):
                turn = -1
            elif self.right.collidepoint(point):
                turn = 1
        return move, turn

    def draw(self, surface):
        labels = ((self.forward, "▲"), (self.backward, "▼"),
                  (self.left, "◀"), (self.right, "▶"))
        for rect, label in labels:
            pressed = any(rect.collidepoint(p) for p in self.active.values())
            if self.mouse_down and self.mouse_position and rect.collidepoint(self.mouse_position):
                pressed = True
            fill = (235, 132, 48, 225) if pressed else (24, 42, 60, 205)
            button = pygame.Surface(rect.size, pygame.SRCALPHA)
            pygame.draw.rect(button, fill, button.get_rect(), border_radius=18)
            pygame.draw.rect(button, (245, 174, 91, 230), button.get_rect(), 3, border_radius=18)
            font = pygame.font.Font(None, max(28, rect.height // 2))
            glyph = font.render(label, True, (255, 255, 255))
            button.blit(glyph, glyph.get_rect(center=button.get_rect().center))
            surface.blit(button, rect)
