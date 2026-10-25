"""Length-prefixed JSON framing shared with the MCP server.

Each message is a 4-byte big-endian unsigned length followed by that many
bytes of UTF-8 JSON. Runs inside Vulcan 12's embedded Python 3.5: no
f-strings, no variable annotations.
"""
import json
import struct

HEADER = struct.Struct("!I")
MAX_MESSAGE_SIZE = 64 * 1024 * 1024


def _default(value):
    """Serialise the odd types the Vulcan SDK hands back (numpy scalars, SWIG lists)."""
    try:
        return float(value)
    except (TypeError, ValueError):
        pass
    try:
        return list(value)
    except TypeError:
        return str(value)


def encode(obj):
    payload = json.dumps(obj, ensure_ascii=False, default=_default).encode("utf-8")
    if len(payload) > MAX_MESSAGE_SIZE:
        raise ValueError("Response too large: {} bytes".format(len(payload)))
    return HEADER.pack(len(payload)) + payload


def recv_exact(sock, n):
    chunks = []
    remaining = n
    while remaining > 0:
        chunk = sock.recv(min(remaining, 65536))
        if not chunk:
            raise ConnectionError("Connection closed by peer")
        chunks.append(chunk)
        remaining -= len(chunk)
    return b"".join(chunks)


def read_message(sock):
    (length,) = HEADER.unpack(recv_exact(sock, HEADER.size))
    if length > MAX_MESSAGE_SIZE:
        raise ValueError("Incoming message too large: {} bytes".format(length))
    return json.loads(recv_exact(sock, length).decode("utf-8"))
