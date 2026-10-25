"""Mock Maptek Vulcan 12 listener server for offline testing and evaluation.

Implements the uint32 big-endian wire protocol used by Vulcan MCP and plugin/server.py.
Allows offline testing of FastMCP tools and agent workflows without Maptek Vulcan Desktop.
"""

from __future__ import annotations

import json
import socket
import struct
import threading
from typing import Any, Callable

HEADER_STRUCT = struct.Struct("!I")


def pack_wire_message(payload_dict: dict[str, Any]) -> bytes:
    payload_bytes = json.dumps(payload_dict, ensure_ascii=False).encode("utf-8")
    return HEADER_STRUCT.pack(len(payload_bytes)) + payload_bytes


def unpack_wire_message(sock: socket.socket) -> dict[str, Any]:
    raw_len = _recv_exact(sock, HEADER_STRUCT.size)
    (length,) = HEADER_STRUCT.unpack(raw_len)
    payload_bytes = _recv_exact(sock, length)
    return json.loads(payload_bytes.decode("utf-8"))


def _recv_exact(sock: socket.socket, n: int) -> bytes:
    buf = bytearray()
    while len(buf) < n:
        chunk = sock.recv(min(n - len(buf), 65536))
        if not chunk:
            raise ConnectionError("Socket connection closed prematurely")
        buf.extend(chunk)
    return bytes(buf)


