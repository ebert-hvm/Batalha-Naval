from communication import Communication
from state_machine import StateMachine
from grid import Grid
import json
import time

CONFIGURATIONS_PATH = "configurations.json"
RESPONSE_TIMEOUT = 45
CONNECTION_MESSAGE = {"action" : "connect"}

class Client(StateMachine):
    def __init__(self):
        with open(CONFIGURATIONS_PATH, 'r') as file:
            json_config = json.load(file)
        self._communication = Communication(json_config['client']['ip'], json_config['client']['port'])
        self._server = (json_config['server']['ip'], json_config['server']['port'])
        self._id = ""
        self._playerIndex = 0
        self._connected = False
        self._config = {}
        self.setupDone = False
        self._grid: list[Grid] = [None, None]
        super().__init__()
    def getBaseMessage(self, action):
        return {"action": action, "clientId": self._id}
    def sendMessage(self, messageDict):
        self._communication.sendTo(messageDict, self._server)

    def closeSocket(self):
        self._communication.closeSocket()
    def connection(self):
        if self.stateChange:
            self.sendMessage(CONNECTION_MESSAGE)
        response, addr = self._communication.receive()
        if not self._connected:
            if addr == self._server and response['action'] == 'connect':
                self._id = response['clientId']
                self._playerIndex = response['player']
                self._connected = True
                print(self._playerIndex)
                print(self._id)
            return False
        if addr == self._server and response['action'] == 'setup' and response['clientId'] == self._id:
            self._config = response['configurations']
            self._grid[0] = Grid(self._config['gridSize'])
            self._grid[1] = Grid(self._config['gridSize'])
            return True
        else:
            return False
        
    def setup(self):
        if self.stateChange:
            print('setting up...')
            self._testTimer = time.time()
        if time.time() > self._testTimer + 1:
            msg = {
                "shipsPosition": [[0,0,5,1]] 
            }
            self.sendMessage({**self.getBaseMessage('setup'), **msg})
            print('setup sent')
            self._testTimer = float('inf')
            self.setupDone = True
        elif self.setupDone:
            dict, addr = self._communication.receive()
            if addr == self._server and dict['action'] == 'game':
                self._grid[0].updateGrid(dict['gameState'][0])
                self._grid[1].updateGrid(dict['gameState'][1])
                if dict['player'] == self._playerIndex:
                    time.sleep(1)
                    move = [0,0]
                    print('making move')
                    self.sendMessage({**self.getBaseMessage('game'), **{"move": move}})
                return True
        return False

    def game(self):
        if self.stateChange:
            print('game start')
        dict, addr = self._communication.receive()
        print(dict)
        if addr == self._server:
            if dict['action'] == 'end':
                if dict['winner'] == self._playerIndex:
                    print('GANHEI')
                else:
                    print('PERDI')
                return True
            elif dict['action'] == 'game':
                self._grid[0].updateGrid(dict['gameState'][0])
                self._grid[1].updateGrid(dict['gameState'][1])
                if dict['player'] == self._playerIndex:
                    time.sleep(1)
                    move = [0,0]
                    print('making move')
                    self.sendMessage({**self.getBaseMessage('game'), **{"move": move}})
        return False
    def end(self):
        self._communication.closeSocket()
        return True


def Main():
    client = Client()
    while(client.execute()):
        pass
if __name__ == '__main__':
    Main()

