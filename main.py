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

# إعدادات الـ Raycasting والبيئة الواقعية
FOV = math.pi / 3       # مجال الرؤية (60 درجة)
HALF_FOV = FOV / 2
NUM_RAYS = 240          # عدد الأشعة لضبط دقة الرسوميات وعمق الغموض وثبات الـ FPS
MAX_DEPTH = 16          # أقصى مسافة للرؤية (لتوليد الضباب المظلم)
DELTA_ANGLE = FOV / NUM_RAYS
SCALE = SCREEN_WIDTH // NUM_RAYS

COLOR_BG = (15, 15, 15)
COLOR_CEILING = (20, 24, 30)
COLOR_FLOOR = (35, 35, 35)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Dark Dungeon 3D Realistic Chase")
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
    """محرك رندرة المتاهة ثلاثية الأبعاد الواقعي مع تطبيق الإضاءة الضبابية والظلال"""
    # 1. رسم السقف والأرضية بتأثير العمق المظلم
    pygame.draw.rect(screen, COLOR_CEILING, (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT // 2))
    pygame.draw.rect(screen, COLOR_FLOOR, (0, SCREEN_HEIGHT // 2, SCREEN_WIDTH, SCREEN_HEIGHT // 2))
    
    start_angle = player.angle - HALF_FOV
    
    # 2. إلقاء الأشعة لبناء الجدران الحجرية ثلاثية الأبعاد
    for ray in range(NUM_RAYS):
        angle = start_angle + ray * DELTA_ANGLE
        sin_a = math.sin(angle)
        cos_a = math.cos(angle)
        
        for depth in range(1, int(MAX_DEPTH * 10)):
            dist = depth / 10.0
            target_x = player.x + cos_a * dist
            target_y = player.y + sin_a * dist
            
            if dungeon_map[int(target_y)][int(target_x)] == 1:
                # إزالة تأثير عين السمكة المشوه للأبعاد (Fish-eye correction)
                dist *= math.cos(player.angle - angle)
                
                # حساب الارتفاع الواقعي للجدار بناءً على المسافة
                wall_height = min(SCREEN_HEIGHT, int(SCREEN_HEIGHT / (dist + 0.0001)))
                
                # إضاءة واقعية متدرجة (كلما ابتعد الجدار أصبح مظلماً كأنه في الظل والضباب)
                shade = 255 / (1 + dist * dist * 0.2)
                color = (int(shade * 0.4), int(shade * 0.45), int(shade * 0.5)) # تأثير حجري مزرق دافئ
                
                pygame.draw.rect(screen, color, (ray * SCALE, (SCREEN_HEIGHT - wall_height) // 2, SCALE, wall_height))
                break

    # 3. رندرة الأعداء والمطاردين ثلاثيي الأبعاد داخل البيئة
    for enemy in enemies:
        ex = enemy.x - player.x
        ey = enemy.y - player.y
        
        # تحويل إحداثيات العدو لنسب الرؤية أمام كود زاوية اللاعب
        theta = math.atan2(ey, ex)
        gamma = theta - player.angle
        if ex > 0 and start_angle % (2*math.pi) > math.pi: gamma += 2*math.pi
        
        if -HALF_FOV < gamma < HALF_FOV:
            screen_x = int((gamma + HALF_FOV) / DELTA_ANGLE)
            dist = math.hypot(ex, ey)
            if 0.2 < dist < MAX_DEPTH:
                sprite_height = min(SCREEN_HEIGHT, int(SCREEN_HEIGHT / dist))
                shade = 255 / (1 + dist * dist * 0.1)
                # رسم كائن العدو على شكل كتلة ضوء أرجوانية مرعبة تقترب منك
                e_color = (int(shade * 0.6), int(shade * 0.1), int(shade * 0.6))
                
                pygame.draw.circle(screen, e_color, (screen_x, SCREEN_HEIGHT // 2), sprite_height // 4)

def main_menu():
    font_title = pygame.font.SysFont(None, 64)
    font_buttons = pygame.font.SysFont(None, 36)
    
    if not os.path.exists("icon.png"):
        icon_surf = pygame.Surface((512, 512))
        icon_surf.fill(COLOR_BG)
        pygame.draw.circle(icon_surf, (192, 57, 43), (256, 256), 180, 20)
        pygame.image.save(icon_surf, "icon.png")
        
    while True:
        screen.fill(COLOR_BG)
        draw_text("REALISTIC LABYRINTH 3D CHASE", font_title, (192, 57, 43), screen, SCREEN_WIDTH//2, 150)
        draw_text(f"🏆 High Score Record: {load_high_score()} Seconds Alive", font_buttons, COLOR_ACCENT, screen, SCREEN_WIDTH//2, 230)
        
        btn_start = pygame.Rect(SCREEN_WIDTH//2 - 120, 360, 240, 60)
        pygame.draw.rect(screen, (142, 68, 173), btn_start, border_radius=10)
        draw_text("ENTER DUNGEON", font_buttons, COLOR_TEXT, screen, SCREEN_WIDTH//2, 390)
        
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

def draw_text(text, font, color, surface, x, y):
    t_obj = font.render(text, True, color)
    surface.blit(t_obj, t_obj.get_rect(center=(x, y)))

def game_loop():
    # إنشاء خريطة ضخمة ومتاهة معقدة للغاية (50x50 block array)
    dungeon_map, spawn_pos, chests_locs, _ = generate_dungeon(50, 50)
    player = Player3D(spawn_pos[0], spawn_pos[1])
    
    # توزيع الأعداء والمطاردين في أرجاء المتاهة
    enemies = [
        Enemy3D(chests_locs[1][0], chests_locs[1][1], 0.035),
        Enemy3D(chests_locs[2][0], chests_locs[2][1], 0.045)
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
                    return # استخدام زر تراجع الهاتف للعودة خطوة للخلف للمنيو الرئيسي

        if not game_over:
            survival_seconds = (pygame.time.get_ticks() - start_ticks) // 1000
            
            # 1. مدخلات كيبورد الحاسوب التقليدية
            keys = pygame.key.get_pressed()
            if keys[pygame.K_w] or keys[pygame.K_UP]: player.move_forward(dungeon_map)
            if keys[pygame.K_s] or keys[pygame.K_DOWN]: player.move_backward(dungeon_map)
            if keys[pygame.K_a] or keys[pygame.K_LEFT]: player.rotate_left()
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]: player.rotate_right()
            
            # 2. مدخلات الهاتف المحمول الذكي عبر الجويستيك اللمسي
            m_input, r_input = joystick.get_action()
            if m_input == 1: player.move_forward(dungeon_map)
            if m_input == -1: player.move_backward(dungeon_map)
            if r_input == -1: player.rotate_left()
            if r_input == 1: player.rotate_right()
            
            # تحديث ذكاء الخصم للمطاردة وحساب أقصر مسار عبر خوارزمية A* المتطورة
            for enemy in enemies:
                enemy.update_chase(player.x, player.y, dungeon_map)
                # إذا مسكك العدو واقترب منك تنتهي اللعبة فوراً (ميكانيكيات ألعاب الرعب والمطاردة)
                if math.hypot(enemy.x - player.x, enemy.y - player.y) < 0.4:
                    game_over = True
                    save_high_score(survival_seconds)

        # رندرة البيئة الواقعية ثلاثية الأبعاد
        render_3d_world(player, dungeon_map, enemies)
        joystick.draw(screen)
        
        # عرض معلومات النجاة والوقت الصامد الحرج
        font = pygame.font.SysFont(None, 32)
        if not game_over:
            draw_text(f"⏱️ Survival Time: {survival_seconds} Seconds", font, (255, 255, 255), screen, 160, 30)
        else:
            draw_text("💥 CAUGHT BY THE LABYRINTH BEAST!", pygame.font.SysFont(None, 54), (192, 57, 43), screen, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 40)
            draw_text(f"You survived for {survival_seconds} seconds. Press Back to exit.", font, COLOR_TEXT, screen, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 20)

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    while True:
        main_menu()
        game_loop()
