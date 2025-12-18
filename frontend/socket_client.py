import socket
import json

class SocketClient:
    def __init__(self, host="127.0.0.1", port=50008):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        print(f"[SocketClient] Connected to {host}:{port}")

    def send(self, msg: dict):
        self.sock.sendall(json.dumps(msg).encode("utf-8"))

    def recv(self):
        data = self.sock.recv(4096)
        if not data:
            return None
        return json.loads(data.decode("utf-8"))
