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
    def __init__(
        self,
        host: str | None = None,
        port: int | str | None = None,
        token: str | None = None,
        timeout: float = TIMEOUT_DEFAULT,
    ):
        self.host = host or get_host()
        if port is not None:
            self.port = int(port)
        else:
            self.port = get_port()
        self.token = token if token is not None else get_auth_token()
        self.default_timeout = timeout

    def send_command(
        self,
        command_type: str,
        params: dict | None = None,
        timeout: float | None = None,
    ) -> dict:
        actual_timeout = timeout if timeout is not None else self.default_timeout
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
        active_token = self.token or get_auth_token()
        if active_token:
            envelope["token"] = active_token

        sock.settimeout(actual_timeout)
        try:
            sock.sendall(pack_message(envelope))
            resp = unpack_message(sock)
        except socket.timeout as exc:
            raise CommandTimeout(
                f"Vulcan timed out after {actual_timeout}s on '{command_type}'. "
                "Check if Vulcan Desktop is showing a modal dialog (e.g., 'No design database is currently open')."
            ) from exc
        finally:
            sock.close()

        if resp.get("status") == "error":
            raise RuntimeError(resp.get("message", "Unknown Vulcan error"))
        result = resp.get("result", {})
        return dict(result) if isinstance(result, dict) else {}
