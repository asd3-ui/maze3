import unittest
from collections import deque

from maze_generator import generate_dungeon


class MazeGenerationTests(unittest.TestCase):
    def test_spawn_is_open_and_inside_grid(self):
        grid, spawn, enemies, _ = generate_dungeon(21, 21)
        self.assertEqual(grid[spawn[1]][spawn[0]], 0)
        self.assertTrue(0 <= spawn[0] < len(grid[0]))
        self.assertTrue(0 <= spawn[1] < len(grid))

    def test_all_open_cells_are_connected(self):
        grid, spawn, _, _ = generate_dungeon(21, 21)
        seen = {spawn}
        queue = deque([spawn])
        while queue:
            x, y = queue.popleft()
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nxt = (x + dx, y + dy)
                if (0 <= nxt[1] < len(grid) and 0 <= nxt[0] < len(grid[0])
                        and grid[nxt[1]][nxt[0]] == 0 and nxt not in seen):
                    seen.add(nxt)
                    queue.append(nxt)
        open_cells = {(x, y) for y, row in enumerate(grid)
                      for x, cell in enumerate(row) if cell == 0}
        self.assertEqual(seen, open_cells)

    def test_enemies_are_on_open_cells(self):
        grid, _, enemies, _ = generate_dungeon(21, 21)
        for x, y in enemies:
            self.assertEqual(grid[y][x], 0)

    def test_even_dimensions_are_normalized(self):
        grid, _, _, _ = generate_dungeon(20, 18)
        self.assertEqual(len(grid) % 2, 1)
        self.assertEqual(len(grid[0]) % 2, 1)


if __name__ == "__main__":
    unittest.main()
