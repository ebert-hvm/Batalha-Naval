import time
import sys
import asyncio
import socket
import json

class Communication:
    def __init__(self, ip, port):
        self._host = (ip, port)
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.settimeout(3000)
        self._socket.bind(self._host)
        print(self._socket.getsockname())
        self._loop = asyncio.get_event_loop()
        self.stop = asyncio.Event()
        self.received_data = []
        self.messageDict = None
        self.receiver = None
    def setTimeout(self, timeout):
        self._socket.settimeout(timeout)
    def sendTo(self, messageDict, receiver):
        self._socket.sendto(json.dumps(messageDict).encode('utf-8'), receiver)
    def closeSocket(self):
        self._socket.close()
    def receive(self):
        data, addr = self._socket.recvfrom(1024)
        data = data.decode('utf-8')
        json_data = json.loads(data)
        return json_data, addr
    def receiveAsync(self):
        self.received_data.append(self.receive())
    def received(self):
        return bool(self.received_data)
    def getData(self):
        return self.received_data.pop(0)
    def senToWrapper(self):
        count_tries = 0
        t1 = time.time()
        t2 = time.time()
        while count_tries < 5 and not self.stop.is_set():
            t1 = time.time()
            if t1 > t2 + 1:
                t2 = t1
                count_tries +=1
                self.sendTo(self.messageDict, self.receiver)
    def startSending(self, messageDict, receiver):
        self.sendTo(messageDict, receiver)
        self.messageDict = messageDict
        self.receiver = receiver
        self._loop.run_in_executor(None, self.sendTo)
    def stopSending(self):
        self.stop.set()
    def startReceiving(self):
        self._loop.run_in_executor(None, self.receiveAsync)
    def stopReceiving(self):
        self.stop_event.set()
        self.received_data.clear()