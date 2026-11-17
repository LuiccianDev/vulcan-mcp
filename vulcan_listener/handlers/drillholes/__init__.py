"""Drillhole commands over ISIS databases (.dhd.isis) and 3D viewport visualization (Python 3.5 compatible)."""

from ..common import command, run_action
from . import _analytics, _display, _isis

if globals().get("_INITIALIZED"):
    try:
        import imp
        _reloader = imp.reload
    except ImportError:
        import importlib
        _reloader = importlib.reload
    _reloader(_isis)
    _reloader(_display)
    _reloader(_analytics)
_INITIALIZED = True

_open = _isis.open_db
_field_cache = _isis.field_cache
_record = _isis.read_record
_desurvey_point = _display.desurvey_point
_grade_to_vulcan_colour = _display.grade_to_vulcan_colour


def _open_hook(params):
    return _open(params)


def _bind(fn):
    return lambda params: fn(params, open_fn=_open_hook)


ACTIONS = {
    "list_dbs": _isis.list_dbs,
    "schema": _bind(_isis.schema),
    "holes": _bind(_isis.holes),
    "hole": _bind(_isis.hole),
    "high_grade": _bind(_isis.high_grade),
    "display": _bind(_display.display_drillholes),
    "clear_display": _display.clear_display,
    "qaqc_validation": _bind(_analytics.qaqc_validation),
    "stats": _bind(_analytics.stats),
}


@command("drillholes", timeout=120)
def drillholes(params):
    return run_action(ACTIONS, params)
