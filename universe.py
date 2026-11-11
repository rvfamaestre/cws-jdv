from cell import Cell, DEAD, ALIVE, PERMANENT, OBJECTIVE


class Universe:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.grid = [[Cell(DEAD) for _ in range(cols)] for _ in range(rows)]

    def set_cell(self, row, col, state):
        if 0 <= row < self.rows and 0 <= col < self.cols:
            self.grid[row][col].state = state

    def get_cell(self, row, col):
        return self.grid[row % self.rows][col % self.cols]

    def count_alive_neighbours(self, row, col):
        count = 0
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                neighbour = self.get_cell(row + dr, col + dc)
                if neighbour.is_alive:
                    count += 1
        return count

    def next_generation(self):
        new_grid = [
            [self.grid[r][c].copy() for c in range(self.cols)] for r in range(self.rows)
        ]
        for r in range(self.rows):
            for c in range(self.cols):
                cell = self.grid[r][c]
                if cell.is_permanent:
                    continue

                neighbours = self.count_alive_neighbours(r, c)

                if cell.is_objective:
                    # Objective markers behave like dead cells but stay visible
                    # until a living pattern reaches that cell.
                    new_grid[r][c].state = ALIVE if neighbours == 3 else OBJECTIVE
                    continue

                if cell.is_alive:
                    new_grid[r][c].state = ALIVE if neighbours in (2, 3) else DEAD
                else:
                    new_grid[r][c].state = ALIVE if neighbours == 3 else DEAD
        self.grid = new_grid

    def clear(self):
        for r in range(self.rows):
            for c in range(self.cols):
                self.grid[r][c] = Cell(DEAD)

    def check_objectives(self, objectives):
        for r, c in objectives:
            if not self.grid[r][c].is_alive:
                return False
        return True

    def copy(self):
        new = Universe(self.rows, self.cols)
        for r in range(self.rows):
            for c in range(self.cols):
                new.grid[r][c] = self.grid[r][c].copy()
        return new
