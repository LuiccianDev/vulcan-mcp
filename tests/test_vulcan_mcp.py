"""Automated unit and structural tests for vulcan-mcp."""

import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "vulcan_listener"))

import pytest  # noqa: E402
import server as listener_server  # noqa: E402
from handlers.common import COMMANDS  # noqa: E402


@pytest.fixture(autouse=True)
def _isolate_unit_test_token(monkeypatch):
    """Isolate unit tests from any VULCAN_MCP_TOKEN in os.environ unless explicitly tested."""
    monkeypatch.delenv("VULCAN_MCP_TOKEN", raising=False)


def test_python35_compatibility_no_fstrings():
    """Ensure no f-strings (JoinedStr, added in Python 3.6) exist in vulcan_listener/."""
    vulcan_listener_dir = ROOT / "vulcan_listener"
    for py_file in vulcan_listener_dir.rglob("*.py"):
        source = py_file.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(py_file))
        for node in ast.walk(tree):
            assert not isinstance(node, ast.JoinedStr), (
                f"Python 3.6+ f-string found in {py_file}:{getattr(node, 'lineno', '?')} "
                "(Vulcan 12 uses Python 3.5.2)"
            )


def test_all_domains_registered():
    expected = {
        "system",
        "block_model",
        "triangulation",
        "design",
        "drillholes",
        "legend",
        "canvas",
        "execute_code",
    }
    assert set(COMMANDS.keys()) == expected


def test_system_ping_and_capabilities():
    res = listener_server.dispatch({"type": "system", "params": {"action": "ping"}})
    assert res["status"] == "success"
    assert res["result"]["connected"] is True

    caps = listener_server.dispatch({"type": "system", "params": {"action": "capabilities"}})
    assert caps["status"] == "success"
    assert "maptek.vulcan" in caps["result"]


def test_token_authentication(monkeypatch):
    monkeypatch.setenv("VULCAN_MCP_TOKEN", "secret-mining-token")
    bad = listener_server.dispatch({"type": "system", "params": {"action": "ping"}})
    assert bad["status"] == "error"
    assert "Authentication failed" in bad["message"]

    good = listener_server.dispatch(
        {"type": "system", "params": {"action": "ping"}, "token": "secret-mining-token"}
    )
    assert good["status"] == "success"


def test_non_loopback_requires_token_and_env_token(monkeypatch):
    from vulcan_mcp import protocol

    # 1. Loopback (127.0.0.1 / localhost) is allowed without token by default
    assert listener_server.is_loopback("127.0.0.1") is True
    assert listener_server.is_loopback("localhost") is True
    assert listener_server.is_loopback("0.0.0.0") is False
    listener_server.validate_binding_security("127.0.0.1", "")

    # 2. Non-loopback (0.0.0.0) without VULCAN_MCP_TOKEN must refuse to start
    with pytest.raises(RuntimeError, match="Refusing to bind to non-loopback address"):
        listener_server.validate_binding_security("0.0.0.0", "")

    # 3. Setting VULCAN_MCP_TOKEN in environment enables auth & permits non-loopback binding
    monkeypatch.setenv("VULCAN_MCP_TOKEN", "env-random-secret-999")
    assert protocol.get_auth_token() == "env-random-secret-999"
    listener_server.validate_binding_security("0.0.0.0", protocol.get_auth_token())

    rejected = listener_server.dispatch({"type": "system", "params": {"action": "ping"}})
    assert rejected["status"] == "error"
    accepted = listener_server.dispatch(
        {"type": "system", "params": {"action": "ping"}, "token": protocol.get_auth_token()}
    )
    assert accepted["status"] == "success"


