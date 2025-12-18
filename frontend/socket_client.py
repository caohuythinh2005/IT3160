import json
import socket
import time
from typing import Any, Optional

HOST = "127.0.0.1"
PORT = 50007
ENCODING = "utf-8"
RECV_CHUNK = 4096


def _recv_all(sock: socket.socket, timeout: float) -> bytes:
    sock.settimeout(timeout)
    chunks = []
    while True:
        try:
            data = sock.recv(RECV_CHUNK)
            if not data:
                break
            chunks.append(data)
        except socket.timeout:
            break
    return b"".join(chunks)


def _send_json(
    payload: dict,
    *,
    expect_response: bool = False,
    timeout: float = 0.5,
    retries: int = 3,
    backoff: float = 0.05,
) -> Optional[Any]:
    data = json.dumps(payload).encode(ENCODING)

    for attempt in range(retries):
        try:
            with socket.create_connection((HOST, PORT), timeout=timeout) as sock:
                sock.sendall(data)

                if not expect_response:
                    return True

                sock.shutdown(socket.SHUT_WR)
                raw = _recv_all(sock, timeout)
                if not raw:
                    return None

                return json.loads(raw.decode(ENCODING))

        except Exception:
            if attempt < retries - 1:
                time.sleep(backoff * (attempt + 1))
            else:
                return None


# ========= Public API =========

def send_action(agent_idx: int, action: str) -> bool:
    return bool(
        _send_json(
            {
                "type": "action",
                "agent": agent_idx,
                "action": action,
            }
        )
    )


def send_command(cmd: str, **kwargs) -> bool:
    payload = {"cmd": cmd, **kwargs}
    return bool(_send_json(payload))


def get_status(timeout: float = 0.5) -> Optional[dict]:
    return _send_json({"cmd": "status"}, expect_response=True, timeout=timeout)


def get_state(timeout: float = 0.5):
    resp = get_status(timeout)
    return resp.get("state") if isinstance(resp, dict) else None


if __name__ == "__main__":
    print("socket_client test:", get_status())
