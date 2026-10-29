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
    max_distance = 0
    while queue:
        (row, col), distance = queue.popleft()
        if distance > max_distance:
            farthest, max_distance = (row, col), distance
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            nxt = (row + dr, col + dc)
            if (0 <= nxt[0] < len(grid) and 0 <= nxt[1] < len(grid[0])
                    and grid[nxt[0]][nxt[1]] == 0 and nxt not in visited):
                visited.add(nxt)
                queue.append((nxt, distance + 1))
    return farthest


def generate_dungeon(rows=21, cols=21):
    rows, cols = max(9, int(rows)), max(9, int(cols))
    if rows % 2 == 0:
        rows += 1
    if cols % 2 == 0:
        cols += 1
    grid = _carve_passages(rows, cols)
    spawn = (1, 1)
    exit_cell = _farthest_open(grid, spawn)

    candidates = []
    for row in range(1, rows - 1):
        for col in range(1, cols - 1):
            if grid[row][col] == 0 and (row, col) != spawn:
                distance = abs(row - spawn[0]) + abs(col - spawn[1])
                if distance >= 6:
                    candidates.append((row, col))
    candidates.sort(
        key=lambda cell: abs(cell[0] - exit_cell[0]) + abs(cell[1] - exit_cell[1]),
        reverse=True,
    )
    enemies = [(col, row) for row, col in candidates[:2]]
    chests = [(exit_cell[1], exit_cell[0])]
    return grid, spawn, enemies, []
