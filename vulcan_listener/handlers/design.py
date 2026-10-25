"""Design database commands (.dgd.isis): layers, objects, polylines, and 3D display."""
from .common import (CommandError, command, list_files, page, require, resolve, run_action,
                     to_list, vulcan, vulcan_gui)

SUFFIXES = (".dgd.isis",)
LOAD_METHODS = ("LOAD_IF_EXISTS", "CLEAR_IF_EXISTS", "ACTIVE_IF_EXISTS")
_DESIGN_TEMP_OBJECTS = []


def _open(params, mode=None):
    path = resolve(require(params, "dgd"), SUFFIXES)
    return vulcan().dgd(path, mode) if mode else vulcan().dgd(path)


def _get_layer(db, name):
    if not db.is_layer(name):
        raise CommandError("Layer '{}' not found. Available: {}".format(name, ", ".join(to_list(db.list_layers()))))
    return db.get_layer(name)


def _safe(obj, method):
    try:
        return getattr(obj, method)()
    except Exception:
        return None


def list_dbs(params):
    return {"design_dbs": list_files(SUFFIXES)}


def list_layers(params):
    db = _open(params)
    try:
        layers = []
        for name in to_list(db.list_layers()):
            if name.startswith("DIG$"):  # internal Vulcan bookkeeping layers
                continue
            layers.append({"name": name, "objects": db.get_layer(name).num_objects()})
        return {"dgd": params["dgd"], "layers": layers}
    finally:
        db.close()


def layer_info(params):
    db = _open(params)
    try:
        layer = _get_layer(db, require(params, "layer"))
        objects = []
        for i in range(layer.num_objects()):
            o = layer.get_object(i)
            entry = {"index": i, "name": _safe(o, "get_name"), "type": _safe(o, "get_type"),
                     "colour": _safe(o, "get_colour"), "description": _safe(o, "get_description")}
            for key, method in (("points", "num_points"), ("length", "length"), ("closed", "is_closed")):
                value = _safe(o, method)
                if value is not None:
                    entry[key] = value
            objects.append(entry)
        result = page(objects, params, default_limit=20)
        result.update({"dgd": params["dgd"], "layer": params["layer"],
                       "description": _safe(layer, "get_description")})
        return result
    finally:
        db.close()


def clear_temp(params):
    removed = 0
    while _DESIGN_TEMP_OBJECTS:
        pair = _DESIGN_TEMP_OBJECTS.pop()
        try:
            pair[0].remove()
            removed += 1
        except Exception:
            pass
    return {"cleared": removed}


def load_layer(params):
    method = params.get("load_method") or "LOAD_IF_EXISTS"
    if method not in LOAD_METHODS:
        raise CommandError("load_method must be one of: {}".format(", ".join(LOAD_METHODS)))
    db = _open(params)
    try:
        layer = _get_layer(db, require(params, "layer"))
        objs = [layer.get_object(i) for i in range(layer.num_objects())]
    finally:
        db.close()

    vg = vulcan_gui()
    use_temp = params.get("use_temp_objects", True)
    if use_temp:
        if params.get("clear_previous", False):
            clear_temp({})
        shown = 0
        for o in objs:
            try:
                tobj = vg.temp_object(o)
                _DESIGN_TEMP_OBJECTS.append((tobj, o))
                shown += 1
            except Exception:
                pass
        return {
            "loaded": shown > 0,
            "layer": params["layer"],
            "objects_displayed": shown,
            "mode": "temp_object",
        }

    ok = vg.add_layer(layer, method)
    return {"loaded": bool(ok), "layer": params["layer"], "load_method": method, "mode": "add_layer"}


def create_polyline(params):
    points = require(params, "points")
    if len(points) < 2:
        raise CommandError("A polyline needs at least 2 points")
    layer_name = require(params, "layer")
    v = vulcan()
    db = _open(params, "w")
    try:
        layer = db.get_layer(layer_name) if db.is_layer(layer_name) else None
        if layer is None:
            layer = v.layer(layer_name)
            db.append(layer)
        line = v.polyline()
        line.set_coordinates([[float(c) for c in p] for p in points])
        line.set_connected()
        if params.get("closed"):
            line.set_closed()
        if params.get("colour") is not None:
            line.set_colour(int(params["colour"]))
        if params.get("name"):
            line.set_name(str(params["name"]))
        layer.append(line)
        db.save_layer(layer)
        return {"created": True, "dgd": params["dgd"], "layer": layer_name, "points": len(points),
                "closed": bool(params.get("closed"))}
    finally:
        db.close()


ACTIONS = {
    "list_dbs": list_dbs,
    "list_layers": list_layers,
    "layer_info": layer_info,
    "load_layer": load_layer,
    "clear_temp": clear_temp,
    "create_polyline": create_polyline,
}


@command("design", timeout=45)
def design(params):
    return run_action(ACTIONS, params)
