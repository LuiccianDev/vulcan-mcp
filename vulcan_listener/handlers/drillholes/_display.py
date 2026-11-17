"""3D desurveying and Envisage viewport visualization for drillholes (Python 3.5 compatible)."""
import math

from ..common import list_files, resolve, to_list, vulcan, vulcan_gui
from ._isis import MAX_RECORDS_PER_HOLE, SUFFIXES, field_cache, open_db, pick_field

DGD_SUFFIXES = (".dgd.isis",)

# Preserved across hot-reload so SWIG does not orphan active 3D temp_objects
_ACTIVE_TEMP_OBJECTS = globals().setdefault("_ACTIVE_TEMP_OBJECTS", [])


def grade_to_vulcan_colour(val):
    """Map copper grade (%) to standard Vulcan palette colour indices (matching bai.scd COBRE)."""
    if val < 0.0:
        return 22
    if val < 0.2:
        return 5
    if val < 0.4:
        return 6
    if val < 0.6:
        return 3
    if val < 0.8:
        return 2
    if val < 1.0:
        return 12
    return 1


def desurvey_point(collar_xyz, surveys, depth):
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


def display_drillholes(params, open_fn=open_db):
    """Visualize drillholes in the 3D Vulcan viewport via temp_object and/or DGD layer."""
    vg = vulcan_gui()
    v = vulcan()
    if params.get("clear_previous", True):
        clear_display({})

    wanted_holes = set(str(h) for h in params["holes"]) if params.get("holes") else None
    max_holes = int(params.get("limit") or 100)
    field = str(params.get("field") or "CUT")
    assay_table = str(params.get("table") or "LEYES")

    db_name = params.get("db")
    if not db_name:
        dbs = list_files(SUFFIXES)
        if dbs:
            db_name = dbs[0]

    polylines = []
    holes_rendered = []

    if db_name and params.get("mode", "isis") != "dgd":
        db = open_fn({"db": db_name})
        try:
            fields_of = field_cache(db)
            tables = [str(t) for t in to_list(db.table_list())]
            collar_table = pick_field(["COLLARES", "COLLAR", "LOCATION"], tables)
            survey_table = pick_field(["DIRECCIONES", "SURVEY", "SURVEYS", "DEVIATION"], tables)

            if collar_table:
                c_all, c_str = fields_of(collar_table)
                c_num = [f for f in c_all if f not in c_str]
                fx = pick_field(["X", "EAST", "ESTE", "XCOLLAR"], c_num)
                fy = pick_field(["Y", "NORTH", "NORTE", "YCOLLAR"], c_num)
                fz = pick_field(["Z", "RL", "COTA", "ELEV", "ZCOLLAR"], c_num)
            else:
                fx = fy = fz = None

            if survey_table:
                s_all, s_str = fields_of(survey_table)
                s_num = [f for f in s_all if f not in s_str]
                f_depth = pick_field(["DEPTH", "PROF", "AT", "LENGTH", "MD", "FROM", "DESDE"], s_num)
                f_az = pick_field(["AZIMUTH", "BEARING", "AZIMUT", "BRG", "AZ"], s_num)
                f_dip = pick_field(["DIP", "INCLINATION", "INCL", "ANG", "BUZ", "BUZAMIENTO"], s_num)
            else:
                f_depth = f_az = f_dip = None

            if assay_table in tables:
                a_all, a_str = fields_of(assay_table)
                a_num = [f for f in a_all if f not in a_str]
                f_from = pick_field(["FROM", "DESDE", "DE"], a_num)
                f_to = pick_field(["TO", "HASTA", "A"], a_num)
                f_val = field if field in a_num else (pick_field(["CUT", "CU", "GRADE", "LEY"], a_num) or (a_num[0] if a_num else None))
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
                            p1 = desurvey_point(collar_xyz, surveys, d_from)
                            p2 = desurvey_point(collar_xyz, surveys, d_to)
                            line = v.polyline()
                            line.set_coordinates([p1, p2])
                            line.set_connected()
                            line.set_colour(grade_to_vulcan_colour(val))
                            line.set_name(str(key))
                            polylines.append(line)
        finally:
            db.close()

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

    displayed_count = 0
    max_segments = int(params.get("max_segments") or 300)
    for obj in polylines[:max_segments]:
        try:
            tobj = vg.temp_object(obj)
            _ACTIVE_TEMP_OBJECTS.append((tobj, obj))
            displayed_count += 1
        except Exception:
            pass

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
