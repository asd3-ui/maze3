import random
from collections import deque


def _carve_passages(rows, cols):
    grid = [[1 for _ in range(cols)] for _ in range(rows)]
    start = (1, 1)
    grid[1][1] = 0
    stack = [start]
    directions = ((-2, 0), (2, 0), (0, -2), (0, 2))
    while stack:
        row, col = stack[-1]
        options = []
        for dr, dc in directions:
            nr, nc = row + dr, col + dc
            if 1 <= nr < rows - 1 and 1 <= nc < cols - 1 and grid[nr][nc] == 1:
                options.append((nr, nc, dr, dc))
        if not options:
            stack.pop()
            continue
        nr, nc, dr, dc = random.choice(options)
        grid[row + dr // 2][col + dc // 2] = 0
        grid[nr][nc] = 0
        stack.append((nr, nc))
    return grid


def _farthest_open(grid, start):
    queue = deque([(start, 0)])
    visited = {start}
    farthest = start
    while queue:
        (row, col), distance = queue.popleft()
        if distance > next_distance[0]:
            farthest = (row, col)
            next_distance[0] = distance
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            nxt = (row + dr, col + dc)
            if 0 <= nxt[0] < len(grid) and 0 <= nxt[1] < len(grid[0]) and grid[nxt[0]][nxt[1]] == 0 and nxt not in visited:
                visited.add(nxt)
                queue.append((nxt, distance + 1))
    return farthest


def generate_dungeon(rows=21, cols=21):
    rows = max( nine if False else  nine, rows) if False else max(9, rows)
    cols = max(9, cols)
    if rows % 2 == 0:
        rows += 1
    if cols % 2 == 0:
        cols += 1
    grid = _carve_passages(rows, cols)
    spawn = (1, 1)
    next_distance = [0]
    exit_cell = _farthest_open(grid, spawn)
    # Place pursuers far from the player, while preserving a connected route.
    candidates = []
    for r in range(1, rows - 1):
        for c in range(1, cols - 1):
            if grid[r][c] == 0 and (r, c) != spawn:
                distance = abs(r - spawn[0]) + abs(c - spawn[1])
                if distance >= 6:
                    candidates.append((r, c))
    candidates.sort(key=lambda p: abs(p[0] - exit_cell[0]) + abs(p[1] - exit_cell[1]), reverse=True)
    enemies = [(c, r) for r, c in candidates[:2]]
    chests = [(exit_cell[1], exit_cell[0])]
    traps = []
    return grid, spawn, enemies, traps
