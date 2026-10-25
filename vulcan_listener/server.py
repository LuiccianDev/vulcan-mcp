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
ROOT_DIR = os.path.dirname(HERE)
ENV_FILE = os.path.join(ROOT_DIR, ".env")
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


def _get_config(key, default=""):
    val = os.getenv(key, "").strip()
    if val:
        return val
    if os.path.isfile(ENV_FILE):
        try:
            with open(ENV_FILE, "r") as fh:
                for raw in fh:
                    line = raw.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    k, v = line.split("=", 1)
                    if k.strip() == key:
                        return v.strip().strip('"').strip("'")
        except Exception:
            pass
    return default


HOST = _get_config("VULCAN_MCP_HOST", "127.0.0.1") or "127.0.0.1"
PORT = int(_get_config("VULCAN_MCP_PORT", "9877") or "9877")
TOKEN = None


def log(msg):
    line = "[Vulcan MCP] {}".format(msg)
    print(line)
    try:
        import maptek.vulcan_gui as vg
        if hasattr(vg, "print_message"):
            vg.print_message(line + "\n")
    except Exception:
        pass


def _check_auth(req):
    expected = _get_config("VULCAN_MCP_TOKEN", "") if TOKEN is None else TOKEN
    if not expected:
        return True
    provided = str(req.get("token") or "")
    return hmac.compare_digest(provided.encode("utf-8"), expected.encode("utf-8"))


def dispatch(req):
    if not isinstance(req, dict):
        return {"status": "error", "message": "Invalid request envelope"}
    if not _check_auth(req):
        return {"status": "error", "message": "Authentication failed: invalid or missing VULCAN_MCP_TOKEN"}
    cmd = req.get("type")
    params = req.get("params") or {}
    entry = COMMANDS.get(cmd)
    if entry is None:
        return {"status": "error", "message": "Unknown command '{}'. Registered: {}".format(
            cmd, ", ".join(sorted(COMMANDS)))}
    fn, _ = entry
    try:
        result = fn(params)
        return {"status": "success", "result": result}
    except CommandError as exc:
        return {"status": "error", "message": str(exc)}
    except Exception as exc:
        return {"status": "error", "message": "{}: {}".format(type(exc).__name__, exc),
                "traceback": traceback.format_exc()}


def handle_client(conn):
    try:
        while True:
            req = wire.read_message(conn)
            cmd = req.get("type", "<unknown>")
            act = (req.get("params") or {}).get("action")
            log("Command: {}{}".format(cmd, "." + act if act else ""))
            resp = dispatch(req)
            conn.sendall(wire.encode(resp))
    except ConnectionError:
        pass
    except Exception as exc:
        log("Client error: {}".format(exc))
    finally:
        try:
            conn.close()
        except Exception:
            pass


def serve_forever():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((HOST, PORT))
    sock.listen(5)
    token_active = bool(_get_config("VULCAN_MCP_TOKEN", ""))
    log("=" * 62)
    log("Vulcan MCP Listener started on {}:{}".format(HOST, PORT))
    log("Working directory: {}".format(os.getcwd()))
    log("Registered domains: {}".format(", ".join(sorted(COMMANDS))))
    log("Token auth: {}".format("ENABLED (os.getenv / .env)" if token_active else "DISABLED (local open mode)"))
    log("Keep this window open while using your AI client. Ctrl+C to stop.")
    log("=" * 62)
    try:
        while True:
            conn, _ = sock.accept()
            # Handle synchronously on the main thread so OpenGL / GUI calls are safe
            handle_client(conn)
    except KeyboardInterrupt:
        log("Stopping server...")
    finally:
        sock.close()


if __name__ == "__main__":
    serve_forever()