def test_legend_parse_and_update(tmp_path, monkeypatch):
    scd = tmp_path / "test.scd"
    scd.write_text(
        "BEGIN$DEF DRILL_COLOUR\n"
        " BEGIN$TAB COBRE\n"
        "   'CUT'\n"
        "   '#LEYES'\n"
        "   'FROM'\n"
        "   'TO'\n"
        "   ''\n"
        "   '144'\n"
        "   '0.0'\n"
        "   '0.5'\n"
        "   '33'\n"
        "   '0.5'\n"
        "   '2.0'\n"
        "   'GELT'\n"
        " END$TAB COBRE\n"
        "END$DEF DRILL_COLOUR\n",
        encoding="latin1",
    )
    monkeypatch.chdir(tmp_path)

    inspected = listener_server.dispatch(
        {"type": "legend", "params": {"action": "inspect", "scd": "test.scd"}}
    )
    assert inspected["status"] == "success"
    assert "COBRE" in inspected["result"]["schemes"]["DRILL_COLOUR"]

    updated = listener_server.dispatch(
        {
            "type": "legend",
            "params": {
                "action": "update",
                "scd": "test.scd",
                "scheme": "DRILL_COLOUR",
                "table": "COBRE",
                "colours": ["10", "1"],
            },
        }
    )
    assert updated["status"] == "success"
    assert updated["result"]["intervals_updated"] == 2
    assert "'10'" in scd.read_text(encoding="latin1")
    assert (tmp_path / "test.scd.bak").exists()


def test_execute_code_handler():
    res = listener_server.dispatch(
        {
            "type": "execute_code",
            "params": {"code": "x = 21 * 2\nprint('hello')\nresult = {'answer': x}"},
        }
    )
    assert res["status"] == "success"
    assert res["result"]["executed"] is True
    assert res["result"]["result"] == {"answer": 42}
    assert "hello" in res["result"]["stdout"]


def test_drillhole_string_fields_never_call_get_double():
    """Verify _field_cache and _record never invoke db.get() on string fields like HOLE_ID."""
    from handlers import drillholes

    class FakeIsisDB:
        def __init__(self):
            self.get_double_calls = []

        def field_list(self, table):
            return ["HOLE_ID", "FROM", "TO", "CUT"]

        def field_list_strings(self, table):
            return ["HOLE_ID"]

        def get(self, field):
            self.get_double_calls.append(field)
            if field == "HOLE_ID":
                raise AssertionError("GetDoubleField called on string field HOLE_ID!")
            return {"FROM": 10.0, "TO": 12.0, "CUT": 1.45}[field]

        def get_string(self, field):
            return "SK08"

    fake_db = FakeIsisDB()
    fields_of = drillholes._field_cache(fake_db)
    f_all, f_str = fields_of("LEYES")
    assert "HOLE_ID" in f_str
    rec = drillholes._record(fake_db, f_all, f_str)
    assert rec == {"HOLE_ID": "SK08", "FROM": 10.0, "TO": 12.0, "CUT": 1.45}
    assert "HOLE_ID" not in fake_db.get_double_calls


def test_drillhole_desurvey_and_colour():
    from handlers import drillholes

    pt = drillholes._desurvey_point([474300.0, 4479500.0, 700.0], [(0.0, 0.0, -90.0)], 50.0)
    assert pt[0] == 474300.0
    assert pt[1] == 4479500.0
    assert abs(pt[2] - 650.0) < 1e-6
    assert drillholes._grade_to_vulcan_colour(1.5) == 1
    assert drillholes._grade_to_vulcan_colour(0.1) == 5


