import json
import math
import os
import sys
import pygame

from maze_generator import generate_dungeon
from entities import Player3D, Enemy3D, VirtualJoystick

pygame.init()
pygame.display.set_caption("Maze 3D")
INFO = pygame.display.Info()
SCREEN_WIDTH = max(640, INFO.current_w or 960)
SCREEN_HEIGHT = max(360, INFO.current_h or 540)
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
clock = pygame.time.Clock()

FOV = math.pi / 3
MAX_DEPTH = 16
NUM_RAYS = max(100, min(180, SCREEN_WIDTH // 6))
DELTA_ANGLE = FOV / NUM_RAYS
RAY_WIDTH = SCREEN_WIDTH / NUM_RAYS
COLOR_BG = (10, 16, 25)
COLOR_CEILING = (21, 31, 44)
COLOR_FLOOR = (29, 34, 39)
ACCENT = (245, 158, 55)
WHITE = (245, 247, 250)
MUTED = (175, 188, 202)
FONT = pygame.font.Font(None, max(24, SCREEN_HEIGHT // 24))
BIG_FONT = pygame.font.Font(None, max(48, SCREEN_HEIGHT // 10))
HIGH_SCORE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "highscore_3d.json")
BACK_KEY = getattr(pygame, "K_AC_BACK", -999)


def load_high_score():
    try:
        with open(HIGH_SCORE_FILE, "r", encoding="utf-8") as file:
            return int(json.load(file).get("high_score", 0))
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        return 0


def save_high_score(score):
    if score <= load_high_score():
        return
    try:
        with open(HIGH_SCORE_FILE, "w", encoding="utf-8") as file:
            json.dump({"high_score": int(score)}, file)
    except OSError:
        pass


def draw_text(surface, text, font, color, center):
    image = font.render(str(text), True, color)
    surface.blit(image, image.get_rect(center=center))


def render_3d_world(player, dungeon_map, enemies):
    width, height = screen.get_size()
    horizon = height // 2
    pygame.draw.rect(screen, COLOR_CEILING, (0, 0, width, horizon))
    pygame.draw.rect(screen, COLOR_FLOOR, (0, horizon, width, height - horizon))
    depth_buffer = [MAX_DEPTH] * NUM_RAYS
    start_angle = player.angle - FOV / 2

    for ray in range(NUM_RAYS):
        angle = start_angle + ray * DELTA_ANGLE
        sin_a, cos_a = math.sin(angle), math.cos(angle)
        distance = 0.05
        while distance < MAX_DEPTH:
            tx = int(player.x + cos_a * distance)
            ty = int(player.y + sin_a * distance)
            if ty < 0 or ty >= len(dungeon_map) or tx < 0 or tx >= len(dungeon_map[0]):
                distance = MAX_DEPTH
                break
            if dungeon_map[ty][tx] == 1:
                break
            distance += 0.035

        corrected = max(0.08, distance * math.cos(player.angle - angle))
        depth_buffer[ray] = corrected
        wall_height = min(height * 1.5, int(height / corrected))
        shade = max(25, min(230, int(225 / (1 + corrected * corrected * 0.11))))
        wall_color = (int(shade * 0.55), int(shade * 0.68), int(shade * 0.82))
        x = int(ray * RAY_WIDTH)
        pygame.draw.rect(screen, wall_color,
                         (x, (height - wall_height) // 2, math.ceil(RAY_WIDTH) + 1, wall_height))

    sprites = []
    for enemy in enemies:
        dx, dy = enemy.x - player.x, enemy.y - player.y
        distance = math.hypot(dx, dy)
        relative = (math.atan2(dy, dx) - player.angle + math.pi) % (2 * math.pi) - math.pi
        if distance > 0.25 and abs(relative) < FOV / 2 + 0.15:
            sprites.append((distance, relative))
    sprites.sort(reverse=True)

    for distance, relative in sprites:
        ray_index = int((relative + FOV / 2) / DELTA_ANGLE)
        if 0 <= ray_index < NUM_RAYS and distance < depth_buffer[ray_index] + 0.25:
            sx = int((relative + FOV / 2) / FOV * width)
            size = min(height, int(height / max(0.25, distance) * 0.52))
            sy = horizon
            glow = max(65, min(255, int(255 / (1 + distance * 0.15))))
            pygame.draw.circle(screen, (glow, 48, 42), (sx, sy), max(8, size // 5))
            pygame.draw.circle(screen, (255, 175, 125), (sx - size // 18, sy - size // 20),
                               max(2, size // 32))


def draw_hud(seconds, joystick):
    width, height = screen.get_size()
    panel = pygame.Surface((min(230, width // 3), 54), pygame.SRCALPHA)
    panel.fill((8, 14, 22, 175))
    screen.blit(panel, (12, 12))
    draw_text(screen, f"TIME  {seconds}s", FONT, WHITE, (panel.get_width() // 2 + 12, 39))
    joystick.draw(screen)


def draw_button(surface, rect, label, fill=ACCENT):
    pygame.draw.rect(surface, (12, 22, 34), rect.inflate(8, 8), border_radius=18)
    pygame.draw.rect(surface, fill, rect, border_radius=16)
    draw_text(surface, label, FONT, WHITE, rect.center)


def main_menu():
    width, height = screen.get_size()
    start = pygame.Rect(width // 2 - min(170, width // 4), height // 2,
                        min(340, width // 2), max(66, height // 9))
    quit_rect = pygame.Rect(start.x, start.bottom + 18, start.width, start.height)
    while True:
        screen.fill(COLOR_BG)
        draw_text(screen, "MAZE 3D", BIG_FONT, WHITE, (width // 2, height // 3))
        draw_text(screen, "ESCAPE THE DUNGEON", FONT, MUTED, (width // 2, height // 3 + 48))
        draw_button(screen, start, "PLAY")
        draw_button(screen, quit_rect, "EXIT", (75, 91, 108))
        draw_text(screen, f"BEST SURVIVAL: {load_high_score()}s", FONT, MUTED,
                  (width // 2, quit_rect.bottom + 34))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, BACK_KEY):
                return False
            if event.type in (pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN):
                pos = event.pos if event.type == pygame.MOUSEBUTTONDOWN else (
                    int(event.x * width), int(event.y * height))
                if start.collidepoint(pos):
                    return True
                if quit_rect.collidepoint(pos):
                    return False
        clock.tick(60)


def game_loop():
    dungeon_map, spawn_pos, enemy_positions, _ = generate_dungeon(21, 21)
    player = Player3D(*spawn_pos)
    enemies = [Enemy3D(x, y, 1.0) for x, y in enemy_positions[:2]]
    if not enemies:
        enemies = [Enemy3D(spawn_pos[0] + 3, spawn_pos[1] + 3, 1.0)]
    joystick = VirtualJoystick(*screen.get_size())
    elapsed = 0.0
    game_over = False
    while True:
        dt = min(clock.tick(60) / 1000.0, 0.05)
        width, height = screen.get_size()
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                return False
            joystick.handle_event(event)
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, BACK_KEY):
                    return True
                if game_over and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    return True
            if game_over and event.type in (pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN):
                return True

        if not game_over:
            keys = pygame.key.get_pressed()
            forward = int(keys[pygame.K_w] or keys[pygame.K_UP])
            backward = int(keys[pygame.K_s] or keys[pygame.K_DOWN])
            turn = int(keys[pygame.K_d] or keys[pygame.K_RIGHT]) - int(
                keys[pygame.K_a] or keys[pygame.K_LEFT])
            touch_move, touch_turn = joystick.get_action()
            player.move(forward - backward + touch_move, dt, dungeon_map)
            player.rotate(turn + touch_turn, dt)
            elapsed += dt
            for enemy in enemies:
                enemy.update_chase(player.x, player.y, dungeon_map, dt)
                if math.hypot(enemy.x - player.x, enemy.y - player.y) < 0.42:
                    game_over = True
                    save_high_score(int(elapsed))
                    break

        render_3d_world(player, dungeon_map, enemies)
        draw_hud(int(elapsed), joystick)
        if game_over:
            overlay = pygame.Surface((width, height), pygame.SRCALPHA)
            overlay.fill((5, 8, 14, 190))
            screen.blit(overlay, (0, 0))
            draw_text(screen, "CAUGHT!", BIG_FONT, (255, 115, 95), (width // 2, height // 2 - 60))
            draw_text(screen, f"SURVIVED {int(elapsed)} SECONDS", FONT, WHITE,
                      (width // 2, height // 2))
            draw_text(screen, "TAP OR PRESS ENTER TO RETURN", FONT, MUTED,
                      (width // 2, height // 2 + 58))
        pygame.display.flip()


def main():
    while main_menu():
        if not game_loop():
            break
    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
