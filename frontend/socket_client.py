import socket
import json

class SocketClient:
    def __init__(self, host="127.0.0.1", port=50008):
        self.host = host
        self.port = port
        self.sock = None
        self._buffer = ""

    def connect(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(1.0)
            self.sock.connect((self.host, self.port))
            return True
        except Exception as e:
            print(f"[SocketClient] Connect error: {e}")
            self.sock = None
            return False

    def send(self, msg: dict):
        if self.sock:
            try:
                self.sock.sendall((json.dumps(msg) + "\n").encode("utf-8"))
            except Exception as e:
                print(f"[SocketClient] Send error: {e}")
                self.sock = None

    def recv(self, timeout=0.1):
        if not self.sock:
            return None
        try:
            self.sock.settimeout(timeout)
            data = self.sock.recv(8192)
            if not data:
                return None

            self._buffer += data.decode("utf-8")
            if "\n" not in self._buffer:
                return None

            line, self._buffer = self._buffer.split("\n", 1)
            line = line.strip()
            if not line:
                return None
            return json.loads(line)
        except Exception as e:
            print(f"[SocketClient] Recv error: {e}")
            return None

    def close(self):
        if self.sock:
            self.sock.close()
            self.sock = None