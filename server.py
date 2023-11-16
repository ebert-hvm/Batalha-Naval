import socket
import traceback
from communication import Communication
from state_machine import StateMachine
from grid import Grid
import json
import uuid
import time

CONFIGURATIONS_PATH = 'configurations.json'

class Player:
    def __init__(self, index, guid, socket):
        self.socket = socket
        self._index = index
        self._guid = guid
    def getIndex(self):
        return self._index
    def getUuid(self):
        return self._guid
    def getBaseMessage(self, action):
        return {"action": action, "clientId": self._guid}

class Server(StateMachine):
    def __init__(self):
        with open(CONFIGURATIONS_PATH, 'r') as file:
            json_config = json.load(file)
        self._game_config = json_config['gameConfigurations']
        host = socket.gethostbyname(socket.gethostname())
        # self._communication = Communication(json_config['server']['ip'], json_config['server']['port'])
        self._communication = Communication(host, 8888)
        self._players: list[Player] = []
        self._grid: list[Grid] = [
            Grid(self._game_config['gridSize'], self._game_config['shipsNumber']),
            Grid(self._game_config['gridSize'], self._game_config['shipsNumber'])
        ]
        self._turn = 0
        self._testFinishTimer = time.time()
        self._communication._socket.bind((host, 8888))
        self._communication._socket.listen(2)
        super().__init__()
    def listenToPlayer(self, socket):
        try:
            data = socket.recv(1024)
            if data is None:
                raise Exception("disconnected")    
            if data:
                return json.loads(data.decode('utf-8'))
        except:
            raise Exception("connection closed")
    def closeSocket(self):
        self._communication.closeSocket()
        for player in self._players:
            player.socket.close()
    def generateUserID(self):
        return str(uuid.uuid4())
    def sendToPlayer(self, player, message):
        # self._communication.sendTo({**player.getBaseMessage(action), **message}, player.getAddress())
        player.socket.sendall(json.dumps(message).encode('utf-8'))
        # self._communication.startSending({**player.getBaseMessage(action), **message}, player.getAddress())

    def connection(self):
        client_socket, _ = self._communication._socket.accept()
        print('accepted')
        dict = self.listenToPlayer(client_socket)
        print(f'dict : {dict}')
        action = dict['action']
        if action != 'connect':
            return False
        
        index = len(self._players)
        player = Player(index, self.generateUserID(), client_socket)
        self._players.append(player)
        self.sendToPlayer(player, {**player.getBaseMessage(action), **{"player": index}})
        print(f"player {index} ({player.getUuid()}) connected!")

        if len(self._players) == 2: return True
        return False
    def setup(self):
        if self.stateChange:
            for player in self._players:
                msg = {**player.getBaseMessage("setup"), **{"configurations": self._game_config}}
                self.sendToPlayer(player, msg)
                # self._communication.sendTo(msg, player.getAddress())
        
        for player in self._players:
            dict = self.listenToPlayer(player.socket)
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
                self.sendToPlayer(player, {**player.getBaseMessage("game"), **msg})
                # self._communication.startSending({**player.getBaseMessage("game"), **msg}, player.getAddress())
        for player in self._players:
            if player.getIndex() == self._turn:
                dict = self.listenToPlayer(player.socket)
                if dict['action'] == 'game' and dict['clientId'] == player.getUuid():
                    x, y = dict['move']
                    print(f'player {self._turn} played {x},{y}')
                    if not self._grid[1 - self._turn].play(x,y):
                        print('troca turno')
                        self._turn = 1 - self._turn
                break
        if self.gameIsFinished(self._turn):
            return True
        for player in self._players:
            if player.getIndex() == 0:
                grids = [self._grid[0].getGrid(), self._grid[1].gridToSend()]
            else:
                grids = [self._grid[0].gridToSend(), self._grid[1].getGrid()]
            print(grids)
            msg = {"player": self._turn, "gameState": grids}
            self.sendToPlayer(player, {**player.getBaseMessage("game"), **msg})
        return False

    def end(self):
        for player in self._players:
            msg = {"winner": self._turn}
            self.sendToPlayer(player, {**player.getBaseMessage("end"), **msg})
            # self._communication.startSending({**player.getBaseMessage("end"), **msg}, player.getAddress())
            player.socket.close()
        return True

def main():
    while True:
        try:
            server = Server()
            while(server.execute()):
                pass
            server.closeSocket()
        except KeyboardInterrupt:
            server.closeSocket()
            break
        except Exception:
            traceback.print_exc()
            server.closeSocket()
            continue

if __name__=='__main__':
    main()