"""ISIS drillhole database (.dhd.isis) access and bilingual query helpers (Python 3.5 compatible)."""

from ..common import CommandError, list_files, page, require, resolve, to_list, vulcan

SUFFIXES = (".dhd.isis",)
MAX_RECORDS_PER_HOLE = 5000


def open_db(params):
    path = resolve(require(params, "db"), SUFFIXES)
    v = vulcan()
    try:
        return v.isisdb(path, "r", "")
    except Exception:
        return v.isisdb(path)


def read_record(db, fields, string_fields):
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


def field_cache(db):
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


def pick_field(candidates, available):
    upper_map = {f.upper(): f for f in available}
    for cand in candidates:
        if cand in upper_map:
            return upper_map[cand]
    return None


def resolve_interval_table(db, requested_table):
    """Resolve an interval table name, supporting bilingual defaults."""
    tables = [str(t) for t in to_list(db.table_list())]
    if requested_table:
        if requested_table not in tables:
            raise CommandError("Table '{}' not found. Available: {}".format(requested_table, ", ".join(tables)))
        return requested_table
    upper_map = {t.upper(): t for t in tables}
    for cand in ("LEYES", "ASSAYS", "ASSAY", "MUESTRAS", "SAMPLES", "LITOLOGIA", "LITHOLOGY"):
        if cand in upper_map:
            return upper_map[cand]
    raise CommandError("No default interval table found; specify 'table'. Available: {}".format(", ".join(tables)))


def prepare_interval_table(db, requested_table, field=None, require_from_to=True):
    """Resolve interval table, validate optional numeric field, and pick FROM/TO columns."""
    table = resolve_interval_table(db, requested_table)
    fields_of = field_cache(db)
    f_all, f_str = fields_of(table)
    from_col = pick_field(("FROM", "DESDE", "DEPTH_FROM"), f_all)
    to_col = pick_field(("TO", "HASTA", "DEPTH_TO"), f_all)
    if require_from_to and (not from_col or not to_col):
        raise CommandError("Table '{}' does not contain FROM/DESDE and TO/HASTA fields".format(table))
    if field is not None:
        if field not in f_all:
            raise CommandError("Field '{}' not in table '{}'. Fields: {}".format(field, table, ", ".join(f_all)))
        if field in f_str:
            raise CommandError("Field '{}' in table '{}' is a string field, not numeric".format(field, table))
    return table, from_col, to_col


def list_dbs(params):
    return {"drillhole_dbs": list_files(SUFFIXES)}


def schema(params, open_fn=open_db):
    db = open_fn(params)
    try:
        tables = [str(t) for t in to_list(db.table_list())]
        fields_of = field_cache(db)
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


def holes(params, open_fn=open_db):
    db = open_fn(params)
    try:
        result = page([str(k) for k in to_list(db.key_list())], params, default_limit=50)
        result["db"] = params["db"]
        return result
    finally:
        db.close()


def hole(params, open_fn=open_db):
    key = str(require(params, "hole"))
    wanted_table = params.get("table")
    limit = int(params.get("limit") or 200)
    db = open_fn(params)
    try:
        db.find_key(key)
        if str(db.get_key()) != key:
            raise CommandError("Hole '{}' not found in {}".format(key, params["db"]))
        fields_of = field_cache(db)
        tables = {}
        for _ in range(MAX_RECORDS_PER_HOLE):
            table = str(db.get_table_name())
            if wanted_table is None or table == wanted_table:
                rows = tables.setdefault(table, [])
                if len(rows) < limit:
                    f_all, f_str = fields_of(table)
                    rows.append(read_record(db, f_all, f_str))
            try:
                db.next()
            except Exception:
                break
            if str(db.get_key()) != key:
                break
        return {"db": params["db"], "hole": key, "tables": tables, "limit_per_table": limit}
    finally:
        db.close()


def high_grade(params, open_fn=open_db):
    table = require(params, "table")
    field = require(params, "field")
    min_value = float(require(params, "min_value"))
    limit = int(params.get("limit") or 25)
    db = open_fn(params)
    try:
        fields_of = field_cache(db)
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
        return {
            "db": params["db"],
            "table": table,
            "field": field,
            "min_value": min_value,
            "intervals_scanned": scanned,
            "matches": len(hits),
            "holes_with_matches": len(set(h["hole"] for h in hits)),
            "top": hits[:limit],
        }
    finally:
        db.close()
