import threading
import time
import sys
import asyncio
import socket
import json

class Communication:
    def __init__(self, ip, port):
        self._host = (ip, port)
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.settimeout(3000)
        # print(self._socket.getsockname())
        self.stop_receiving = threading.Event()
        self.received_data = []
        self.messageDict = None
        self.receiver = None
    def connect(self, server):
        print(f'connecting: {server[0]} {server[1]}')
        self._socket.connect(server)
    def setTimeout(self, timeout):
        self._socket.settimeout(timeout)
    def send(self):
        try:
            self._socket.sendall(json.dumps(self.messageDict).encode('utf-8'))
        except socket.error:
            pass
    def sendTo(self, messageDict, receiver):
        self._socket.sendto(json.dumps(messageDict).encode('utf-8'), receiver)
    def closeSocket(self):
        self.stop_receiving.set()
        time.sleep(1)  # To ensure sending/receiving threads finish
        self._socket.close()
        
    def receive(self):
        self.received_data.clear()
        while not self.stop_receiving.is_set():
            try:
                data = self._socket.recv(1024)
                if data is not None:
                    json_data = json.loads(data.decode('utf-8'))
                    if json_data is not None:
                        self.received_data.append(json_data)
                else:
                    socket.close()
            except:
                time.sleep(0.1)
                continue
    def receiveAsync(self):
        self.received_data.append(self.receive())
    def received(self):
        return len(self.received_data) != 0
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
        self.messageDict = messageDict
        self.receiver = receiver
        send_thread = threading.Thread(target=self.send)
        send_thread.start()
    def startReceiving(self):
        receive_thread = threading.Thread(target=self.receive)
        receive_thread.start()
    def stopReceiving(self):
        self.stop_receiving.set()
        self.received_data.clear()