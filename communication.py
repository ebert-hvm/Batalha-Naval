import socket
import json

class Communication:
    def __init__(self, ip, port):
        self._host = (ip, port)
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.settimeout(15)
        self._socket.bind(self._host)
    def sendTo(self, messageDict, receiver):
        self._socket.sendto(json.dumps(messageDict).encode('utf-8'), receiver)
    def closeSocket(self):
        self._socket.close()
    def receive(self):
        data, addr = self._socket.recvfrom(1024)
        data = data.decode('utf-8')
        json_data = json.loads(data)
        return json_data, addr