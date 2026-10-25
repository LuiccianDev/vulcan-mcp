"""System commands: connectivity, project inventory, capabilities."""
import os
import sys

from .common import command, project_dir, run_action

CATEGORIES = [
    ("block_models", (".bmf",)),
    ("triangulations", (".00t", ".tri")),
    ("design_dbs", (".dgd.isis",)),
    ("drillhole_dbs", (".dhd.isis",)),
    ("specs", (".dsf",)),
    ("legends", (".scd",)),
    ("scripts", (".bcf", ".lava", ".py")),
]


def _has(module_name):
    try:
        __import__(module_name)
        return True
    except Exception:
        return False


def ping(params):
    return {
        "connected": True,
        "app": "Maptek Vulcan",
        "python": sys.version.split()[0],
        "vulcan_api": _has("maptek.vulcan"),
        "project_dir": project_dir(),
    }


def project_info(params):
    files = os.listdir(project_dir())
    inventory = {}
    for name, suffixes in CATEGORIES:
        matches = sorted(f for f in files if f.lower().endswith(suffixes))
        inventory[name] = {"count": len(matches), "files": matches[:50]}
    return {"project_dir": project_dir(), "inventory": inventory}


def capabilities(params):
    caps = {"maptek.vulcan": _has("maptek.vulcan"), "maptek.vulcan_gui": _has("maptek.vulcan_gui"),
            "pandas": _has("pandas"), "PIL": _has("PIL.ImageGrab"), "win32gui": _has("win32gui")}
    try:
        import maptek.vulcan_gui as vg
        caps["gfx"] = hasattr(vg, "gfx")
    except Exception:
        caps["gfx"] = False
    return caps


ACTIONS = {"ping": ping, "project_info": project_info, "capabilities": capabilities}


@command("system", timeout=15)
def system(params):
    return run_action(ACTIONS, params)
