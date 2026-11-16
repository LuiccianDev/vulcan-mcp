"""Block model commands (.bmf) through maptek.vulcan.block_model."""
from .common import (CommandError, command, list_files, require, resolve, run_action,
                     to_list, vulcan)

SUFFIXES = (".bmf",)
WORLD_FIELDS = ["xworld", "yworld", "zworld", "xlength", "ylength", "zlength"]


def _open(params):
    return vulcan().block_model(resolve(require(params, "model"), SUFFIXES))


def _fields(bm):
    return [str(f) for f in to_list(bm.field_list())]


def _value(bm, field):
    if bm.is_string(field):
        return bm.get_string(field)
    return bm.get(field)


def list_models(params):
    return {"block_models": list_files(SUFFIXES)}


def info(params):
    bm = _open(params)
    try:
        fields = []
        for name in _fields(bm):
            entry = {"name": name}
            for key, getter in (("type", "field_type"), ("default", "field_default_string"),
                                ("description", "field_description")):
                try:
                    entry[key] = getattr(bm, getter)(name)
                except Exception:
                    pass
            fields.append(entry)
        schemas = []
        for k in range(int(bm.model_n_schemas())):
            schemas.append({"extent": to_list(bm.model_schema_extent(k)),
                            "block_size": to_list(bm.model_schema_size(k))})
        orig = to_list(bm.model_origin())
        ext = to_list(bm.model_extent())
        world_ext = [
            orig[0] + ext[0], orig[0] + ext[1],
            orig[1] + ext[2], orig[1] + ext[3],
            orig[2] + ext[4], orig[2] + ext[5],
        ] if len(orig) == 3 and len(ext) == 6 else ext
        return {
            "model": params["model"],
            "n_blocks": bm.n_blocks(),
            "origin": orig,
            "orientation": to_list(bm.model_orientation()),
            "extent": ext,
            "world_extent": world_ext,
            "schemas": schemas,
            "variables": fields,
        }
    finally:
        bm.close()


def query_xyz(params):
    x, y, z = float(require(params, "x")), float(require(params, "y")), float(require(params, "z"))
    bm = _open(params)
    try:
        code = bm.find_world_xyz(x, y, z)
        if code != 0:
            return {"found": False, "point": [x, y, z], "code": code,
                    "hint": "Point is outside the model or in an empty region"}
        wanted = params.get("variables") or _fields(bm)
        values = {}
        for field in list(wanted) + WORLD_FIELDS:
            try:
                values[field] = _value(bm, field)
            except Exception as exc:
                values[field] = "error: {}".format(exc)
        return {"found": True, "point": [x, y, z], "block": values}
    finally:
        bm.close()


def stats(params):
    variable = require(params, "variable")
    bm = _open(params)
    try:
        if variable not in _fields(bm):
            raise CommandError("Variable '{}' not in model. Available: {}".format(variable, ", ".join(_fields(bm))))
        try:
            frame = bm.get_pandas([variable, "xlength", "ylength", "zlength"], params.get("select") or "")
        except ImportError:
            raise CommandError("pandas is not available in Vulcan's Python")
        try:
            default = float(bm.field_default_string(variable))
            frame = frame[frame[variable] != default]
        except Exception:
            default = None
        frame = frame.assign(volume=frame["xlength"] * frame["ylength"] * frame["zlength"])
        result = {"variable": variable, "select": params.get("select") or "",
                  "excluded_default": default, "summary": _summary(frame, variable, params)}
        cutoff = params.get("cutoff")
        if cutoff is not None:
            result["above_cutoff"] = _summary(frame[frame[variable] >= float(cutoff)], variable, params)
            result["above_cutoff"]["cutoff"] = float(cutoff)
        return result
    finally:
        bm.close()


def _summary(frame, variable, params):
    if len(frame) == 0:
        return {"blocks": 0}
    volume = float(frame["volume"].sum())
    out = {
        "blocks": int(len(frame)),
        "min": float(frame[variable].min()),
        "max": float(frame[variable].max()),
        "mean": float(frame[variable].mean()),
        "volume_weighted_mean": float((frame[variable] * frame["volume"]).sum() / volume) if volume else None,
        "volume": volume,
    }
    density = params.get("density")
    if density is not None:
        out["tonnes"] = volume * float(density)
    return out


def grade_tonnage_curve(params):
    variable = require(params, "variable")
    density = float(params.get("density") or 2.7)
    cutoffs_param = params.get("cutoffs")
    if cutoffs_param is not None and isinstance(cutoffs_param, (list, tuple)):
        cutoffs = [float(c) for c in cutoffs_param]
    else:
        cutoffs = None

    bm = _open(params)
    try:
        if variable not in _fields(bm):
            raise CommandError("Variable '{}' not in model. Available: {}".format(variable, ", ".join(_fields(bm))))
        try:
            frame = bm.get_pandas([variable, "xlength", "ylength", "zlength"], params.get("select") or "")
        except ImportError:
            raise CommandError("pandas is not available in Vulcan's Python")

        try:
            default = float(bm.field_default_string(variable))
            frame = frame[frame[variable] != default]
        except Exception:
            default = None

        frame = frame[frame[variable] >= 0.0]
        frame = frame.assign(volume=frame["xlength"] * frame["ylength"] * frame["zlength"])
        frame = frame.assign(tonnes=frame["volume"] * density)

        if len(frame) == 0:
            return {
                "model_name": params["model"],
                "variable": variable,
                "density": density,
                "total_blocks": 0,
                "total_volume": 0.0,
                "total_tonnes": 0.0,
                "overall_mean_grade": 0.0,
                "intervals": [],
            }

        total_blocks = int(len(frame))
        total_volume = float(frame["volume"].sum())
        total_tonnes = float(frame["tonnes"].sum())
        total_metal = float((frame[variable] * frame["tonnes"]).sum())
        overall_mean = (total_metal / total_tonnes) if total_tonnes > 0 else 0.0

        if cutoffs is None:
            min_grade = float(frame[variable].min())
            max_grade = float(frame[variable].max())
            step = (max_grade - min_grade) / 5.0 if max_grade > min_grade else 1.0
            cutoffs = [round(min_grade + i * step, 4) for i in range(6)]

        intervals = []
        for cut in cutoffs:
            sub = frame[frame[variable] >= cut]
            if len(sub) == 0:
                intervals.append({
                    "cutoff": cut,
                    "blocks_above": 0,
                    "volume": 0.0,
                    "tonnes": 0.0,
                    "mean_grade": 0.0,
                    "metal_content": 0.0,
                })
                continue
            vol = float(sub["volume"].sum())
            tons = float(sub["tonnes"].sum())
            metal = float((sub[variable] * sub["tonnes"]).sum())
            mean_g = (metal / tons) if tons > 0 else 0.0
            intervals.append({
                "cutoff": cut,
                "blocks_above": int(len(sub)),
                "volume": round(vol, 2),
                "tonnes": round(tons, 2),
                "mean_grade": round(mean_g, 4),
                "metal_content": round(metal, 2),
            })

        return {
            "model_name": params["model"],
            "variable": variable,
            "density": density,
            "total_blocks": total_blocks,
            "total_volume": round(total_volume, 2),
            "total_tonnes": round(total_tonnes, 2),
            "overall_mean_grade": round(overall_mean, 4),
            "intervals": intervals,
        }
    finally:
        bm.close()


ACTIONS = {"list": list_models, "info": info, "query_xyz": query_xyz, "stats": stats, "grade_tonnage_curve": grade_tonnage_curve}


@command("block_model", timeout=120)
def block_model(params):
    return run_action(ACTIONS, params)
