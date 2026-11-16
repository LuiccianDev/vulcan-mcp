"""Unit tests for models, resilience client, and protocol edge cases."""

import pytest

from vulcan_mcp.client import (
    VulcanCommandError,
    VulcanConnectionError,
    VulcanMCPClient,
)
from vulcan_mcp.models.responses import (
    BlockModelStatsResponse,
    CanvasResponse,
    DesignCadResponse,
    DrillholeAuditResponse,
    ExecuteCodeResponse,
    LegendResponse,
    TriangulationResponse,
    VulcanBaseResponse,
    VulcanInventoryResponse,
    VulcanPingResponse,
)
from vulcan_mcp.protocol import (
    MAX_MESSAGE_SIZE,
    pack_message,
    unpack_message,
)


def test_all_models_instantiation():
    """Verify that all response models instantiate and serialize cleanly."""
    base = VulcanBaseResponse(status="ok")
    assert base.status == "ok"
    assert base.error is None

    ping = VulcanPingResponse(message="pong", protocol_version=1)
    assert ping.message == "pong"
    assert ping.protocol_version == 1

    inv = VulcanInventoryResponse(project="Pit1", block_models=["ore.bmf"])
    assert inv.project == "Pit1"
    assert "ore.bmf" in inv.block_models

    bm = BlockModelStatsResponse(model_name="mine.bmf", variables=[{"name": "CU"}])
    assert bm.model_name == "mine.bmf"

    tri = TriangulationResponse(triangulation="topo.00t", triangles=150, volume=1000.5)
    assert tri.triangles == 150
    assert tri.volume == 1000.5

    dh = DrillholeAuditResponse(database="gold.dhd.isis", hole_count=42)
    assert dh.hole_count == 42

    cad = DesignCadResponse(database="mine.dgd.isis", layers=["TOPO", "PIT"])
    assert len(cad.layers or []) == 2

    leg = LegendResponse(legend_file="cu_grade.scd", intervals=[{"min": 0.1, "max": 0.5}])
    assert len(leg.intervals or []) == 1

    canvas = CanvasResponse(screenshot_path="shot.png", width=1920, height=1080)
    assert canvas.width == 1920

    code = ExecuteCodeResponse(stdout="hello", result=123)
    assert code.stdout == "hello"
    assert code.result == 123


def test_protocol_oversized_payload_raises():
    """Verify that payloads exceeding MAX_MESSAGE_SIZE raise ValueError."""
    with pytest.raises(ValueError, match="Payload exceeds maximum allowed size"):
        huge_str = "x" * (MAX_MESSAGE_SIZE + 10)
        pack_message({"data": huge_str})


def test_protocol_unpack_oversized_raises():
    """Verify that socket streams reporting oversized length raise ValueError."""

    class FakeSock:
        def __init__(self, raw: bytes):
            self._raw = bytearray(raw)

        def recv(self, n: int) -> bytes:
            chunk = bytes(self._raw[:n])
            del self._raw[:n]
            return chunk

    import struct

    fake_header = struct.pack("!I", MAX_MESSAGE_SIZE + 500)
    sock = FakeSock(fake_header)
    with pytest.raises(ValueError, match="Incoming response exceeds maximum allowed size"):
        unpack_message(sock)


def test_client_connection_error_on_unreachable_port():
    """Verify VulcanMCPClient raises VulcanConnectionError when port is closed."""
    client = VulcanMCPClient(host="127.0.0.1", port=59999, max_retries=0)
    with pytest.raises(VulcanConnectionError, match="Cannot connect to Maptek Vulcan"):
        client.send_command("system", {"action": "ping"})


def test_client_handles_error_status():
    """Verify VulcanMCPClient raises VulcanCommandError on server error status."""

    class MockErrorSocket:
        def setsockopt(self, *args):
            pass

        def settimeout(self, *args):
            pass

        def connect(self, addr):
            pass

        def sendall(self, data):
            pass

        def recv(self, n):
            import json
            import struct

            payload = json.dumps({"status": "error", "message": "Simulated Vulcan Failure"}).encode(
                "utf-8"
            )
            if not hasattr(self, "_sent_header"):
                self._sent_header = True
                return struct.pack("!I", len(payload))
            return payload

        def close(self):
            pass

    import unittest.mock

    client = VulcanMCPClient()
    with unittest.mock.patch("socket.socket", return_value=MockErrorSocket()):
        with pytest.raises(VulcanCommandError, match="Simulated Vulcan Failure"):
            client.send_command("test")
