from communication import Communication
from state_machine import StateMachine
from grid import Grid
import json
import uuid
import time

CONFIGURATIONS_PATH = 'configurations.json'

class Player:
    def __init__(self, index, guid, addr):
        self._index = index
        self._guid = guid
        self._addr = addr
    def getIndex(self):
        return self._index
    def getAddress(self):
        return self._addr
    def getUuid(self):
        return self._guid
    def getBaseMessage(self, action):
        return {"action": action, "clientId": self._guid}

class Server(StateMachine):
    def __init__(self):
        with open(CONFIGURATIONS_PATH, 'r') as file:
            json_config = json.load(file)
        self._game_config = json_config['gameConfigurations']
        self._communication = Communication(json_config['server']['ip'], json_config['server']['port'])
        self._players: list[Player] = []
        self._grid: list[Grid] = [
            Grid(self._game_config['gridSize'], self._game_config['shipsNumber']),
            Grid(self._game_config['gridSize'], self._game_config['shipsNumber'])
        ]
        self._turn = 0
        self._testFinishTimer = time.time()
        super().__init__()
    def listen(self):
        return self._communication.receive()
    def closeSocket(self):
        self._communication.closeSocket()
    def generateUserID(self):
        return str(uuid.uuid4())
    def sendToPlayer(self, player, message, action):
        self._communication.sendTo({**player.getBaseMessage(action), **message}, player.getAddress())

    def connection(self):
        dict, addr = self.listen()
        for player in self._players:
            if player.getAddress() == addr:
                return False
        action = dict['action']
        if action != 'connect':
            return False
        
        index = len(self._players)
        player = Player(index, self.generateUserID(), addr)
        self._players.append(player)
        self.sendToPlayer(player, {"player": index}, action)
        print(f"player {index}({player.getUuid()}) connected!")

        if len(self._players) == 2: return True
        return False
    def setup(self):
        if self.stateChange:
            for player in self._players:
                msg = {**player.getBaseMessage("setup"), **{"configurations": self._game_config}}
                self._communication.sendTo(msg, player.getAddress())
        
        dict, _ = self.listen()
        print('received')
        for player in self._players:
            if dict['clientId'] == player.getUuid() and dict['action'] == 'setup':
                index = player.getIndex()
                if self._grid[index].built:
                    return False
                self._grid[index].build(dict['shipsPosition'])
        for grid in self._grid:
            if not grid.built:
                return False
        return True
    def gameIsFinished(self, turn):
        return self._grid[1 - turn].isFinished()
    def nextTurn(self, x, y):
        return 1 - self._turn
    def game(self):
        if self.stateChange:
            print('game start')
            for player in self._players:
                if player.getIndex() == 0:
                    grids = [self._grid[0].getGrid(), self._grid[1].gridToSend()]
                else:
                    grids = [self._grid[0].gridToSend(), self._grid[1].getGrid()]
                msg = {"player": self._turn, "gameState": grids}
                self._communication.sendTo({**player.getBaseMessage("game"), **msg}, player.getAddress())
        dict, _ = self.listen()
        turnPlayer = None
        for player in self._players:
            if player.getIndex() == self._turn:
                turnPlayer = player
        if dict['action'] == 'game' and dict['clientId'] == turnPlayer.getUuid():
            x, y = dict['move']
            print(f'player {self._turn} played {x},{y}')
            if not self._grid[1 - self._turn].play(x,y):
                self._turn = 1 - self._turn
            for player in self._players:
                if player.getIndex() == 0:
                    grids = [self._grid[0].getGrid(), self._grid[1].gridToSend()]
                else:
                    grids = [self._grid[0].gridToSend(), self._grid[1].getGrid()]
                print(grids)
                msg = {"player": self._turn, "gameState": grids}
                self._communication.sendTo({**player.getBaseMessage("game"), **msg}, player.getAddress())
            return self.gameIsFinished(self._turn)
        return False

    def end(self):
        for player in self._players:
            msg = {"winner": self._turn}
            self._communication.sendTo({**player.getBaseMessage("end"), **msg}, player.getAddress())
        self._communication.closeSocket()
        return True

def main():
    while True:
        try:
            server = Server()
            while(server.execute()):
                pass
        except KeyboardInterrupt:
            break
        else:
            continue

if __name__=='__main__':
    main()