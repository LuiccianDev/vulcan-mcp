"""Live integration test suite for vulcan-mcp against a running Maptek Vulcan 12 session.

Can be executed either directly:
    python tests/test_live.py
or via pytest:
    pytest tests/test_live.py -v -s
"""

import sys
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from vulcan_mcp.client import VulcanMCPClient  # noqa: E402

client = VulcanMCPClient()


def _is_vulcan_listening() -> bool:
    try:
        res = client.send_command("system", {"action": "ping"}, timeout=3.0)
        return bool(res.get("connected"))
    except Exception:
        return False


pytestmark = pytest.mark.skipif(
    not _is_vulcan_listening(),
    reason="Vulcan listener is not running on 127.0.0.1:9877",
)


def test_level1_ping():
    res = client.send_command("system", {"action": "ping"})
    assert res["connected"] is True
    assert res["vulcan_api"] is True
    # Hot-reload handlers in the running Vulcan listener so latest on-disk handlers are active
    client.send_command(
        "execute_code",
        {
            "code": (
                "import importlib, handlers.block_models, handlers.drillholes, handlers.design\n"
                "importlib.reload(handlers.block_models)\n"
                "importlib.reload(handlers.drillholes)\n"
                "importlib.reload(handlers.design)\n"
                "result = True"
            )
        },
    )
    print(f"\n[L1 PASS] Connected to {res['app']} (Python {res['python']}) in {res['project_dir']}")


def test_level2_project_inventory():
    res = client.send_command("system", {"action": "project_info"})
    inv = res["inventory"]
    assert inv["block_models"]["count"] >= 1
    assert inv["triangulations"]["count"] >= 1
    assert inv["design_dbs"]["count"] >= 1
    assert inv["drillhole_dbs"]["count"] >= 1
    assert inv["legends"]["count"] >= 1
    print(f"\n[L2 PASS] Inventory: { {k: v['count'] for k, v in inv.items()} }")


def test_level3_block_model():
    models = client.send_command("block_model", {"action": "list"})["block_models"]
    model = "bmw_ml_30_30_30.bmf" if "bmw_ml_30_30_30.bmf" in models else models[0]

    info = client.send_command("block_model", {"action": "info", "model": model})
    assert info["n_blocks"] > 0
    var_names = [v["name"] for v in info["variables"]]
    print(f"\n[L3.1 PASS] Model '{model}': {info['n_blocks']} blocks, vars={var_names}")

    # Compute world midpoint from model origin + local extent
    orig = info["origin"]
    ext = info["extent"]
    mx = orig[0] + (ext[0] + ext[1]) / 2.0
    my = orig[1] + (ext[2] + ext[3]) / 2.0
    mz = orig[2] + (ext[4] + ext[5]) / 2.0
    q = client.send_command(
        "block_model", {"action": "query_xyz", "model": model, "x": mx, "y": my, "z": mz}
    )
    assert q["found"] is True, f"Block not found at ({mx}, {my}, {mz}): {q}"
    print(
        f"[L3.2 PASS] Block @ ({mx:.1f}, {my:.1f}, {mz:.1f}) -> cobre_iw2={q['block'].get('cobre_iw2')}"
    )

    grade_var = next(
        (v for v in ("cobre_iw2", "cobre_iwd2", "cobre") if v in var_names), var_names[0]
    )
    stats = client.send_command(
        "block_model",
        {"action": "stats", "model": model, "variable": grade_var, "cutoff": 0.4, "density": 2.7},
        timeout=120.0,
    )
    assert stats["summary"]["blocks"] > 0
    print(
        f"[L3.3 PASS] Stats for '{grade_var}': {stats['summary']} | Above cutoff: {stats.get('above_cutoff')}"
    )


def test_level4_triangulation():
    tris = client.send_command("triangulation", {"action": "list"})["triangulations"]
    name = "toposiccha_exten.00t" if "toposiccha_exten.00t" in tris else tris[0]

    info = client.send_command("triangulation", {"action": "info", "name": name})
    assert info["nodes"] > 0 and info["faces"] > 0
    print(
        f"\n[L4.1 PASS] Triangulation '{name}': {info['nodes']} nodes, {info['faces']} faces, closed={info['closed']}"
    )

    ext = info["extent"]
    cx = (ext[0][0] + ext[1][0]) / 2.0
    cy = (ext[0][1] + ext[1][1]) / 2.0
    elev = client.send_command(
        "triangulation", {"action": "elevation", "name": name, "points": [[cx, cy]]}
    )
    assert len(elev["elevations"]) == 1
    print(f"[L4.2 PASS] Elevation @ ({cx:.1f}, {cy:.1f}) -> Z = {elev['elevations'][0]['z']:.2f}")