def test_vulcan_mcp_client_dynamic_configuration(monkeypatch):
    """Test VulcanMCPClient constructor ergonomics and environment variable fallback."""
    from vulcan_mcp.client import VulcanMCPClient
    from vulcan_mcp.protocol import DEFAULT_HOST, DEFAULT_PORT

    # 1. Default initialization
    client = VulcanMCPClient()
    assert client.host == DEFAULT_HOST
    assert client.port == DEFAULT_PORT
    assert client.token is None
    assert client.default_timeout == 30.0

    # 2. Explicit constructor parameters matching AutoCAD MCP
    custom = VulcanMCPClient(
        host="192.168.1.10",
        port="9878",
        token="custom-token-xyz",
        timeout=45.0,
    )
    assert custom.host == "192.168.1.10"
    assert custom.port == 9878
    assert custom.token == "custom-token-xyz"
    assert custom.default_timeout == 45.0

    # 3. Dynamic fallback to environment variables
    monkeypatch.setenv("VULCAN_MCP_HOST", "127.0.0.2")
    monkeypatch.setenv("VULCAN_MCP_PORT", "9999")
    monkeypatch.setenv("VULCAN_MCP_TOKEN", "env-secret-token")
    env_client = VulcanMCPClient()
    assert env_client.host == "127.0.0.2"
    assert env_client.port == 9999
    assert env_client.token == "env-secret-token"


def test_version_synchronization():
    """Ensure pyproject.toml and vulcan_mcp.__version__ stay synchronized."""
    import tomllib

    import vulcan_mcp

    pyproject_path = ROOT / "pyproject.toml"
    with open(pyproject_path, "rb") as f:
        pyproject_data = tomllib.load(f)
    pyproject_version = pyproject_data["project"]["version"]

    pkg_version = vulcan_mcp.__version__

    assert pkg_version == pyproject_version
    assert pkg_version == "0.5.1"


def test_drillhole_qaqc_validation(monkeypatch):
    """Verify drillholes qaqc_validation end-to-end contract, bilingual fields, limits, and errors."""
    import pytest
    from handlers import common, drillholes

    from vulcan_mcp.models import DrillholeQAQCResponse

    class FakeQaqcDB:
        def __init__(self, rows, fields=None, string_fields=None, tables=None):
            self._rows = rows
            self._idx = -1
            self._fields = fields or ["HOLE_ID", "DESDE", "HASTA", "CUT"]
            self._str_fields = string_fields or ["HOLE_ID"]
            self._tables = tables or ["COLLARES", "LEYES"]

        def table_list(self):
            return self._tables

        def field_list(self, table):
            return self._fields

        def field_list_strings(self, table):
            return self._str_fields

        def __iter__(self):
            for i in range(len(self._rows)):
                self._idx = i
                yield self

        def get_table_name(self):
            return self._rows[self._idx]["_table"]

        def get_key(self):
            return self._rows[self._idx]["HOLE_ID"]

        def get(self, field):
            return self._rows[self._idx][field]

        def close(self):
            pass

    rows = [
        {"_table": "COLLARES", "HOLE_ID": "DH001"},
        {"_table": "LEYES", "HOLE_ID": "DH001", "DESDE": 0.0, "HASTA": 2.0, "CUT": 0.5},
        {"_table": "LEYES", "HOLE_ID": "DH001", "DESDE": 1.5, "HASTA": 4.0, "CUT": -0.2},
        {"_table": "LEYES", "HOLE_ID": "DH001", "DESDE": 6.0, "HASTA": 5.0, "CUT": 12.0},
    ]
    fake_db = FakeQaqcDB(rows)
    monkeypatch.setattr(drillholes, "_open", lambda params: fake_db)

    res = drillholes.drillholes(
        {
            "action": "qaqc_validation",
            "db": "test.dhd.isis",
            "field": "CUT",
            "min_valid": 0.0,
            "max_valid": 10.0,
            "limit": 3,
        }
    )
    assert res["table"] == "LEYES"
    assert res["holes_checked"] == 1
    assert res["intervals_checked"] == 3
    assert res["total_anomalies"] == 5
    assert len(res["anomalies"]) == 3
    assert res["summary"] == {
        "overlap": 1,
        "gap": 1,
        "inverted_interval": 1,
        "out_of_range": 2,
    }

    parsed = DrillholeQAQCResponse(status="success", **res)
    assert parsed.total_anomalies == 5
    assert parsed.anomalies[0].hole == "DH001"

    with pytest.raises(common.CommandError, match="string field"):
        drillholes.drillholes(
            {
                "action": "qaqc_validation",
                "db": "test.dhd.isis",
                "table": "LEYES",
                "field": "HOLE_ID",
            }
        )

    with pytest.raises(common.CommandError, match="not found"):
        drillholes.drillholes(
            {
                "action": "qaqc_validation",
                "db": "test.dhd.isis",
                "table": "MISSING_TABLE",
            }
        )


