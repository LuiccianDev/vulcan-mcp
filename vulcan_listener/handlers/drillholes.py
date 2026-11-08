"""Drillhole commands over ISIS databases (.dhd.isis) and 3D viewport visualization."""
import math

from .common import (CommandError, command, list_files, page, require, resolve, run_action,
                     to_list, vulcan, vulcan_gui)

SUFFIXES = (".dhd.isis",)
DGD_SUFFIXES = (".dgd.isis",)
MAX_RECORDS_PER_HOLE = 5000

# Held in memory so SWIG does not garbage-collect displayed 3D temp_objects
_ACTIVE_TEMP_OBJECTS = []


def _open(params):
    path = resolve(require(params, "db"), SUFFIXES)
    v = vulcan()
    try:
        return v.isisdb(path, "r", "")
    except Exception:
        return v.isisdb(path)


def _record(db, fields, string_fields):
    values = {}
    for field in fields:
        if field in string_fields:
            try:
                values[field] = db.get_string(field)
            except Exception:
                values[field] = None
        else:
            try:
                values[field] = db.get(field)
            except Exception:
                values[field] = None
    return values


def _field_cache(db):
    all_cache = {}
    str_cache = {}

    def fields_of(table):
        if table not in all_cache:
            all_cache[table] = [str(f) for f in to_list(db.field_list(table))]
            try:
                str_cache[table] = set(str(f) for f in to_list(db.field_list_strings(table)))
            except Exception:
                s = set()
                for fname in all_cache[table]:
                    try:
                        if db.is_string(fname, table):
                            s.add(fname)
                    except Exception:
                        pass
                str_cache[table] = s
        return all_cache[table], str_cache[table]

    return fields_of


def list_dbs(params):
    return {"drillhole_dbs": list_files(SUFFIXES)}


def schema(params):
    db = _open(params)
    try:
        tables = [str(t) for t in to_list(db.table_list())]
        fields_of = _field_cache(db)
        table_info = {}
        string_fields = {}
        for t in tables:
            f_all, f_str = fields_of(t)
            table_info[t] = f_all
            string_fields[t] = sorted(list(f_str))
        return {
            "db": params["db"],
            "tables": table_info,
            "string_fields": string_fields,
            "holes": len(to_list(db.key_list())),
        }
    finally:
        db.close()


def holes(params):
    db = _open(params)
    try:
        result = page([str(k) for k in to_list(db.key_list())], params, default_limit=50)
        result["db"] = params["db"]
        return result
    finally:
        db.close()


def hole(params):
    key = str(require(params, "hole"))
    wanted_table = params.get("table")
    limit = int(params.get("limit") or 200)
    db = _open(params)
    try:
        db.find_key(key)
        if str(db.get_key()) != key:
            raise CommandError("Hole '{}' not found in {}".format(key, params["db"]))
        fields_of = _field_cache(db)
        tables = {}
        for _ in range(MAX_RECORDS_PER_HOLE):
            table = str(db.get_table_name())
            if wanted_table is None or table == wanted_table:
                rows = tables.setdefault(table, [])
                if len(rows) < limit:
                    f_all, f_str = fields_of(table)
                    rows.append(_record(db, f_all, f_str))
            try:
                db.next()
            except Exception:
                break
            if str(db.get_key()) != key:
                break
        return {"db": params["db"], "hole": key, "tables": tables, "limit_per_table": limit}
    finally:
        db.close()


def high_grade(params):
    table = require(params, "table")
    field = require(params, "field")
    min_value = float(require(params, "min_value"))
    limit = int(params.get("limit") or 25)
    db = _open(params)
    try:
        fields_of = _field_cache(db)
        f_all, f_str = fields_of(table)
        if field not in f_all:
            raise CommandError("Field '{}' not in table '{}'. Fields: {}".format(field, table, ", ".join(f_all)))
        if field in f_str:
            raise CommandError("Field '{}' in table '{}' is a string field, not numeric".format(field, table))
        extra = [f for f in ("FROM", "TO") if f in f_all and f not in f_str]
        hits = []
        scanned = 0
        for _ in db:
            if str(db.get_table_name()) != table:
                continue
            scanned += 1
            try:
                value = float(db.get(field))
            except Exception:
                continue
            if value >= min_value:
                hit = {"hole": str(db.get_key()), field: value}
                for f in extra:
                    hit[f] = db.get(f)
                hits.append(hit)
        hits.sort(key=lambda h: h[field], reverse=True)
        return {"db": params["db"], "table": table, "field": field, "min_value": min_value,
                "intervals_scanned": scanned, "matches": len(hits),
                "holes_with_matches": len(set(h["hole"] for h in hits)), "top": hits[:limit]}
    finally:
        db.close()


