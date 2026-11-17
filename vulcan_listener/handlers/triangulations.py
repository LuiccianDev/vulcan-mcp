"""Triangulation commands (.00t / .tri)."""
import math
import os

from .common import CommandError, command, list_files, require, resolve, run_action, to_list, vulcan, vulcan_gui

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


def _sample_elevation(tri, x, y):
    """Sample surface Z at (x, y), returning None for missing, NaN/Inf, or Vulcan -9999.0 sentinels."""
    try:
        z = tri.get_elevation(x, y)
    except Exception:
        return None
    if z is None:
        return None
    z_val = float(z)
    if math.isnan(z_val) or math.isinf(z_val) or z_val <= -9999.0:
        return None
    return z_val


def profile(params):
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
        z = _sample_elevation(tri, sx, sy)
        if z is not None:
            elevations.append(z)
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


def _extent_xy(raw_extent):
    """Extract (min_x, min_y, max_x, max_y) from Vulcan's nested [[min], [max]] or flat 6-float extent."""
    ext = to_list(raw_extent)
    if len(ext) == 2 and isinstance(ext[0], (list, tuple)):
        p_min = to_list(ext[0])
        p_max = to_list(ext[1])
        return float(p_min[0]), float(p_min[1]), float(p_max[0]), float(p_max[1])
    return float(ext[0]), float(ext[1]), float(ext[3]), float(ext[4])


def cut_fill(params):
    """Calculate cut, fill, and net volumes between a base surface and a target surface over a 2D grid."""
    base_name = require(params, "name")
    target_name = require(params, "target_name")
    step = float(params.get("step") if params.get("step") is not None else 10.0)
    if step <= 0.0:
        raise CommandError("Grid step must be greater than 0")

    base_tri = vulcan().triangulation(resolve(base_name, SUFFIXES))
    target_tri = vulcan().triangulation(resolve(target_name, SUFFIXES))

    b_min_x, b_min_y, b_max_x, b_max_y = _extent_xy(base_tri.extent())
    t_min_x, t_min_y, t_max_x, t_max_y = _extent_xy(target_tri.extent())
    min_x = max(b_min_x, t_min_x)
    min_y = max(b_min_y, t_min_y)
    max_x = min(b_max_x, t_max_x)
    max_y = min(b_max_y, t_max_y)

    if min_x >= max_x or min_y >= max_y:
        raise CommandError("Surfaces '{}' and '{}' have no overlapping XY extent".format(base_name, target_name))

    nx = int((max_x - min_x) / step) + 1
    ny = int((max_y - min_y) / step) + 1
    if nx * ny > 250000:
        raise CommandError("Grid too dense ({} cells); increase 'step' above {}".format(nx * ny, step))

    cell_area = step * step
    cut_vol = 0.0
    fill_vol = 0.0
    sampled = 0

    for ix in range(nx):
        x = min_x + (ix + 0.5) * step
        if x > max_x:
            continue
        for iy in range(ny):
            y = min_y + (iy + 0.5) * step
            if y > max_y:
                continue
            zb = _sample_elevation(base_tri, x, y)
            zt = _sample_elevation(target_tri, x, y)
            if zb is None or zt is None:
                continue
            sampled += 1
            diff = zt - zb
            if diff < 0.0:
                cut_vol += (-diff) * cell_area
            elif diff > 0.0:
                fill_vol += diff * cell_area

    return {
        "base_triangulation": base_name,
        "target_triangulation": target_name,
        "step": step,
        "sampled_cells": sampled,
        "area_evaluated_m2": round(sampled * cell_area, 2),
        "cut_volume_m3": round(cut_vol, 2),
        "fill_volume_m3": round(fill_vol, 2),
        "net_volume_m3": round(fill_vol - cut_vol, 2),
    }


ACTIONS = {
    "list": list_tris,
    "info": info,
    "elevation": elevation,
    "profile": profile,
    "cut_fill": cut_fill,
    "point_inside": point_inside,
    "load": load,
    "unload": unload,
}


@command("triangulation", timeout=45)
def triangulation(params):
    return run_action(ACTIONS, params)
