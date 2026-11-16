"""Triangulation commands (.00t / .tri)."""
import os

from .common import command, list_files, require, resolve, run_action, to_list, vulcan, vulcan_gui

SUFFIXES = (".00t", ".tri")


def list_tris(params):
    return {"triangulations": list_files(SUFFIXES)}


def info(params):
    path = resolve(require(params, "name"), SUFFIXES)
    tri = vulcan().triangulation(path)
    closed = bool(tri.is_closed())
    out = {
        "name": params["name"],
        "nodes": tri.n_nodes(),
        "faces": tri.n_faces(),
        "extent": to_list(tri.extent()),
        "closed": closed,
        "consistent": bool(tri.is_consistent()),
        "crossing": bool(tri.is_crossing()),
        "ok": bool(tri.is_ok()),
        "centroid": to_list(tri.centroid())[:3],
    }
    if closed:
        out["volume"] = tri.volume()
    try:
        out["colour_index"] = tri.get_colour_index()
    except Exception:
        pass
    return out


def elevation(params):
    path = resolve(require(params, "name"), SUFFIXES)
    points = require(params, "points")
    tri = vulcan().triangulation(path)
    return {"name": params["name"],
            "elevations": [{"x": p[0], "y": p[1], "z": tri.get_elevation(float(p[0]), float(p[1]))}
                           for p in points]}


def load(params):
    path = resolve(require(params, "name"), SUFFIXES)
    ok = vulcan_gui().load_triangulation(path)
    return {"loaded": bool(ok) if ok is not None else True, "name": os.path.basename(path)}


def unload(params):
    path = resolve(require(params, "name"), SUFFIXES)
    vulcan_gui().remove_triangulations([path])
    return {"removed": os.path.basename(path)}


def point_inside(params):
    path = resolve(require(params, "name"), SUFFIXES)
    points = require(params, "points")
    tri = vulcan().triangulation(path)
    return {
        "name": params["name"],
        "results": [
            {"point": p, "inside": bool(tri.point_inside(float(p[0]), float(p[1]), float(p[2])))}
            for p in points
        ],
    }


def profile(params):
    import math
    path = resolve(require(params, "name"), SUFFIXES)
    start_pt = require(params, "start")
    end_pt = require(params, "end")
    step = float(params.get("step") or 10.0)
    if step <= 0.0:
        step = 10.0

    x1, y1 = float(start_pt[0]), float(start_pt[1])
    x2, y2 = float(end_pt[0]), float(end_pt[1])
    total_length = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    tri = vulcan().triangulation(path)
    n_samples = max(2, int(total_length / step) + 1)
    points = []
    elevations = []

    for i in range(n_samples):
        fraction = float(i) / float(n_samples - 1)
        sx = x1 + fraction * (x2 - x1)
        sy = y1 + fraction * (y2 - y1)
        station = fraction * total_length
        try:
            z = tri.get_elevation(sx, sy)
            if z is not None and not math.isnan(z) and z > -9999.0:
                elevations.append(z)
            else:
                z = None
        except Exception:
            z = None
        points.append({
            "station": round(station, 2),
            "x": round(sx, 3),
            "y": round(sy, 3),
            "z": round(z, 3) if z is not None else None,
        })

    return {
        "triangulation": params["name"],
        "total_length": round(total_length, 2),
        "step": step,
        "min_elevation": round(min(elevations), 3) if elevations else None,
        "max_elevation": round(max(elevations), 3) if elevations else None,
        "points": points,
    }


ACTIONS = {
    "list": list_tris,
    "info": info,
    "elevation": elevation,
    "profile": profile,
    "point_inside": point_inside,
    "load": load,
    "unload": unload,
}


@command("triangulation", timeout=45)
def triangulation(params):
    return run_action(ACTIONS, params)