def test_listener_and_client_connection_resilience(monkeypatch):
    """Verify listener handles malformed envelopes, idle/partial timeouts, accept errors, and client retries."""
    import socket
    import threading

    import server as listener_server
    import wire

    from vulcan_mcp.client import VulcanMCPClient

    # 1. Malformed non-dict envelope & non-dict params return clean error envelopes
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.bind(("127.0.0.1", 0))
    srv.listen(4)
    port = srv.getsockname()[1]

    def _serve_two():
        for _ in range(2):
            conn, _ = srv.accept()
            listener_server.handle_client(conn, read_timeout=1.0)

    t = threading.Thread(target=_serve_two, daemon=True)
    t.start()

    for payload, expected_msg in (
        ([1, 2, 3], "Invalid request envelope"),
        ({"type": "system", "params": "bad"}, "Invalid request params"),
    ):
        c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        c.connect(("127.0.0.1", port))
        c.sendall(wire.encode(payload))
        resp = wire.read_message(c)
        assert resp["status"] == "error"
        assert expected_msg in resp["message"]
        c.close()
    t.join(timeout=2.0)
    srv.close()

    # 2. Idle/stalled client times out cleanly without blocking next client
    srv2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv2.bind(("127.0.0.1", 0))
    srv2.listen(4)
    port2 = srv2.getsockname()[1]

    def _serve_idle_then_valid():
        conn1, _ = srv2.accept()
        listener_server.handle_client(conn1, read_timeout=0.15)
        conn2, _ = srv2.accept()
        listener_server.handle_client(conn2, read_timeout=1.0)

    t2 = threading.Thread(target=_serve_idle_then_valid, daemon=True)
    t2.start()

    idle = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    idle.connect(("127.0.0.1", port2))
    idle.sendall(wire.HEADER.pack(50) + b"part")

    client = VulcanMCPClient(host="127.0.0.1", port=port2, timeout=2.0, max_retries=0)
    ping_res = client.send_command("system", {"action": "ping"})
    assert ping_res["connected"] is True
    idle.close()
    t2.join(timeout=2.0)
    srv2.close()

    # 3. VulcanMCPClient retries on immediate post-connect close
    srv3 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv3.bind(("127.0.0.1", 0))
    srv3.listen(4)
    port3 = srv3.getsockname()[1]

    def _drop_then_ok():
        c1, _ = srv3.accept()
        c1.close()
        c2, _ = srv3.accept()
        listener_server.handle_client(c2, read_timeout=1.0)

    t3 = threading.Thread(target=_drop_then_ok, daemon=True)
    t3.start()
    retry_client = VulcanMCPClient(
        host="127.0.0.1", port=port3, timeout=2.0, max_retries=2, retry_delay=0.05
    )
    assert retry_client.send_command("system", {"action": "ping"})["connected"] is True
    t3.join(timeout=2.0)
    srv3.close()

    # 4. serve_forever survives transient ConnectionAbortedError on accept()
    calls = {"n": 0}

    class FakeListenSock:
        def setsockopt(self, *args):
            pass

        def bind(self, *args):
            pass

        def listen(self, *args):
            pass

        def accept(self):
            calls["n"] += 1
            if calls["n"] == 1:
                raise ConnectionAbortedError("transient abort")
            raise KeyboardInterrupt()

        def close(self):
            pass

    monkeypatch.setattr(listener_server.socket, "socket", lambda *a, **kw: FakeListenSock())
    listener_server.serve_forever()
    assert calls["n"] == 2


