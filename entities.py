import pygame
import math
import heapq

class Player3D:
    def __init__(self, start_x, start_y):
        self.x = start_x
        self.y = start_y
        self.angle = 0.0 # زاوية النظر والالتفات ثلاثية الأبعاد
        self.speed = 0.08
        self.rot_speed = 0.05 # سرعة دوران الكاميرا
        self.health = 100
        self.score = 0

    def move_forward(self, dungeon_map):
        nx = self.x + math.cos(self.angle) * self.speed
        ny = self.y + math.sin(self.angle) * self.speed
        if dungeon_map[int(self.y)][int(nx)] == 0: self.x = nx
        if dungeon_map[int(ny)][int(self.x)] == 0: self.y = ny

    def move_backward(self, dungeon_map):
        nx = self.x - math.cos(self.angle) * self.speed
        ny = self.y - math.sin(self.angle) * self.speed
        if dungeon_map[int(self.y)][int(nx)] == 0: self.x = nx
        if dungeon_map[int(ny)][int(self.x)] == 0: self.y = ny

    def rotate_left(self):
        self.angle -= self.rot_speed

    def rotate_right(self):
        self.angle += self.rot_speed

class Enemy3D:
    def __init__(self, start_x, start_y, speed):
        self.x = float(start_x) + 0.5
        self.y = float(start_y) + 0.5
        self.speed = speed
        self.path = []
        self.recalc_timer = 0

    def heuristic(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def a_star(self, start, goal, dungeon_map):
        start_node = (int(start[1]), int(start[0])) # row, col
        goal_node = (int(goal[1]), int(goal[0]))

        open_set = []
        heapq.heappush(open_set, (0, start_node))
        came_from = {}
        g_score = {start_node: 0}

        while open_set:
            _, current = heapq.heappop(open_set)

            if current == goal_node:
                path = []
                while current in came_from:
                    path.append((float(current[1]) + 0.5, float(current[0]) + 0.5))
                    current = came_from[current]
                path.reverse()
                return path

            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                neighbor = (current[0] + dr, current[1] + dc)
                if 0 <= neighbor[0] < len(dungeon_map) and 0 <= neighbor[1] < len(dungeon_map[0]):
                    if dungeon_map[neighbor[0]][neighbor[1]] == 1: continue
                else: continue

                tg = g_score[current] + 1
                if neighbor not in g_score or tg < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tg
                    f = tg + self.heuristic(neighbor, goal_node)
                    heapq.heappush(open_set, (f, neighbor))
        return []

    def update_chase(self, player_x, player_y, dungeon_map):
        self.recalc_timer += 1
        if self.recalc_timer % 15 == 0 or not self.path:
            self.path = self.a_star((self.x, self.y), (player_x, player_y), dungeon_map)

        if self.path:
            tx, ty = self.path[0]
            dx = tx - self.x
            dy = ty - self.y
            dist = math.hypot(dx, dy)

            if dist < self.speed:
                self.x = tx
                self.y = ty
                self.path.pop(0)
            else:
                self.x += (dx / dist) * self.speed
                self.y += (dy / dist) * self.speed

class VirtualJoystick:
    """جهاز تحكم متطور باللمس للهواتف الذكية (الحركة والالتفات)"""
    def __init__(self, screen_width, screen_height):
        # جزء الحركة (يمين - يسار - أمام - خلف)
        bx1 = 180
        by1 = screen_height - 180
        sz = 65
        self.fwd = pygame.Rect(bx1 - sz//2, by1 - int(sz*1.4), sz, sz)
        self.bwd = pygame.Rect(bx1 - sz//2, by1 + int(sz*0.4), sz, sz)
        
        # جزء الالتفات ورؤية المتاهة (أزرار جانبية يمين الشاشة)
        bx2 = screen_width - 180
        self.rot_l = pygame.Rect(bx2 - int(sz*1.2), by1 - sz//2, sz, sz)
        self.rot_r = pygame.Rect(bx2 + int(sz*0.4), by1 - sz//2, sz, sz)

    def draw(self, surface):
        buttons = [(self.fwd, "▲"), (self.bwd, "▼"), (self.rot_l, "↩"), (self.rot_r, "↪")]
        for rect, icon in buttons:
            s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            pygame.draw.rect(s, (44, 62, 80, 180), (0, 0, rect.width, rect.height), border_radius=15)
            pygame.draw.rect(s, (230, 126, 34, 220), (0, 0, rect.width, rect.height), 3, border_radius=15)
            surface.blit(s, (rect.x, rect.y))
            font = pygame.font.SysFont(None, 42)
            txt = font.render(icon, True, (255, 255, 255))
            surface.blit(txt, txt.get_rect(center=(rect.x + rect.width//2, rect.y + rect.height//2)))

    def get_action(self):
        move, rot = 0, 0 # 1 للأمام، -1 للخلف | 1 يمين، -1 يسار
        pts = [pygame.mouse.get_pos()] if pygame.mouse.get_pressed()[0] else []
        
        for p in pts:
            if self.fwd.collidepoint(p): move = 1
            if self.bwd.collidepoint(p): move = -1
            if self.rot_l.collidepoint(p): rot = -1
            if self.rot_r.collidepoint(p): rot = 1
        return move, rot
