"""Drillhole interval QA/QC validation and descriptive statistics (Python 3.5 compatible)."""
import math

from ..common import require
from ._isis import open_db, prepare_interval_table


def _scan_hole_qaqc(hole_id, intervals, field, min_valid, max_valid, tolerance):
    """Validate sorted intervals for one drillhole and return anomaly dicts."""
    anomalies = []
    intervals.sort(key=lambda item: (item[0], item[1]))
    prev_to = None
    for from_v, to_v, grade_v in intervals:
        if from_v < 0.0 or from_v >= to_v:
            anomalies.append({
                "hole": hole_id,
                "issue_type": "inverted_interval",
                "from_depth": round(from_v, 6),
                "to_depth": round(to_v, 6),
                "value": grade_v,
                "detail": "Invalid interval: from ({}) >= to ({}) or negative".format(from_v, to_v),
            })
        if field is not None and grade_v is not None:
            if (min_valid is not None and grade_v < min_valid) or (max_valid is not None and grade_v > max_valid):
                anomalies.append({
                    "hole": hole_id,
                    "issue_type": "out_of_range",
                    "from_depth": round(from_v, 6),
                    "to_depth": round(to_v, 6),
                    "value": grade_v,
                    "detail": "Field '{}' value {} outside [{}, {}]".format(field, grade_v, min_valid, max_valid),
                })
        if prev_to is not None:
            if from_v < prev_to - tolerance:
                anomalies.append({
                    "hole": hole_id,
                    "issue_type": "overlap",
                    "from_depth": round(from_v, 6),
                    "to_depth": round(to_v, 6),
                    "value": grade_v,
                    "detail": "Overlap of {:.4f}m with previous interval ending at {:.4f}m".format(prev_to - from_v, prev_to),
                })
            elif from_v > prev_to + tolerance:
                anomalies.append({
                    "hole": hole_id,
                    "issue_type": "gap",
                    "from_depth": round(from_v, 6),
                    "to_depth": round(to_v, 6),
                    "value": grade_v,
                    "detail": "Sampling gap of {:.4f}m after previous interval ending at {:.4f}m".format(from_v - prev_to, prev_to),
                })
        if prev_to is None or to_v > prev_to:
            prev_to = to_v
    return anomalies


def _percentile(sorted_vals, pct):
    """Linear-interpolated percentile over a non-empty sorted list."""
    if len(sorted_vals) == 1:
        return sorted_vals[0]
    k = (len(sorted_vals) - 1) * (pct / 100.0)
    f = int(math.floor(k))
    c = int(math.ceil(k))
    if f == c:
        return sorted_vals[f]
    return sorted_vals[f] + (sorted_vals[c] - sorted_vals[f]) * (k - f)


def qaqc_validation(params, open_fn=open_db):
    """Scan drillhole intervals for overlaps, gaps, inverted intervals, and grade outliers."""
    requested_table = params.get("table")
    field = params.get("field")
    tolerance = float(params.get("tolerance") if params.get("tolerance") is not None else 0.01)
    min_valid = float(params["min_valid"]) if params.get("min_valid") is not None else None
    max_valid = float(params["max_valid"]) if params.get("max_valid") is not None else None
    limit = int(params.get("limit") or 100)

    db = open_fn(params)
    try:
        table, from_col, to_col = prepare_interval_table(db, requested_table, field=field, require_from_to=True)

        by_hole = {}
        intervals_checked = 0
        for _ in db:
            if str(db.get_table_name()) != table:
                continue
            try:
                from_v = float(db.get(from_col))
                to_v = float(db.get(to_col))
            except Exception:
                continue
            grade_v = None
            if field is not None:
                try:
                    grade_v = float(db.get(field))
                except Exception:
                    grade_v = None
            hole_id = str(db.get_key())
            by_hole.setdefault(hole_id, []).append((from_v, to_v, grade_v))
            intervals_checked += 1

        all_anomalies = []
        summary = {"overlap": 0, "gap": 0, "inverted_interval": 0, "out_of_range": 0}
        for hole_id in sorted(by_hole.keys()):
            hole_issues = _scan_hole_qaqc(hole_id, by_hole[hole_id], field, min_valid, max_valid, tolerance)
            for issue in hole_issues:
                summary[issue["issue_type"]] = summary.get(issue["issue_type"], 0) + 1
                all_anomalies.append(issue)

        return {
            "db": params["db"],
            "table": table,
            "field": field,
            "holes_checked": len(by_hole),
            "intervals_checked": intervals_checked,
            "total_anomalies": len(all_anomalies),
            "summary": summary,
            "anomalies": all_anomalies[:limit],
        }
    finally:
        db.close()


def stats(params, open_fn=open_db):
    """Compute descriptive and length-weighted statistics for a numeric drillhole field."""
    field = require(params, "field")
    db = open_fn(params)
    try:
        table, from_col, to_col = prepare_interval_table(db, params.get("table"), field=field, require_from_to=False)

        values = []
        weighted_sum = 0.0
        total_length = 0.0
        scanned = 0
        missing = 0

        for _ in db:
            if str(db.get_table_name()) != table:
                continue
            scanned += 1
            try:
                val = float(db.get(field))
            except Exception:
                missing += 1
                continue
            if math.isnan(val) or math.isinf(val):
                missing += 1
                continue
            values.append(val)
            if from_col and to_col:
                try:
                    length = float(db.get(to_col)) - float(db.get(from_col))
                    if length > 0.0:
                        weighted_sum += val * length
                        total_length += length
                except Exception:
                    pass

        n = len(values)
        if n > 0:
            values.sort()
            mean_v = sum(values) / float(n)
            var_v = sum((v - mean_v) ** 2 for v in values) / float(n)
        else:
            mean_v = 0.0
            var_v = 0.0

        return {
            "db": params["db"],
            "table": table,
            "field": field,
            "intervals_scanned": scanned,
            "valid_count": n,
            "missing_count": missing,
            "min": round(values[0], 6) if n > 0 else None,
            "max": round(values[-1], 6) if n > 0 else None,
            "mean": round(mean_v, 6) if n > 0 else None,
            "weighted_mean": round(weighted_sum / total_length, 6) if (n > 0 and total_length > 0.0) else None,
            "std_dev": round(math.sqrt(var_v), 6) if n > 0 else None,
            "p50": round(_percentile(values, 50.0), 6) if n > 0 else None,
            "p90": round(_percentile(values, 90.0), 6) if n > 0 else None,
            "total_length": round(total_length, 3),
        }
    finally:
        db.close()