def test_cli_flags_and_auth_token(tmp_path, monkeypatch, capsys):
    """Verify --version, --help, --generate-token, shared token parity, and --check health check."""
    import json
    import socket
    import threading

    import pytest
    import server as listener_server

    from vulcan_mcp import __version__, protocol
    from vulcan_mcp.cli import main as mcp_main

    # Isolate home and env so ~/.vulcan_mcp/token is created inside tmp_path
    monkeypatch.delenv("VULCAN_MCP_TOKEN", raising=False)
    monkeypatch.setattr(protocol.Path, "home", staticmethod(lambda: tmp_path))
    monkeypatch.setattr(
        listener_server,
        "_token_file_path",
        lambda: str(tmp_path / ".vulcan_mcp" / "token"),
    )

    assert mcp_main(["--version"]) == 0
    assert __version__ in capsys.readouterr().out

    with pytest.raises(SystemExit) as exc_info:
        mcp_main(["--help"])
    assert exc_info.value.code == 0
    help_out = capsys.readouterr().out
    assert "--check" in help_out
    assert "--generate-token" in help_out

    assert mcp_main(["--generate-token"]) == 0
    gen_out = capsys.readouterr().out
    assert "VULCAN_MCP_TOKEN" in gen_out

    mcp_token = protocol.get_auth_token()
    listener_token = listener_server._get_expected_token()
    assert mcp_token is not None
    assert mcp_token == listener_token

    # Environment variable overrides token file when set explicitly
    monkeypatch.setenv("VULCAN_MCP_TOKEN", "env-override-token")
    assert protocol.get_auth_token() == "env-override-token"
    assert listener_server._get_expected_token() == "env-override-token"
    monkeypatch.delenv("VULCAN_MCP_TOKEN")

    # --check succeeds against live local socket using the shared token
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.bind(("127.0.0.1", 0))
    srv.listen(2)
    port = srv.getsockname()[1]

    def _serve_one():
        conn, _ = srv.accept()
        listener_server.handle_client(conn, read_timeout=2.0)

    t = threading.Thread(target=_serve_one, daemon=True)
    t.start()

    monkeypatch.setenv("VULCAN_MCP_HOST", "127.0.0.1")
    monkeypatch.setenv("VULCAN_MCP_PORT", str(port))
    capsys.readouterr()
    assert mcp_main(["--check"]) == 0
    raw_out = capsys.readouterr().out
    check_payload = json.loads(raw_out[raw_out.index("{") :])
    assert check_payload["ok"] is True
    assert check_payload["token_configured"] is True
    from handlers.common import get_listener_meta

    assert check_payload["listener_version"] == get_listener_meta()[0]
    assert "drillholes" in check_payload["domains"]
    t.join(timeout=2.0)
    srv.close()

    # --check returns non-zero exit code when listener is unreachable
    assert mcp_main(["--check"]) == 1


def test_listener_reload_and_frame_limit():
    """Verify system.reload hot-reloads handlers and wire.read_message rejects oversized headers."""
    import pytest
    import wire
    from handlers import system as sys_handler

    res = sys_handler.system({"action": "reload", "module": "system"})
    assert res["reloaded"] == ["system"]
    assert res["count"] == 1

    class OversizedSock:
        def recv(self, _n):
            return wire.HEADER.pack(wire.MAX_MESSAGE_SIZE + 1)

    with pytest.raises(ValueError, match="Incoming message too large"):
        wire.read_message(OversizedSock())