def _grade_to_vulcan_colour(val):
    """Map copper grade (%) to standard Vulcan palette colour indices (matching bai.scd COBRE)."""
    if val < 0.0:
        return 22  # grey / unassayed
    if val < 0.2:
        return 5   # blue
    if val < 0.4:
        return 6   # cyan
    if val < 0.6:
        return 3   # green
    if val < 0.8:
        return 2   # yellow
    if val < 1.0:
        return 12  # orange
    return 1       # red (high grade >= 1.0%)


def _pick_field(candidates, available):
    upper_map = {f.upper(): f for f in available}
    for cand in candidates:
        if cand in upper_map:
            return upper_map[cand]
    return None


def _desurvey_point(collar_xyz, surveys, depth):
    """Compute 3D world (X, Y, Z) at downhole depth using tangential segments."""
    x, y, z = collar_xyz[0], collar_xyz[1], collar_xyz[2]
    if not surveys or depth <= 0.0:
        return [x, y, z - max(0.0, depth)]
    prev_d, prev_az, prev_dip = surveys[0]
    for i in range(1, len(surveys)):
        cur_d, cur_az, cur_dip = surveys[i]
        seg_end = min(depth, cur_d)
        if seg_end > prev_d:
            ds = seg_end - prev_d
            az_rad = math.radians(prev_az)
            dip_rad = math.radians(prev_dip)
            # In Vulcan drillholes, negative dip points downward (or positive dip downward if >0)
            vz = math.sin(dip_rad) if prev_dip < 0 else -math.sin(dip_rad)
            vh = math.cos(dip_rad)
            x += ds * vh * math.sin(az_rad)
            y += ds * vh * math.cos(az_rad)
            z += ds * vz
        prev_d, prev_az, prev_dip = cur_d, cur_az, cur_dip
        if depth <= cur_d:
            return [x, y, z]
    if depth > prev_d:
        ds = depth - prev_d
        az_rad = math.radians(prev_az)
        dip_rad = math.radians(prev_dip)
        vz = math.sin(dip_rad) if prev_dip < 0 else -math.sin(dip_rad)
        vh = math.cos(dip_rad)
        x += ds * vh * math.sin(az_rad)
        y += ds * vh * math.cos(az_rad)
        z += ds * vz
    return [x, y, z]


def clear_display(params):
    """Remove all temporary 3D drillhole objects from the Vulcan viewport."""
    removed = 0
    while _ACTIVE_TEMP_OBJECTS:
        pair = _ACTIVE_TEMP_OBJECTS.pop()
        try:
            pair[0].remove()
            removed += 1
        except Exception:
            pass
    return {"cleared": removed}


