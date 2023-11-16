from communication import Communication
from state_machine import StateMachine
from grid import Grid
import json
import time
import socket

CONFIGURATIONS_PATH = "configurations.json"
CONNECTION_MESSAGE = {"action" : "connect"}

class Client(StateMachine):
    def __init__(self):
        with open(CONFIGURATIONS_PATH, 'r') as file:
            json_config = json.load(file)
        host = socket.gethostbyname(socket.gethostname())
        self._communication = Communication(host, 0)
        # self._server = (json_config['server']['ip'], json_config['server']['port'])
        self._server = (json_config['server']['ip'], json_config['server']['port'])
        self._id = ""
        self._playerIndex = 0
        self.turn = False
        self._connected = False
        self._config = {}
        self.setupDone = False
        self._grid: list[Grid] = [None, None]
        self.won = False
        super().__init__()
  
    def myTurn(self):
        return self.turn

    def getBaseMessage(self, action):
        return {"action": action, "clientId": self._id}
  
    def sendMessage(self, messageDict):
        self._communication.sendTo(messageDict, self._server)
  
    def closeSocket(self):
        self._communication.closeSocket()
  
    def getGrids(self):
        if self._playerIndex == 0:
            return [self._grid[0].getGrid(), self._grid[1].getGrid()]
        else:
            return [self._grid[1].getGrid(), self._grid[0].getGrid()]
  
    def getConfig(self):
        return self._config
  
    def connection(self):
        if self.stateChange:
            # self.sendMessage(CONNECTION_MESSAGE)
            self._communication.startSending(CONNECTION_MESSAGE, self._server)
            self._communication.startReceiving()
        if not self._communication.received():
            return False
        response, addr = self._communication.getData()
        if not self._connected:
            if addr == self._server and response['action'] == 'connect':
                self._id = response['clientId']
                self._playerIndex = response['player']
                self._connected = True
                print(self._playerIndex)
                print(self._id)
                self._communication.startReceiving()
            return False
        if addr == self._server and response['action'] == 'setup' and response['clientId'] == self._id:
            self._config = response['configurations']
            self._grid[0] = Grid(self._config['gridSize'], self._config['shipsNumber'])
            self._grid[1] = Grid(self._config['gridSize'], self._config['shipsNumber'])
            return True
        else:
            return False
 
    def haveIWon(self):
        return self.won
 
    def finishSetup(self, ships):
        msg = {
            "shipsPosition": ships
        }
        # self.sendMessage({**self.getBaseMessage('setup'), **msg})
        self._communication.startSending({**self.getBaseMessage('setup'), **msg}, self._server)
        print('setup sent')
        self._communication.startReceiving()
 
    def makeMove(self, x, y):
        if self.turn:
            print(f'making move: {x} {y}')
            if self._grid[1 - self._playerIndex].getGrid()[y][x] != Grid.EMPTY:
                return
            self._communication.startSending({**self.getBaseMessage('game'), **{"move": [x,y]}}, self._server)
            # self.sendMessage({**self.getBaseMessage('game'), **{"move": [x,y]}})
            self.turn = False
 
    def setup(self):
        if self.stateChange:
            print('setting up...')
        if self._communication.received():
            dict, addr = self._communication.getData()
            if addr == self._server and dict['action'] == 'game':
                self._grid[0].updateGrid(dict['gameState'][0])
                self._grid[1].updateGrid(dict['gameState'][1])
                if self._playerIndex == dict['player']:
                    print('my turn')
                    self.turn = True
                return True
        return False

    def game(self):
        if self.stateChange:
            self._communication.startReceiving()
            print('game start')
        if not self._communication.received():
            return False
        dict, addr = self._communication.getData()
        if addr == self._server:
            if dict['action'] == 'end':
                if dict['winner'] == self._playerIndex:
                    print('GANHEI')
                    self.won = True
                else:
                    print('PERDI')
                return True
            elif dict['action'] == 'game':
                print(dict['gameState'])
                self._grid[0].updateGrid(dict['gameState'][0])
                self._grid[1].updateGrid(dict['gameState'][1])
                if self._playerIndex == dict['player']:
                    print('my turn')
                    self.turn = True
        self._communication.startReceiving()
        return False
  
    def end(self):
        self._communication.closeSocket()
        return True


def main():
    client = Client()
    while(client.execute()):
        pass
if __name__ == '__main__':
    main()