def test_level5_drillholes():
    dbs = client.send_command("drillholes", {"action": "list_dbs"})["drillhole_dbs"]
    db = "bmw_sondajes.dhd.isis" if "bmw_sondajes.dhd.isis" in dbs else dbs[0]

    schema = client.send_command("drillholes", {"action": "schema", "db": db})
    assert schema["holes"] > 0
    print(
        f"\n[L5.1 PASS] Drillhole DB '{db}': {schema['holes']} holes, tables={list(schema['tables'].keys())}"
    )

    holes = client.send_command("drillholes", {"action": "holes", "db": db, "limit": 5})
    first_hole = holes["items"][0]
    hole_data = client.send_command(
        "drillholes", {"action": "hole", "db": db, "hole": first_hole, "limit": 5}
    )
    assert len(hole_data["tables"]) >= 1
    print(
        f"[L5.2 PASS] Hole '{first_hole}' tables fetched: { {k: len(v) for k, v in hole_data['tables'].items()} }"
    )

    if "LEYES" in schema["tables"] and "CUT" in schema["tables"]["LEYES"]:
        hg = client.send_command(
            "drillholes",
            {
                "action": "high_grade",
                "db": db,
                "table": "LEYES",
                "field": "CUT",
                "min_value": 1.0,
                "limit": 5,
            },
            timeout=120.0,
        )
        print(
            f"[L5.3 PASS] High-grade intervals (>=1.0% Cu): {hg['matches']} matches, top 3={hg['top'][:3]}"
        )

    disp = client.send_command(
        "drillholes",
        {"action": "display", "db": db, "table": "LEYES", "field": "CUT", "limit": 5},
        timeout=60.0,
    )
    assert disp["displayed"] is True
    assert disp["segments_rendered"] > 0
    print(
        f"[L5.4 PASS] 3D Drillholes displayed in Vulcan viewport: "
        f"{disp['holes_count']} holes, {disp['segments_rendered']} coloured 3D segments"
    )


def test_level6_design_cad():
    dbs = client.send_command("design", {"action": "list_dbs"})["design_dbs"]
    dgd = "baisusxier.dgd.isis" if "baisusxier.dgd.isis" in dbs else dbs[0]

    layers = client.send_command("design", {"action": "list_layers", "dgd": dgd})["layers"]
    assert len(layers) >= 1
    print(f"\n[L6.1 PASS] DGD '{dgd}' layers: {[layer_obj['name'] for layer_obj in layers]}")

    target_layer = (
        "SONDAJE_LEYES"
        if any(layer_obj["name"] == "SONDAJE_LEYES" for layer_obj in layers)
        else layers[0]["name"]
    )
    linfo = client.send_command(
        "design", {"action": "layer_info", "dgd": dgd, "layer": target_layer, "limit": 3}
    )
    assert linfo["total"] >= 0
    print(
        f"[L6.2 PASS] Layer '{target_layer}': {linfo['total']} objects, sample={linfo['items'][:2]}"
    )


def test_level7_legends():
    legends = client.send_command("legend", {"action": "list"})["legends"]
    scd = "bai.scd" if "bai.scd" in legends else legends[0]

    inspected = client.send_command("legend", {"action": "inspect", "scd": scd})
    assert "DRILL_COLOUR" in inspected["schemes"]
    print(
        f"\n[L7 PASS] Legend '{scd}' schemes: { {k: list(v.keys()) for k, v in inspected['schemes'].items()} }"
    )


def test_level8_screenshot():
    snap = client.send_command("canvas", {"action": "screenshot", "max_width": 800, "quality": 70})
    assert snap["mime_type"] == "image/jpeg"
    assert snap["width"] <= 800
    assert snap["bytes"] > 500
    print(
        f"\n[L8 PASS] Screenshot captured: {snap['width']}x{snap['height']} JPEG ({snap['bytes'] / 1024:.1f} KB)"
    )


def test_level9_execute_code():
    res = client.send_command(
        "execute_code",
        {
            "code": "import maptek.vulcan as v\nresult = {'has_bm': hasattr(v, 'block_model'), 'dir': project_dir}"
        },
    )
    assert res["executed"] is True
    assert res["result"]["has_bm"] is True
    print(f"\n[L9 PASS] Custom PyVulcan code executed: {res['result']}")


def run_all_cli():
    print("=" * 70)
    print("VULCAN MCP - LIVE INTEGRATION TEST SUITE (9 LEVELS)")
    print("=" * 70)
    if not _is_vulcan_listening():
        print("[ERROR] Vulcan listener is not reachable on 127.0.0.1:9877")
        sys.exit(1)

    tests = [
        ("Level 1: Connectivity & Ping", test_level1_ping),
        ("Level 2: Project Inventory", test_level2_project_inventory),
        ("Level 3: Block Models (.bmf)", test_level3_block_model),
        ("Level 4: Triangulations (.00t)", test_level4_triangulation),
        ("Level 5: Drillholes (.dhd.isis)", test_level5_drillholes),
        ("Level 6: CAD Design (.dgd.isis)", test_level6_design_cad),
        ("Level 7: Colour Legends (.scd)", test_level7_legends),
        ("Level 8: Viewport Screenshot (JPEG)", test_level8_screenshot),
        ("Level 9: PyVulcan Code Execution", test_level9_execute_code),
    ]
    passed = 0
    for title, fn in tests:
        t0 = time.perf_counter()
        try:
            fn()
            dt = (time.perf_counter() - t0) * 1000
            print(f"  --> PASS ({dt:.0f} ms)")
            passed += 1
        except Exception as exc:
            print(f"  --> FAIL in {title}: {exc}")

    print("=" * 70)
    print(f"RESULT: {passed}/{len(tests)} levels passed.")
    print("=" * 70)
    sys.exit(0 if passed == len(tests) else 1)


if __name__ == "__main__":
    run_all_cli()
