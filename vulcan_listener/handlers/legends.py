"""Envisage colour scheme commands (.scd)."""
import re
import shutil

from .common import CommandError, command, list_files, require, resolve, run_action

SUFFIXES = (".scd",)
PALETTES = {
    "high_contrast_mining": ["10", "120", "95", "2", "4", "45", "1"],
    "classic_blue_to_red": ["144", "125", "107", "88", "70", "51", "33"],
    "traffic_light": ["2", "9", "4", "45", "1"],
    "hot_metal": ["240", "140", "70", "51", "33", "1", "6"],
}


def _parse_scd(text):
    schemes = {}
    for def_match in re.finditer(r"BEGIN\$DEF\s+(\S+)(.*?)END\$DEF\s+\1", text, re.DOTALL):
        scheme_type = def_match.group(1)
        tables = {}
        for tab_match in re.finditer(r"BEGIN\$TAB\s+(\S+)(.*?)END\$TAB\s+\1", def_match.group(2), re.DOTALL):
            tab_name = tab_match.group(1)
            tokens = [m.group(1) for m in re.finditer(r"'([^']*)'", tab_match.group(2))]
            tables[tab_name] = tokens
        schemes[scheme_type] = tables
    return schemes


def list_legends(params):
    return {"legends": list_files(SUFFIXES), "presets": sorted(PALETTES)}


def inspect_legend(params):
    path = resolve(require(params, "scd"), SUFFIXES)
    with open(path, "r", encoding="latin1") as fh:
        text = fh.read()
    return {"scd": params["scd"], "schemes": _parse_scd(text)}


def update_table(params):
    path = resolve(require(params, "scd"), SUFFIXES)
    scheme = require(params, "scheme")
    table = require(params, "table")
    preset = params.get("preset")
    colours = params.get("colours")
    if preset:
        if preset not in PALETTES:
            raise CommandError("Unknown preset '{}'. Available: {}".format(preset, ", ".join(sorted(PALETTES))))
        colours = PALETTES[preset]
    if not colours:
        raise CommandError("Provide either 'preset' or 'colours' list")

    with open(path, "r", encoding="latin1") as fh:
        text = fh.read()

    bak_path = path + ".bak"
    shutil.copyfile(path, bak_path)

    def_pattern = re.compile(r"(BEGIN\$DEF\s+" + re.escape(scheme) + r"\b)(.*?)(END\$DEF\s+" + re.escape(scheme) + r"\b)", re.DOTALL)
    def_match = def_pattern.search(text)
    if not def_match:
        raise CommandError("Scheme '{}' not found in {}".format(scheme, params["scd"]))

    tab_pattern = re.compile(r"(BEGIN\$TAB\s+" + re.escape(table) + r"\b)(.*?)(END\$TAB\s+" + re.escape(table) + r"\b)", re.DOTALL)
    tab_match = tab_pattern.search(def_match.group(2))
    if not tab_match:
        raise CommandError("Table '{}' not found under '{}'".format(table, scheme))

    body = tab_match.group(2)
    lines = body.splitlines(True)
    # In numeric tables, triplets of ('colour', 'from', 'to') precede the trailing mode ('GELT')
    quoted_indices = [i for i, line in enumerate(lines) if re.match(r"^\s*'[^']*'\s*$", line)]
    header_skip = 0
    if scheme == "DRILL_COLOUR" and len(quoted_indices) >= 5:
        header_skip = 5
    elif scheme in ("SAMPLES_COLOUR",) and len(quoted_indices) >= 1:
        header_skip = 1

    triplet_Indices = quoted_indices[header_skip:]
    if triplet_Indices and re.search(r"'(GELT|GTLE|GELE)'", lines[triplet_Indices[-1]]):
        triplet_Indices = triplet_Indices[:-1]

    colour_line_positions = triplet_Indices[0::3]
    updated = 0
    for idx, line_pos in enumerate(colour_line_positions):
        new_c = str(colours[min(idx, len(colours) - 1)])
        lines[line_pos] = re.sub(r"'[^']*'", "'{}'".format(new_c), lines[line_pos], count=1)
        updated += 1

    new_tab = tab_match.group(1) + "".join(lines) + tab_match.group(3)
    new_def = def_match.group(1) + def_match.group(2)[:tab_match.start()] + new_tab + def_match.group(2)[tab_match.end():] + def_match.group(3)
    new_text = text[:def_match.start()] + new_def + text[def_match.end():]

    with open(path, "w", encoding="latin1") as fh:
        fh.write(new_text)

    return {"updated": True, "scd": params["scd"], "scheme": scheme, "table": table,
            "intervals_updated": updated, "backup": bak_path}


def restore_backup(params):
    path = resolve(require(params, "scd"), SUFFIXES)
    bak_path = path + ".bak"
    shutil.copyfile(bak_path, path)
    return {"restored": True, "scd": params["scd"], "from": bak_path}


ACTIONS = {"list": list_legends, "inspect": inspect_legend, "update": update_table, "restore": restore_backup}


@command("legend", timeout=15)
def legend(params):
    return run_action(ACTIONS, params)
