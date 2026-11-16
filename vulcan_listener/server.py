"""Maptek Vulcan 12 MCP Socket Listener (Python 3.5 compatible).

Run from Maptek Vulcan Desktop via:
    File > Python Script > vulcan_listener/server.py (check 'Run in shell window')
"""

import hmac
import os
import socket
import sys
import traceback

# Ensure package imports work when executed directly by path
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import wire  # noqa: E402
from handlers import (  # noqa: E402, F401
    block_models,
    canvas,
    code,
    design,
    drillholes,
    legends,
    system,
    triangulations,
)
from handlers.common import COMMANDS, CommandError  # noqa: E402

HOST = os.environ.get("VULCAN_MCP_HOST", "127.0.0.1").strip() or "127.0.0.1"
PORT = int(os.environ.get("VULCAN_MCP_PORT", "9877").strip() or "9877")
TOKEN = os.environ.get("VULCAN_MCP_TOKEN", "").strip()
CLIENT_READ_TIMEOUT = float(os.environ.get("VULCAN_MCP_CLIENT_TIMEOUT", "5.0").strip() or "5.0")
LOOPBACK_HOSTS = ("127.0.0.1", "localhost", "::1")


def log(msg):
    line = "[Vulcan MCP] {}".format(msg)
    print(line)
    try:
        import maptek.vulcan_gui as vg

        if hasattr(vg, "print_message"):
            vg.print_message(line + "\n")
    except Exception:
        pass


def is_loopback(host):
    return str(host or "").strip().lower() in LOOPBACK_HOSTS


def _token_file_path():
    return os.path.join(os.path.expanduser("~"), ".vulcan_mcp", "token")


def _get_expected_token():
    if TOKEN:
        return TOKEN
    env_token = os.environ.get("VULCAN_MCP_TOKEN", "").strip()
    if env_token:
        return env_token
    token_path = _token_file_path()
    try:
        if os.path.isfile(token_path):
            with open(token_path, "r") as fh:
                return fh.read().strip()
    except Exception:
        pass
    return ""


def _listener_version():
    try:
        import __init__ as listener_pkg
        return getattr(listener_pkg, "__version__", "0.4.0")
    except Exception:
        return "0.4.0"


def validate_binding_security(host=None, token=None):
    target_host = HOST if host is None else host
    active_token = _get_expected_token() if token is None else str(token or "").strip()
    if not is_loopback(target_host) and not active_token:
        raise RuntimeError(
            "Refusing to bind to non-loopback address '{}' without VULCAN_MCP_TOKEN set.".format(
                target_host
            )
        )


def _check_auth(req):
    expected = _get_expected_token()
    if not expected:
        return True
    provided = str(req.get("token") or "")
    return hmac.compare_digest(provided.encode("utf-8"), expected.encode("utf-8"))


def dispatch(req):
    if not isinstance(req, dict):
        return {"status": "error", "message": "Invalid request envelope"}
    if not _check_auth(req):
        return {
            "status": "error",
            "message": "Authentication failed: invalid or missing VULCAN_MCP_TOKEN",
        }
    cmd = req.get("type")
    raw_params = req.get("params")
    if raw_params is not None and not isinstance(raw_params, dict):
        return {"status": "error", "message": "Invalid request params: expected dict"}
    params = raw_params or {}
    entry = COMMANDS.get(cmd)
    if entry is None:
        return {
            "status": "error",
            "message": "Unknown command '{}'. Registered: {}".format(
                cmd, ", ".join(sorted(COMMANDS))
            ),
        }
    fn, _ = entry
    try:
        result = fn(params)
        return {"status": "success", "result": result}
    except CommandError as exc:
        return {"status": "error", "message": str(exc)}
    except Exception as exc:
        return {
            "status": "error",
            "message": "{}: {}".format(type(exc).__name__, exc),
            "traceback": traceback.format_exc(),
        }


def handle_client(conn, read_timeout=None):
    try:
        try:
            conn.settimeout(CLIENT_READ_TIMEOUT if read_timeout is None else read_timeout)
        except Exception:
            pass
        while True:
            req = wire.read_message(conn)
            if isinstance(req, dict):
                cmd = req.get("type", "<unknown>")
                raw_params = req.get("params")
                act = raw_params.get("action") if isinstance(raw_params, dict) else None
                log("Command: {}{}".format(cmd, "." + str(act) if act else ""))
            else:
                log("Command: <invalid-envelope>")
            resp = dispatch(req)
            conn.sendall(wire.encode(resp))
    except (ConnectionError, socket.timeout):
        pass
    except Exception as exc:
        log("Client error: {}".format(exc))
    finally:
        try:
            conn.close()
        except Exception:
            pass


def serve_forever():
    validate_binding_security(HOST, _get_expected_token())
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((HOST, PORT))
    sock.listen(5)
    token_active = bool(_get_expected_token())
    log("=" * 62)
    log("Vulcan MCP Listener v{} started on {}:{}".format(_listener_version(), HOST, PORT))
    log("Working directory: {}".format(os.getcwd()))
    log("Registered domains: {}".format(", ".join(sorted(COMMANDS))))
    if token_active:
        log("Token authentication: ENABLED (HMAC protected)")
    else:
        log("Token authentication: DISABLED (localhost open mode)")
        log("Security Notice: Token is OPTIONAL on localhost, but RECOMMENDED")
        log("                 as a security wall against unintended script execution.")
    log("Keep this window open while using your AI client. Ctrl+C to stop.")
    log("=" * 62)
    try:
        while True:
            try:
                conn, _ = sock.accept()
            except OSError as exc:
                log("Accept error (continuing): {}".format(exc))
                continue
            # Handle synchronously on the main thread so OpenGL / GUI calls are safe
            handle_client(conn)
    except KeyboardInterrupt:
        log("Stopping server...")
    finally:
        sock.close()


if __name__ == "__main__":
    serve_forever()