class MockVulcanServer:
    """Threaded TCP Socket Server emulating a Maptek Vulcan 12 Desktop session."""

    def __init__(self, host: str = "127.0.0.1", port: int = 0, token: str | None = None):
        self.host = host
        self.requested_port = port
        self.port = port
        self.token = token
        self._server_socket: socket.socket | None = None
        self._thread: threading.Thread | None = None
        self._running = False
        self._handlers: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {}
        self.received_requests: list[dict[str, Any]] = []
        self._lock = threading.Lock()

        self._setup_default_responses()

    def _setup_default_responses(self) -> None:
        """Register realistic default mining responses for all Vulcan MCP domains."""
        self._handlers["system"] = self._default_system
        self._handlers["block_model"] = self._default_block_model
        self._handlers["triangulation"] = self._default_triangulation
        self._handlers["design"] = self._default_design
        self._handlers["drillholes"] = self._default_drillholes
        self._handlers["legend"] = self._default_legend
        self._handlers["canvas"] = self._default_canvas
        self._handlers["screenshot"] = self._default_screenshot
        self._handlers["execute_code"] = self._default_execute_code

    def _default_system(self, params: dict[str, Any]) -> dict[str, Any]:
        action = params.get("action", "project_info")
        if action == "ping":
            return {
                "connected": True,
                "app": "Maptek Vulcan 12.0.4 (Mock Harness)",
                "python": "3.5.2",
                "vulcan_api": True,
                "project_dir": "C:/Projects/Copper_Porphyry_Deposit",
            }
        elif action == "capabilities":
            return {
                "connected": True,
                "maptek.vulcan": True,
                "maptek.vulcan_gui": True,
                "mapteksdk": True,
                "win32gui": True,
                "PIL": True,
                "numpy": True,
            }
        else:
            return {
                "connected": True,
                "project_dir": "C:/Projects/Copper_Porphyry_Deposit",
                "inventory": {
                    "block_models": {"count": 1, "files": ["deposit_block_model.bmf"]},
                    "triangulations": {
                        "count": 2,
                        "files": ["topo_surface.00t", "orebody_solid.00t"],
                    },
                    "design_databases": {"count": 1, "files": ["pit_design.dgd.isis"]},
                    "drillhole_databases": {"count": 1, "files": ["exploration.dhd.isis"]},
                    "legends": {"count": 1, "files": ["copper_grades.scd"]},
                    "specifications": {"count": 0, "files": []},
                },
            }

    def _default_block_model(self, params: dict[str, Any]) -> dict[str, Any]:
        action = params.get("action", "list")
        if action == "list":
            return {"models": ["deposit_block_model.bmf"]}
        elif action == "info":
            return {
                "model": params.get("model", "deposit_block_model.bmf"),
                "dimensions": {"nx": 120, "ny": 100, "nz": 40},
                "origin": {"x": 474000.0, "y": 4479000.0, "z": 500.0},
                "variables": [
                    {"name": "CU", "type": "float", "default": -99.0},
                    {"name": "AU", "type": "float", "default": -99.0},
                    {"name": "DENSITY", "type": "float", "default": 2.7},
                ],
            }
        elif action == "query_xyz":
            return {
                "x": params.get("x", 474500.0),
                "y": params.get("y", 4479500.0),
                "z": params.get("z", 650.0),
                "values": {"CU": 1.25, "AU": 0.45, "DENSITY": 2.68},
            }
        elif action == "stats":
            return {
                "variable": params.get("variable", "CU"),
                "mean": 0.78,
                "min": 0.01,
                "max": 3.85,
                "std_dev": 0.42,
                "total_blocks": 480000,
                "blocks_above_cutoff": 125400,
            }
        return {"status": "ok"}

    def _default_triangulation(self, params: dict[str, Any]) -> dict[str, Any]:
        action = params.get("action", "list")
        if action == "list":
            return {"triangulations": ["topo_surface.00t", "orebody_solid.00t"]}
        elif action == "info":
            return {
                "triangulation": params.get("triangulation", "orebody_solid.00t"),
                "triangle_count": 8420,
                "is_solid": True,
                "extents": {
                    "min_x": 474100.0,
                    "max_x": 474900.0,
                    "min_y": 4479100.0,
                    "max_y": 4479800.0,
                    "min_z": 550.0,
                    "max_z": 750.0,
                },
            }
        elif action == "calculate_volume":
            return {
                "triangulation": params.get("triangulation", "orebody_solid.00t"),
                "volume": 2450000.0,
                "surface_area": 125000.0,
            }
        elif action == "load":
            return {
                "triangulation": params.get("triangulation", "orebody_solid.00t"),
                "loaded": True,
            }
        return {"status": "ok"}

    def _default_design(self, params: dict[str, Any]) -> dict[str, Any]:
        action = params.get("action", "list_layers")
        if action == "list_layers":
            return {"layers": ["pit_crest", "toe_lines", "faults_layer"]}
        elif action == "get_layer":
            return {
                "layer": params.get("layer", "pit_crest"),
                "objects_count": 3,
                "polylines": [
                    {
                        "id": 1,
                        "point_count": 4,
                        "closed": True,
                        "points": [
                            [474200.0, 4479200.0, 700.0],
                            [474800.0, 4479200.0, 700.0],
                            [474800.0, 4479700.0, 700.0],
                            [474200.0, 4479200.0, 700.0],
                        ],
                    }
                ],
            }
        elif action == "create_polyline":
            pts = params.get("points", [])
            return {
                "layer": params.get("layer", "new_polylines"),
                "points_saved": len(pts),
                "closed": params.get("closed", False),
            }
        return {"status": "ok"}

    def _default_drillholes(self, params: dict[str, Any]) -> dict[str, Any]:
        action = params.get("action", "list_dbs")
        if action == "list_dbs":
            return {"drillhole_dbs": ["exploration.dhd.isis"]}
        elif action == "holes":
            return {"holes": ["DH001", "DH002", "DH003"], "total": 3, "offset": 0, "limit": 100}
        elif action == "schema":
            return {
                "db": params.get("db", "exploration.dhd.isis"),
                "tables": {
                    "COLLARES": ["HOLE_ID", "X", "Y", "Z", "PROFUNDIDAD"],
                    "DIRECCIONES": ["HOLE_ID", "AT", "BRG", "DIP"],
                    "LEYES": ["HOLE_ID", "FROM", "TO", "CU", "AU"],
                },
                "string_fields": {"COLLARES": ["HOLE_ID"], "LEYES": ["HOLE_ID"]},
                "holes": 3,
            }
        elif action == "hole":
            return {
                "hole": params.get("hole", "DH001"),
                "collar": {
                    "HOLE_ID": params.get("hole", "DH001"),
                    "X": 474300.0,
                    "Y": 4479500.0,
                    "Z": 700.0,
                    "PROFUNDIDAD": 250.0,
                },
                "surveys": [{"AT": 0.0, "BRG": 0.0, "DIP": -90.0}],
                "assays": [
                    {"FROM": 0.0, "TO": 25.0, "CU": 0.25},
                    {"FROM": 25.0, "TO": 55.0, "CU": 1.48},
                ],
            }
        elif action == "high_grade":
            return {
                "high_grade_intervals": [
                    {"hole": "DH001", "from": 25.0, "to": 55.0, "field": "CU", "value": 1.48}
                ],
                "count": 1,
            }
        elif action == "display":
            return {
                "displayed_holes": 1,
                "segments_created": 2,
                "mode": params.get("mode", "isis"),
            }
        elif action == "clear_display":
            return {"cleared": True}
        return {"status": "ok"}

    def _default_legend(self, params: dict[str, Any]) -> dict[str, Any]:
        action = params.get("action", "inspect")
        if action == "inspect":
            return {
                "scd": params.get("scd", "copper_grades.scd"),
                "schemes": {
                    "DRILL_COLOUR": {
                        "tables": ["COBRE"],
                        "COBRE": [
                            {"lower": 0.0, "upper": 0.5, "colour": 144},
                            {"lower": 0.5, "upper": 2.0, "colour": 33},
                        ],
                    }
                },
            }
        elif action == "update":
            return {
                "scd": params.get("scd", "copper_grades.scd"),
                "scheme": params.get("scheme", "DRILL_COLOUR"),
                "table": params.get("table", "COBRE"),
                "intervals_updated": len(params.get("colours", [])),
            }
        return {"status": "ok"}

    def _default_canvas(self, params: dict[str, Any]) -> dict[str, Any]:
        action = params.get("action", "clear_all")
        if action == "screenshot":
            return {
                "data": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
                "mime_type": "image/jpeg",
                "width": 800,
                "height": 600,
            }
        return {"action": action, "success": True}

    def _default_screenshot(self, params: dict[str, Any]) -> dict[str, Any]:
        # 1x1 transparent PNG in base64
        base64_1x1_png = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        return {
            "image_base64": base64_1x1_png,
            "format": "png",
            "width": 1280,
            "height": 720,
        }

    def _default_execute_code(self, params: dict[str, Any]) -> dict[str, Any]:
        code = params.get("code", "")
        return {
            "executed": True,
            "result": {"evaluated": True},
            "stdout": "Mock Vulcan script finished successfully.\n",
            "code_length": len(code),
        }

    def register_handler(
        self,
        command_type: str,
        handler: Callable[[dict[str, Any]], dict[str, Any]],
    ) -> None:
        """Register a custom handler function for a command type."""
        with self._lock:
            self._handlers[command_type] = handler

    def start(self) -> MockVulcanServer:
        """Start the mock server on a background thread."""
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server_socket.bind((self.host, self.requested_port))
        self.port = self._server_socket.getsockname()[1]
        self._server_socket.listen(5)
        self._server_socket.settimeout(0.2)
        self._running = True

        self._thread = threading.Thread(target=self._serve_loop, daemon=True)
        self._thread.start()
        return self

    def _serve_loop(self) -> None:
        while self._running:
            try:
                conn, _ = self._server_socket.accept()
            except socket.timeout:
                continue
            except OSError:
                break

            conn.settimeout(3.0)
            try:
                msg = unpack_wire_message(conn)
                with self._lock:
                    self.received_requests.append(msg)

                # Validate token if configured
                token_received = msg.get("token")
                if self.token and token_received != self.token:
                    err_resp = {"status": "error", "message": "Authentication failed"}
                    conn.sendall(pack_wire_message(err_resp))
                    conn.close()
                    continue

                cmd_type = msg.get("type", "")
                params = msg.get("params", {})
                with self._lock:
                    handler = self._handlers.get(cmd_type)

                if handler is None:
                    resp = {"status": "error", "message": f"Unknown command type: {cmd_type}"}
                else:
                    try:
                        res_data = handler(params)
                        if (
                            isinstance(res_data, dict)
                            and "status" in res_data
                            and res_data["status"] == "error"
                        ):
                            resp = res_data
                        else:
                            resp = {"status": "success", "result": res_data}
                    except Exception as exc:
                        resp = {"status": "error", "message": str(exc)}

                conn.sendall(pack_wire_message(resp))
            except Exception:
                pass
            finally:
                conn.close()

    def stop(self) -> None:
        """Stop the mock server gracefully."""
        self._running = False
        if self._server_socket:
            try:
                self._server_socket.close()
            except Exception:
                pass
        if self._thread:
            self._thread.join(timeout=1.0)

    def __enter__(self) -> MockVulcanServer:
        return self.start()

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.stop()
