import pygame
import math
import heapq

class Player3D:
    def __init__(self, start_x, start_y):
        self.x = float(start_x)
        self.y = float(start_y)
        self.angle = 0.0 
        self.speed = 0.06 # تقليل السرعة قليلاً لتناسب شاشات اللمس
        self.rot_speed = 0.04 
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
        start_node = (int(start[0]), int(start[1])) 
        goal_node = (int(goal[0]), int(goal[1]))

        open_set = []
        heapq.heappush(open_set, (0, start_node))
        came_from = {}
        g_score = {start_node: 0}

        while open_set:
            _, current = heapq.heappop(open_set)

            if current == goal_node:
                path = []
                while current in came_from:
                    path.append((float(current[0]) + 0.5, float(current[1]) + 0.5))
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
        # إعادة حساب المسار كل 30 إطار لحفظ طاقة المعالج وتقليل التجميد
        if self.recalc_timer % 30 == 0 or not self.path:
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
    def __init__(self, screen_width, screen_height):
        bx1 = 180
        by1 = screen_height - 180
        sz = 75 # زيادة الحجم لتناسب أصابع اليد
        self.fwd = pygame.Rect(bx1 - sz//2, by1 - int(sz*1.4), sz, sz)
        self.bwd = pygame.Rect(bx1 - sz//2, by1 + int(sz*0.4), sz, sz)
        
        bx2 = screen_width - 180
        self.rot_l = pygame.Rect(bx2 - int(sz*1.2), by1 - sz//2, sz, sz)
        self.rot_r = pygame.Rect(bx2 + int(sz*0.4), by1 - sz//2, sz, sz)

    def draw(self, surface):
        # رسم الأزرار بأسهم هندسية مرسومة يدوياً كمتجهات بدلاً من الخطوط المنهارة
        buttons = [
            (self.fwd, [(0, 15), (-15, -10), (15, -10)]), # سهم لأعلى
            (self.bwd, [(0, -15), (-15, 10), (15, 10)]),  # سهم لأسفل
            (self.rot_l, [(15, 0), (-10, -15), (-10, 15)]),# التفات يسار
            (self.rot_r, [(-15, 0), (10, -15), (10, 15)]) # التفات يمين
        ]
        for rect, poly_pts in buttons:
            s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            pygame.draw.rect(s, (44, 62, 80, 200), (0, 0, rect.width, rect.height), border_radius=20)
            pygame.draw.rect(s, (230, 126, 34, 255), (0, 0, rect.width, rect.height), 4, border_radius=20)
            
            # رسم السهم الهندسي في منتصف الزر
            center_pts = [(pt[0] + rect.width//2, pt[1] + rect.height//2) for pt in poly_pts]
            pygame.draw.polygon(s, (255, 255, 255), center_pts)
            surface.blit(s, (rect.x, rect.y))

    def get_action(self):
        move, rot = 0, 0
        pts = []
        if pygame.mouse.get_pressed()[0]:
            pts.append(pygame.mouse.get_pos())
            
        for p in pts:
            if self.fwd.collidepoint(p): move = 1
            if self.bwd.collidepoint(p): move = -1
            if self.rot_l.collidepoint(p): rot = -1
            if self.rot_r.collidepoint(p): rot = 1
        return move, rot
