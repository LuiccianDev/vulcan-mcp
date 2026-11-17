"""System commands: connectivity, project inventory, capabilities."""
import os
import sys

from .common import (
    COMMANDS,
    CommandError,
    command,
    get_listener_meta,
    project_dir,
    run_action,
)

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


def _discover_handler_modules():
    """Discover loaded handler modules from sys.modules without a hardcoded registry."""
    prefix = "handlers."
    modules = {}
    for mod_name, mod in list(sys.modules.items()):
        if not mod_name.startswith(prefix) or mod_name == "handlers.common" or mod is None:
            continue
        short_name = mod_name[len(prefix) :]
        if "." not in short_name:
            modules[short_name] = mod_name
    return modules


def ping(params):
    version, protocol = get_listener_meta()
    return {
        "connected": True,
        "app": "Maptek Vulcan",
        "listener_version": version,
        "protocol_version": protocol,
        "python": sys.version.split()[0],
        "vulcan_api": _has("maptek.vulcan"),
        "project_dir": project_dir(),
        "domains": sorted(COMMANDS.keys()),
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


def reload_handlers(params):
    available = _discover_handler_modules()
    target = params.get("module")
    if target is not None:
        if target not in available:
            raise CommandError("Unknown handler module '{}'. Available: {}".format(
                target, ", ".join(sorted(available.keys()))
            ))
        targets = [target]
    else:
        targets = sorted(available.keys())

    try:
        import imp
        reloader = imp.reload
    except ImportError:
        import importlib
        reloader = importlib.reload

    reloaded = []
    for name in targets:
        mod_name = available[name]
        mod = sys.modules.get(mod_name)
        if mod is None:
            mod = __import__(mod_name, fromlist=["*"])
        reloader(mod)
        reloaded.append(name)
    return {"reloaded": reloaded, "count": len(reloaded)}


ACTIONS = {
    "ping": ping,
    "project_info": project_info,
    "capabilities": capabilities,
    "reload": reload_handlers,
}


@command("system", timeout=15)
def system(params):
    return run_action(ACTIONS, params)
