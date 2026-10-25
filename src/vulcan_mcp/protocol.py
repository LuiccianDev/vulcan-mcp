"""Wire protocol and environment configuration for Vulcan MCP."""
import json
import os
import struct

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 9877
HEADER_STRUCT = struct.Struct("!I")
MAX_MESSAGE_SIZE = 64 * 1024 * 1024
TIMEOUT_DEFAULT = 30.0
TIMEOUT_LONG = 120.0


class CommandTimeout(ConnectionError):
    """Raised when a socket command times out waiting for Vulcan."""


def get_host() -> str:
    return os.environ.get("VULCAN_MCP_HOST", DEFAULT_HOST).strip() or DEFAULT_HOST


def get_port() -> int:
    raw = os.environ.get("VULCAN_MCP_PORT", "").strip()
    return int(raw) if raw else DEFAULT_PORT


def get_auth_token() -> str | None:
    token = os.environ.get("VULCAN_MCP_TOKEN", "").strip()
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
