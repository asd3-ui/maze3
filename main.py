import pygame
import sys
import json
import os
import math
from maze_generator import generate_dungeon
from entities import Player3D, Enemy3D, VirtualJoystick

pygame.init()
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

# تحسين أداء الهاتف: 120 شعاعاً (بدلاً من 240) يعطي أداءً ممتازاً ومستقراً جداً وبدون لاغ
FOV = math.pi / 3       
HALF_FOV = FOV / 2
NUM_RAYS = 120          
MAX_DEPTH = 12          
DELTA_ANGLE = FOV / NUM_RAYS
SCALE = SCREEN_WIDTH // NUM_RAYS

COLOR_BG = (15, 15, 15)
COLOR_CEILING = (20, 24, 30)
COLOR_FLOOR = (35, 35, 35)
COLOR_ACCENT = (230, 126, 34)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Dark Dungeon 3D Stable")
clock = pygame.time.Clock()
HIGH_SCORE_FILE = "highscore_3d.json"

def load_high_score():
    if os.path.exists(HIGH_SCORE_FILE):
        try:
            with open(HIGH_SCORE_FILE, "r") as f: return json.load(f).get("high_score", 0)
        except: return 0
    return 0

def save_high_score(score):
    if score > load_high_score():
        try:
            with open(HIGH_SCORE_FILE, "w") as f: json.dump({"high_score": score}, f)
        except: pass

