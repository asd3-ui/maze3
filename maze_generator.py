import random

def generate_dungeon(rows, cols):
    grid = [[1 for _ in range(cols)] for _ in range(rows)]
    rooms = []
    
    min_room_size = 4
    max_room_size = 7
    max_rooms_count = 6 

    for _ in range(max_rooms_count):
        w = random.randint(min_room_size, max_room_size)
        h = random.randint(min_room_size, max_room_size)
        x = random.randint(1, cols - w - 1)
        y = random.randint(1, rows - h - 1)
        
        overlap = False
        for other in rooms:
            if (x < other['x'] + other['w'] and x + w > other['x'] and
                y < other['y'] + other['h'] and y + h > other['y']):
                overlap = True
                break
                
        if not overlap:
            for r in range(y, y + h):
                for c in range(x, x + w):
                    grid[r][c] = 0
            rooms.append({'x': x, 'y': y, 'w': w, 'h': h})

    for i in range(len(rooms) - 1):
        x1, y1 = rooms[i]['x'] + rooms[i]['w'] // 2, rooms[i]['y'] + rooms[i]['h'] // 2
        x2, y2 = rooms[i+1]['x'] + rooms[i+1]['w'] // 2, rooms[i+1]['y'] + rooms[i+1]['h'] // 2
        
        for c in range(min(x1, x2), max(x1, x2) + 1):
            grid[y1][c] = 0
        for r in range(min(y1, y2), max(y1, y2) + 1):
            grid[r][x2] = 0

    # إرجاع قيم صحيحة للغرفة الأولى لمنع أخطاء كسر المصفوفات الإحداثية
    player_spawn = (int(rooms[0]['x'] + 2), int(rooms[0]['y'] + 2))
    
    chest_positions = []
    trap_positions = []
    for room in rooms[1:]:
        chest_positions.append((room['x'] + room['w'] // 2, room['y'] + room['h'] // 2))
        trap_positions.append((room['x'] + 1, room['y'] + 1))
        
    return grid, player_spawn, chest_positions, trap_positions