def display_drillholes(params):
    """Visualize drillholes in the 3D Vulcan viewport via temp_object and/or DGD layer."""
    vg = vulcan_gui()
    v = vulcan()
    if params.get("clear_previous", True):
        clear_display({})

    wanted_holes = set(str(h) for h in params["holes"]) if params.get("holes") else None
    max_holes = int(params.get("limit") or 100)
    field = str(params.get("field") or "CUT")
    assay_table = str(params.get("table") or "LEYES")

    # Check if user wants to build 3D grade-coloured segments from the ISIS drillhole DB
    db_name = params.get("db")
    if not db_name:
        dbs = list_files(SUFFIXES)
        if dbs:
            db_name = dbs[0]

    polylines = []
    holes_rendered = []

    if db_name and params.get("mode", "isis") != "dgd":
        db = _open({"db": db_name})
        try:
            fields_of = _field_cache(db)
            tables = [str(t) for t in to_list(db.table_list())]
            collar_table = _pick_field(["COLLARES", "COLLAR", "LOCATION"], tables)
            survey_table = _pick_field(["DIRECCIONES", "SURVEY", "SURVEYS", "DEVIATION"], tables)

            if collar_table:
                c_all, c_str = fields_of(collar_table)
                fx = _pick_field(["X", "EAST", "ESTE", "XCOLLAR"], [f for f in c_all if f not in c_str])
                fy = _pick_field(["Y", "NORTH", "NORTE", "YCOLLAR"], [f for f in c_all if f not in c_str])
                fz = _pick_field(["Z", "RL", "COTA", "ELEV", "ZCOLLAR"], [f for f in c_all if f not in c_str])
            else:
                fx = fy = fz = None

            if survey_table:
                s_all, s_str = fields_of(survey_table)
                s_num = [f for f in s_all if f not in s_str]
                f_depth = _pick_field(["DEPTH", "PROF", "AT", "LENGTH", "MD", "FROM", "DESDE"], s_num)
                f_az = _pick_field(["AZIMUTH", "BEARING", "AZIMUT", "BRG", "AZ"], s_num)
                f_dip = _pick_field(["DIP", "INCLINATION", "INCL", "ANG", "BUZ", "BUZAMIENTO"], s_num)
            else:
                f_depth = f_az = f_dip = None

            if assay_table in tables:
                a_all, a_str = fields_of(assay_table)
                a_num = [f for f in a_all if f not in a_str]
                f_from = _pick_field(["FROM", "DESDE", "DE"], a_num)
                f_to = _pick_field(["TO", "HASTA", "A"], a_num)
                f_val = field if field in a_num else (_pick_field(["CUT", "CU", "GRADE", "LEY"], a_num) or (a_num[0] if a_num else None))
            else:
                f_from = f_to = f_val = None

            if fx and fy and fz and f_from and f_to and f_val:
                all_keys = [str(k) for k in to_list(db.key_list())]
                for key in all_keys:
                    if wanted_holes and key not in wanted_holes:
                        continue
                    if len(holes_rendered) >= max_holes:
                        break
                    db.find_key(key)
                    if str(db.get_key()) != key:
                        continue
                    collar_xyz = None
                    surveys = []
                    intervals = []
                    for _ in range(MAX_RECORDS_PER_HOLE):
                        tname = str(db.get_table_name())
                        if tname == collar_table and collar_xyz is None:
                            try:
                                collar_xyz = [float(db.get(fx)), float(db.get(fy)), float(db.get(fz))]
                            except Exception:
                                pass
                        elif tname == survey_table and f_depth and f_az and f_dip:
                            try:
                                surveys.append((float(db.get(f_depth)), float(db.get(f_az)), float(db.get(f_dip))))
                            except Exception:
                                pass
                        elif tname == assay_table:
                            try:
                                intervals.append((float(db.get(f_from)), float(db.get(f_to)), float(db.get(f_val))))
                            except Exception:
                                pass
                        try:
                            db.next()
                        except Exception:
                            break
                        if str(db.get_key()) != key:
                            break

                    if collar_xyz and intervals:
                        surveys.sort(key=lambda s: s[0])
                        holes_rendered.append(key)
                        for d_from, d_to, val in intervals:
                            if d_to <= d_from:
                                continue
                            p1 = _desurvey_point(collar_xyz, surveys, d_from)
                            p2 = _desurvey_point(collar_xyz, surveys, d_to)
                            line = v.polyline()
                            line.set_coordinates([p1, p2])
                            line.set_connected()
                            line.set_colour(_grade_to_vulcan_colour(val))
                            line.set_name(str(key))
                            polylines.append(line)
        finally:
            db.close()

    # Fallback or explicit DGD mode: read pre-built 3D traces from SONDAJE_LEYES in .dgd.isis
    if not polylines:
        dgd_name = params.get("dgd")
        if not dgd_name:
            dgds = list_files(DGD_SUFFIXES)
            if dgds:
                dgd_name = dgds[0]
        layer_name = str(params.get("layer") or "SONDAJE_LEYES")
        if dgd_name:
            dgd = v.dgd(resolve(dgd_name, DGD_SUFFIXES))
            try:
                if dgd.is_layer(layer_name):
                    lyr = dgd.get_layer(layer_name)
                    for i in range(lyr.num_objects()):
                        obj = lyr.get_object(i)
                        hname = ""
                        try:
                            hname = str(obj.get_name())
                        except Exception:
                            pass
                        if wanted_holes and hname not in wanted_holes:
                            continue
                        if len(holes_rendered) >= max_holes:
                            break
                        polylines.append(obj)
                        if hname and hname not in holes_rendered:
                            holes_rendered.append(hname)
            finally:
                dgd.close()

    # Display in Vulcan 3D viewport via temp_object
    displayed_count = 0
    max_segments = int(params.get("max_segments") or 300)
    for obj in polylines[:max_segments]:
        try:
            tobj = vg.temp_object(obj)
            _ACTIVE_TEMP_OBJECTS.append((tobj, obj))
            displayed_count += 1
        except Exception:
            pass

    # Optionally save to a DGD layer and load if a DGD is currently open in the GUI
    saved_layer = None
    save_to_layer = params.get("save_layer")
    if save_to_layer and polylines:
        dgd_files = list_files(DGD_SUFFIXES)
        if dgd_files:
            dgd_path = resolve(params.get("dgd") or dgd_files[0], DGD_SUFFIXES)
            dgd = v.dgd(dgd_path, "w")
            try:
                lname = str(save_to_layer)
                lyr = v.layer(lname)
                for obj in polylines:
                    lyr.append(obj)
                if not dgd.is_layer(lname):
                    dgd.append(lyr)
                dgd.save_layer(lyr)
                saved_layer = lname
            finally:
                dgd.close()

    return {
        "displayed": displayed_count > 0,
        "holes_count": len(holes_rendered),
        "holes": holes_rendered[:25],
        "segments_rendered": displayed_count,
        "colour_field": field,
        "saved_layer": saved_layer,
    }


ACTIONS = {
    "list_dbs": list_dbs,
    "schema": schema,
    "holes": holes,
    "hole": hole,
    "high_grade": high_grade,
    "display": display_drillholes,
    "clear_display": clear_display,
}


@command("drillholes", timeout=120)
def drillholes(params):
    return run_action(ACTIONS, params)
