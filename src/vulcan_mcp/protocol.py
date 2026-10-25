"""Wire protocol and environment configuration for Vulcan MCP."""
import json
import os
from pathlib import Path
import struct

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 9877
HEADER_STRUCT = struct.Struct("!I")
MAX_MESSAGE_SIZE = 64 * 1024 * 1024
TIMEOUT_DEFAULT = 30.0
TIMEOUT_LONG = 120.0
PROJECT_ROOT = Path(__file__).resolve().parents[2]


class CommandTimeout(ConnectionError):
    """Raised when a socket command times out waiting for Vulcan."""


def _read_dotenv(key: str, env_path: Path | None = None) -> str:
    """Read a key from the project's .env file if not set in os.environ."""
    path = env_path or (PROJECT_ROOT / ".env")
    if not path.is_file():
        return ""
    try:
        for raw_line in path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            if k.strip() == key:
                return v.strip().strip('"').strip("'")
    except OSError:
        pass
    return ""


def _get_config(key: str) -> str:
    val = os.getenv(key, "").strip()
    if val:
        return val
    return _read_dotenv(key)


def get_host() -> str:
    return _get_config("VULCAN_MCP_HOST") or DEFAULT_HOST


def get_port() -> int:
    raw = _get_config("VULCAN_MCP_PORT")
    return int(raw) if raw else DEFAULT_PORT


def get_auth_token() -> str | None:
    token = _get_config("VULCAN_MCP_TOKEN")
    return token or None


def pack_message(envelope: dict) -> bytes:
    payload = json.dumps(envelope, ensure_ascii=False).encode("utf-8")
    if len(payload) > MAX_MESSAGE_SIZE:
        raise ValueError(f"Payload exceeds maximum allowed size ({len(payload)} bytes)")
    return HEADER_STRUCT.pack(len(payload)) + payload


def unpack_message(sock) -> dict:
    raw_len = _recv_exact(sock, HEADER_STRUCT.size)
    (length,) = HEADER_STRUCT.unpack(raw_len)
    if length > MAX_MESSAGE_SIZE:
        raise ValueError(f"Incoming response exceeds maximum allowed size ({length} bytes)")
    payload = _recv_exact(sock, length)
    return json.loads(payload.decode("utf-8"))


def _recv_exact(sock, n: int) -> bytes:
    buf = bytearray()
    while len(buf) < n:
        chunk = sock.recv(min(n - len(buf), 65536))
        if not chunk:
            raise ConnectionError("Socket connection closed by Vulcan listener")
        buf.extend(chunk)
    return bytes(buf)
