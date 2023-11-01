class Grid:
    EMPTY = 0
    SHIP = 1
    MISS = 2
    HIT = 3
    def __init__(self, gridSize):
        self._grid = [[Grid.EMPTY for _ in range(gridSize)] for _ in range(gridSize)]
        self.built = False
    def updateGrid(self, grid):
        self._grid = grid
    def build(self, shipsPosition):
        for ship in shipsPosition:
            for i in range(ship[3]):
                for j in range(ship[2]):
                    self._grid[ship[1] + i][ship[0] + j] = self.SHIP
        self.built = True
    def gridToSend(self):
        grid = []
        for row in self._grid:
            r = []
            for el in row:
                if el == self.SHIP:
                    r.append(self.EMPTY)
                else:
                    r.append(el)
            grid.append(r)
        return grid
    def getGrid(self):
        return self._grid
    def play(self, x, y):
        if self._grid[y][x] == self.EMPTY:
            self._grid[y][x] = self.MISS
        elif self._grid[y][x] == self.SHIP:
            self._grid[y][x] = self.HIT