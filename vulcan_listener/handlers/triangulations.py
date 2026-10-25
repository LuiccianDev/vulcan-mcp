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


ACTIONS = {"list": list_tris, "info": info, "elevation": elevation, "load": load, "unload": unload}


@command("triangulation", timeout=45)
def triangulation(params):
    return run_action(ACTIONS, params)
