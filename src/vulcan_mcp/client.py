"""TCP Socket client for communicating with the Maptek Vulcan listener."""

import socket

from vulcan_mcp.protocol import (
    TIMEOUT_DEFAULT,
    CommandTimeout,
    get_auth_token,
    get_host,
    get_port,
    pack_message,
    unpack_message,
)


class VulcanMCPClient:
    def __init__(self, host: str | None = None, port: int | None = None):
        self.host = host or get_host()
        self.port = port or get_port()

    def send_command(
        self,
        command_type: str,
        params: dict | None = None,
        timeout: float = TIMEOUT_DEFAULT,
    ) -> dict:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        sock.settimeout(3.0)
        try:
            sock.connect((self.host, self.port))
        except OSError as exc:
            sock.close()
            raise ConnectionError(
                f"Cannot connect to Maptek Vulcan on {self.host}:{self.port} ({exc}). "
                "Ensure Vulcan Desktop is open and plugin/server.py is running."
            ) from exc

        envelope: dict = {"type": command_type, "params": params or {}}
        token = get_auth_token()
        if token:
            envelope["token"] = token

        sock.settimeout(timeout)
        try:
            sock.sendall(pack_message(envelope))
            resp = unpack_message(sock)
        except socket.timeout as exc:
            raise CommandTimeout(
                f"Vulcan timed out after {timeout}s on '{command_type}'. "
                "Check if Vulcan Desktop is showing a modal dialog (e.g., 'No design database is currently open')."
            ) from exc
        finally:
            sock.close()

        if resp.get("status") == "error":
            raise RuntimeError(resp.get("message", "Unknown Vulcan error"))
        result = resp.get("result", {})
        return dict(result) if isinstance(result, dict) else {}
