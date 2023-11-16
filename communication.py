import sys
import asyncio
import socket
import json

class Communication:
    def __init__(self, ip, port):
        self._host = (ip, port)
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.settimeout(300)
        self._socket.bind(self._host)
        print(self._socket.getsockname())
        self._loop = asyncio.get_event_loop()
        self.stop_event = asyncio.Event()
        self.received_data = []
    def setTimeout(self, timeout):
        self._socket.settimeout(timeout)
    def sendTo(self, messageDict, receiver):
        self._socket.sendto(json.dumps(messageDict).encode('utf-8'), receiver)
    def closeSocket(self):
        self._socket.close()
    def receive(self):
        try:
            data, addr = self._socket.recvfrom(1024)
        except ConnectionResetError:
            print("A client closed the connection.")
            sys.exit()
        data = data.decode('utf-8')
        json_data = json.loads(data)
        return json_data, addr
    def receiveAsync(self):
        self.received_data.append(self.receive())
    def received(self):
        return bool(self.received_data)
    def getData(self):
        return self.received_data.pop(0)
    def startReceiving(self):
        self._loop.run_in_executor(None, self.receiveAsync)
    def stopReceiving(self):
        self.stop_event.set()
        self.received_data.clear()