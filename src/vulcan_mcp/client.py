"""TCP Socket client for communicating with the Maptek Vulcan listener."""

import logging
import socket
import time

from vulcan_mcp.protocol import (
    TIMEOUT_DEFAULT,
    CommandTimeout,
    get_auth_token,
    get_host,
    get_port,
    pack_message,
    unpack_message,
)

logger = logging.getLogger("vulcan_mcp.client")


class VulcanConnectionError(ConnectionError):
    """Raised when the TCP connection to Vulcan cannot be established."""


class VulcanCommandError(RuntimeError):
    """Raised when Vulcan responds with an explicit error status."""


class VulcanMCPClient:
    """Robust client communicating with Maptek Vulcan 12 Desktop over TCP."""

    def __init__(
        self,
        host: str | None = None,
        port: int | str | None = None,
        token: str | None = None,
        timeout: float = TIMEOUT_DEFAULT,
        max_retries: int = 1,
        retry_delay: float = 0.5,
    ):
        self.host = host or get_host()
        if port is not None:
            self.port = int(port)
        else:
            self.port = get_port()
        self.token = token if token is not None else get_auth_token()
        self.default_timeout = timeout
        self.max_retries = max(0, max_retries)
        self.retry_delay = max(0.0, retry_delay)

    def send_command(
        self,
        command_type: str,
        params: dict | None = None,
        timeout: float | None = None,
    ) -> dict:
        """Sends a JSON-RPC like command envelope to Vulcan with automatic retry logic."""
        actual_timeout = timeout if timeout is not None else self.default_timeout
        attempts = 0
        last_exception: Exception | None = None

        while attempts <= self.max_retries:
            attempts += 1
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            sock.settimeout(3.0)
            try:
                sock.connect((self.host, self.port))
            except OSError as exc:
                sock.close()
                last_exception = VulcanConnectionError(
                    f"Cannot connect to Maptek Vulcan on {self.host}:{self.port} ({exc}). "
                    "Ensure Vulcan Desktop is open and vulcan_listener/server.py is running."
                )
                if attempts <= self.max_retries:
                    time.sleep(self.retry_delay)
                    continue
                raise last_exception from exc

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
            except ConnectionError as exc:
                last_exception = exc
                if attempts <= self.max_retries:
                    time.sleep(self.retry_delay)
                    continue
                raise
            finally:
                sock.close()

            if resp.get("status") == "error":
                raise VulcanCommandError(resp.get("message", "Unknown Vulcan error"))
            result = resp.get("result", {})
            return dict(result) if isinstance(result, dict) else {}

        if last_exception:
            raise last_exception
        return {}