def render_3d_world(player, dungeon_map, enemies):
    # رسم الخلفية والسقف والأرضية
    pygame.draw.rect(screen, COLOR_CEILING, (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT // 2))
    pygame.draw.rect(screen, COLOR_FLOOR, (0, SCREEN_HEIGHT // 2, SCREEN_WIDTH, SCREEN_HEIGHT // 2))
    
    start_angle = player.angle - HALF_FOV
    
    for ray in range(NUM_RAYS):
        angle = start_angle + ray * DELTA_ANGLE
        sin_a = math.sin(angle)
        cos_a = math.cos(angle)
        
        for depth in range(1, int(MAX_DEPTH * 10)):
            dist = depth / 10.0
            target_x = player.x + cos_a * dist
            target_y = player.y + sin_a * dist
            
            # فحص حدود الخريطة لمنع تداخل العمليات والمحافظة على الذاكرة
            if 0 <= int(target_y) < len(dungeon_map) and 0 <= int(target_x) < len(dungeon_map[0]):
                if dungeon_map[int(target_y)][int(target_x)] == 1:
                    dist *= math.cos(player.angle - angle)
                    wall_height = min(SCREEN_HEIGHT, int(SCREEN_HEIGHT / (dist + 0.0001)))
                    
                    shade = 255 / (1 + dist * dist * 0.3)
                    color = (int(shade * 0.35), int(shade * 0.4), int(shade * 0.45))
                    
                    pygame.draw.rect(screen, color, (ray * SCALE, (SCREEN_HEIGHT - wall_height) // 2, SCALE, wall_height))
                    break
            else:
                break

    # رندرة الخصوم والمطاردين
    for enemy in enemies:
        ex = enemy.x - player.x
        ey = enemy.y - player.y
        theta = math.atan2(ey, ex)
        gamma = theta - player.angle
        
        if ex > 0 and start_angle % (2*math.pi) > math.pi: gamma += 2*math.pi
        
        if -HALF_FOV < gamma < HALF_FOV:
            screen_x = int((gamma + HALF_FOV) / DELTA_ANGLE) * SCALE
            dist = math.hypot(ex, ey)
            if 0.3 < dist < MAX_DEPTH:
                sprite_height = min(SCREEN_HEIGHT, int(SCREEN_HEIGHT / dist))
                shade = 255 / (1 + dist * dist * 0.1)
                e_color = (int(shade * 0.7), int(shade * 0.1), int(shade * 0.2))
                pygame.draw.circle(screen, e_color, (screen_x, SCREEN_HEIGHT // 2), sprite_height // 5)

def draw_custom_hud(time_alive, is_game_over):
    """واجهة مستخدم هندسية بديلة عن الخطوط لمنع انهيار تطبيق الأندرويد"""
    if not is_game_over:
        # رسم شريط علوي يوضح الوقت بالثواني عبر مربعات رسومية مبسطة
        pygame.draw.rect(screen, (44, 62, 80), (20, 20, 240, 45), border_radius=8)
        pygame.draw.rect(screen, COLOR_ACCENT, (25, 25, min(230, time_alive * 4), 35), border_radius=5)
    else:
        # شاشة الموت الحجرية الحمراء
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((192, 57, 43, 200)) # غطاء أحمر شفاف للموت
        screen.blit(overlay, (0,0))
        # رسم جمجمة/شكل هندسي تحذيري في المنتصف
        pygame.draw.rect(screen, (255, 255, 255), (SCREEN_WIDTH//2 - 50, SCREEN_HEIGHT//2 - 50, 100, 100), border_radius=20)

def main_menu():
    # لا تنشئ ملفات أثناء التشغيل على أندرويد؛ الأيقونة تخص إعدادات البناء فقط.
    while True:
        screen.fill(COLOR_BG)
        
        # زر مستطيل كبير لبدء اللعبة الهندسية (الدخول للدهليز)
        btn_start = pygame.Rect(SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 - 40, 300, 80)
        pygame.draw.rect(screen, (230, 126, 34), btn_start, border_radius=15)
        pygame.draw.polygon(screen, (255,255,255), [(SCREEN_WIDTH//2 - 15, SCREEN_HEIGHT//2 - 20), (SCREEN_WIDTH//2 - 15, SCREEN_HEIGHT//2 + 20), (SCREEN_WIDTH//2 + 20, SCREEN_HEIGHT//2)])
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_AC_BACK:
                    pygame.quit()
                    sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn_start.collidepoint(pygame.mouse.get_pos()): return

        pygame.display.flip()
        clock.tick(60)

def game_loop():
    # تصغير حجم الخريطة إلى 20×20 لضمان أداء مستقر وسلس وبدون استهلاك للذاكرة على الهاتف
    dungeon_map, spawn_pos, chests_locs, _ = generate_dungeon(20, 20)
    player = Player3D(spawn_pos[0], spawn_pos[1])
    
    enemies = [
        Enemy3D(chests_locs[0][0], chests_locs[0][1], 0.035)
    ]
    
    joystick = VirtualJoystick(SCREEN_WIDTH, SCREEN_HEIGHT)
    start_ticks = pygame.time.get_ticks()
    running = True
    game_over = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_AC_BACK:
                    return # العودة للمنيو عند ضغط زر التراجع للهاتف

        survival_seconds = (pygame.time.get_ticks() - start_ticks) // 1000

        if not game_over:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_w] or keys[pygame.K_UP]: player.move_forward(dungeon_map)
            if keys[pygame.K_s] or keys[pygame.K_DOWN]: player.move_backward(dungeon_map)
            if keys[pygame.K_a] or keys[pygame.K_LEFT]: player.rotate_left()
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]: player.rotate_right()
            
            m_input, r_input = joystick.get_action()
            if m_input == 1: player.move_forward(dungeon_map)
            if m_input == -1: player.move_backward(dungeon_map)
            if r_input == -1: player.rotate_left()
            if r_input == 1: player.rotate_right()
            
            for enemy in enemies:
                enemy.update_chase(player.x, player.y, dungeon_map)
                if math.hypot(enemy.x - player.x, enemy.y - player.y) < 0.45:
                    game_over = True
                    save_high_score(survival_seconds)

        render_3d_world(player, dungeon_map, enemies)
        joystick.draw(screen)
        draw_custom_hud(survival_seconds, game_over)

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    while True:
        main_menu()
        game_loop()
