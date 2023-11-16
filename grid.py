class Grid:
    EMPTY = 0
    SHIP = 1
    MISS = 2
    HIT = 3
    REVEALED_SHIP = 4
    def __init__(self, gridSize, ships_num):
        self._grid = [[Grid.EMPTY for _ in range(gridSize)] for _ in range(gridSize)]
        self.built = False
        self.ships = []
        self.ships_remaining = ships_num
    def updateGrid(self, grid):
        self._grid = grid
    def build(self, shipsPosition):
        for shape in shipsPosition:
            ship = []
            for x in range(shape[2]):
                for y in range(shape[3]):
                    i = shape[1] + y
                    j = shape[0] + x
                    self._grid[i][j] = self.SHIP
                    ship.append([j,i,0])
            self.ships.append(ship)

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
    def isFinished(self):
        print(f'faltam : {self.ships_remaining} navios')
        return self.ships_remaining == 0
    def reveal_ship(self, ship_index):
        ship = self.ships[ship_index]
        for tile in ship:
            x, y = tile[0], tile[1]
            self._grid[y][x] = self.REVEALED_SHIP
            for i in range(x - 1, x + 2):
                for j in range(y - 1, y + 2):
                    if 0 <= i < len(self._grid) and 0 <= j < len(self._grid):
                        if self._grid[j][i] == self.EMPTY:
                            self._grid[j][i] = self.MISS
    def play(self, x, y):
        if self._grid[y][x] == self.EMPTY:
            self._grid[y][x] = self.MISS
            return False
        elif self._grid[y][x] == self.SHIP:
            self._grid[y][x] = self.HIT
            for i, ship in enumerate(self.ships):
                found = False
                for j, tile in enumerate(ship):
                    if tile[0] == x and tile[1] == y:
                        self.ships[i][j][2] = 1
                        found = True
                        break
                if found and all(tile[2] == 1 for tile in ship):
                    print(f'faltam : {self.ships_remaining} navios')
                    self.ships_remaining -= 1
                    print(f'faltam : {self.ships_remaining} navios')
                    self.reveal_ship(i)
                    break
            print(self.ships)
            return True