def test_drillhole_stats_and_triangulation_cut_fill(monkeypatch):
    """Verify drillholes stats and triangulation cut_fill contracts with Pydantic validation."""
    from handlers import drillholes, triangulations

    from vulcan_mcp.models import CutFillResponse, DrillholeStatsResponse

    class FakeStatsDB:
        def __init__(self, rows):
            self._rows = rows
            self._idx = -1

        def table_list(self):
            return ["COLLARES", "LEYES"]

        def field_list(self, table):
            return ["HOLE_ID", "FROM", "TO", "CUT"]

        def field_list_strings(self, table):
            return ["HOLE_ID"]

        def __iter__(self):
            for i in range(len(self._rows)):
                self._idx = i
                yield self

        def get_table_name(self):
            return "LEYES"

        def get(self, field):
            return self._rows[self._idx][field]

        def close(self):
            pass

    fake_db = FakeStatsDB(
        [
            {"FROM": 0.0, "TO": 2.0, "CUT": 1.0},
            {"FROM": 2.0, "TO": 6.0, "CUT": 2.5},
            {"FROM": 6.0, "TO": 8.0, "CUT": None},
        ]
    )
    monkeypatch.setattr(drillholes, "_open", lambda params: fake_db)
    stats_res = drillholes.drillholes({"action": "stats", "db": "test.dhd.isis", "field": "CUT"})
    parsed_stats = DrillholeStatsResponse(status="success", **stats_res)
    assert parsed_stats.valid_count == 2
    assert parsed_stats.missing_count == 1
    assert parsed_stats.mean == 1.75
    assert parsed_stats.weighted_mean == 2.0
    assert parsed_stats.total_length == 6.0

    class FakeTri:
        def __init__(self, z_val):
            self._z = z_val

        def extent(self):
            return [[0.0, 0.0, 0.0], [20.0, 20.0, 100.0]]

        def get_elevation(self, x, y):
            return self._z

    class FakeVulcan:
        def triangulation(self, path):
            return FakeTri(100.0) if "base" in path else FakeTri(95.0)

    monkeypatch.setattr(triangulations, "resolve", lambda name, suffixes: name)
    monkeypatch.setattr(triangulations, "vulcan", lambda: FakeVulcan())
    cf_res = triangulations.triangulation(
        {"action": "cut_fill", "name": "base.00t", "target_name": "pit.00t", "step": 10.0}
    )
    parsed_cf = CutFillResponse(status="success", **cf_res)
    assert parsed_cf.sampled_cells == 4
    assert parsed_cf.area_evaluated_m2 == 400.0
    assert parsed_cf.cut_volume_m3 == 2000.0
    assert parsed_cf.fill_volume_m3 == 0.0
    assert parsed_cf.net_volume_m3 == -2000.0


def test_triangulation_cut_fill_ignores_sentinels(monkeypatch):
    """Verify cut_fill skips NaN, Inf, and Vulcan -9999.0 no-data cells."""
    from handlers import triangulations

    class SentinelTri:
        def __init__(self, z_map):
            self._z_map = z_map

        def extent(self):
            return [[0.0, 0.0, 0.0], [20.0, 20.0, 100.0]]

        def get_elevation(self, x, y):
            return self._z_map.get((round(x, 1), round(y, 1)), 100.0)

    base_map = {
        (5.0, 5.0): 100.0,
        (5.0, 15.0): float("nan"),
        (15.0, 5.0): -9999.0,
        (15.0, 15.0): float("inf"),
    }
    target_map = {
        (5.0, 5.0): 95.0,
        (5.0, 15.0): 95.0,
        (15.0, 5.0): 95.0,
        (15.0, 15.0): 95.0,
    }

    class FakeVulcan:
        def triangulation(self, path):
            return SentinelTri(base_map if "base" in path else target_map)

    monkeypatch.setattr(triangulations, "resolve", lambda name, suffixes: name)
    monkeypatch.setattr(triangulations, "vulcan", lambda: FakeVulcan())

    res = triangulations.triangulation(
        {"action": "cut_fill", "name": "base.00t", "target_name": "pit.00t", "step": 10.0}
    )
    assert res["sampled_cells"] == 1
    assert res["area_evaluated_m2"] == 100.0
    assert res["cut_volume_m3"] == 500.0
    assert res["fill_volume_m3"] == 0.0
    assert res["net_volume_m3"] == -500.0
