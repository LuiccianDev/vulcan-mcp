"""Registry and helpers shared by every handler module (Python 3.5 compatible)."""
import os

# name -> (function, default_timeout_seconds)
COMMANDS = {}


class CommandError(Exception):
    """An error meant for the caller: its message is returned verbatim."""


def command(name, timeout=30):
    def decorator(fn):
        COMMANDS[name] = (fn, timeout)
        return fn
    return decorator


def run_action(actions, params):
    action = params.get("action")
    if action not in actions:
        raise CommandError("Unknown action '{}'. Valid actions: {}".format(
            action, ", ".join(sorted(actions))))
    return actions[action](params)


def require(params, key):
    value = params.get(key)
    if value is None or value == "":
        raise CommandError("Parameter '{}' is required for action '{}'".format(key, params.get("action")))
    return value


def vulcan():
    try:
        import maptek.vulcan as module
    except ImportError:
        raise CommandError("maptek.vulcan is not available: run the listener from Vulcan (File > Python Script)")
    return module


def vulcan_gui():
    try:
        import maptek.vulcan_gui as module
    except ImportError:
        raise CommandError("maptek.vulcan_gui is not available: run the listener from Vulcan (File > Python Script)")
    return module


def project_dir():
    return os.getcwd()


def resolve(name, suffixes):
    """Return the absolute path of a project file, or raise if it does not exist."""
    path = name if os.path.isabs(name) else os.path.join(project_dir(), name)
    if not os.path.isfile(path):
        raise CommandError("File not found: {} (expected one of: {})".format(name, ", ".join(suffixes)))
    if not path.lower().endswith(tuple(suffixes)):
        raise CommandError("'{}' is not a {} file".format(name, " / ".join(suffixes)))
    return path


def list_files(suffixes):
    base = project_dir()
    return sorted(
        f for f in os.listdir(base)
        if f.lower().endswith(tuple(suffixes)) and os.path.isfile(os.path.join(base, f))
    )


def page(items, params, default_limit=50):
    limit = int(params.get("limit") or default_limit)
    offset = int(params.get("offset") or 0)
    return {"total": len(items), "offset": offset, "limit": limit, "items": items[offset:offset + limit]}


def to_list(value):
    """SWIG vectors (double_list, string_list, nested lists) to plain Python lists."""
    try:
        return [to_list(v) for v in value] if not isinstance(value, (str, bytes)) else value
    except TypeError:
        return value
