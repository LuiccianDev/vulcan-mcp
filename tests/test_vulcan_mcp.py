"""Automated unit and structural tests for vulcan-mcp."""
import ast
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "vulcan_listener"))

import server as listener_server  # noqa: E402
import wire  # noqa: E402
from handlers.common import COMMANDS  # noqa: E402


def test_python35_compatibility_no_fstrings():
    """Ensure no f-strings (JoinedStr, added in Python 3.6) exist in vulcan_listener/."""
    listener_dir = ROOT / "vulcan_listener"
    for py_file in listener_dir.rglob("*.py"):
        source = py_file.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(py_file))
        for node in ast.walk(tree):
            assert not isinstance(node, ast.JoinedStr), (
                f"Python 3.6+ f-string found in {py_file}:{getattr(node, 'lineno', '?')} "
                "(Vulcan 12 uses Python 3.5.2)"
            )


def test_all_domains_registered():
    expected = {"system", "block_model", "triangulation", "design", "drillholes", "legend", "canvas", "execute_code"}
    assert set(COMMANDS.keys()) == expected


def test_system_ping_and_capabilities():
    res = listener_server.dispatch({"type": "system", "params": {"action": "ping"}})
    assert res["status"] == "success"
    assert res["result"]["connected"] is True

    caps = listener_server.dispatch({"type": "system", "params": {"action": "capabilities"}})
    assert caps["status"] == "success"
    assert "maptek.vulcan" in caps["result"]


def test_token_authentication(monkeypatch):
    monkeypatch.setattr(listener_server, "TOKEN", "secret-mining-token")
    bad = listener_server.dispatch({"type": "system", "params": {"action": "ping"}})
    assert bad["status"] == "error"
    assert "Authentication failed" in bad["message"]

    good = listener_server.dispatch(
        {"type": "system", "params": {"action": "ping"}, "token": "secret-mining-token"}
    )
    assert good["status"] == "success"


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
    monkeypatch.setattr(listener_server, "TOKEN", "")

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
        {"type": "execute_code", "params": {"code": "x = 21 * 2\nprint('hello')\nresult = {'answer': x}"}}
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
