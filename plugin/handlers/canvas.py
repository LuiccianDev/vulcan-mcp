"""Canvas, viewport screenshot (token-optimised JPEG), and GUI macro commands."""
import base64
import io

from .common import CommandError, command, require, run_action, vulcan_gui


def _find_vulcan_bbox():
    try:
        import win32gui
    except ImportError:
        return None
    matches = []

    def enum_cb(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd) or ""
            if "vulcan" in title.lower():
                rect = win32gui.GetWindowRect(hwnd)
                if (rect[2] - rect[0]) > 200 and (rect[3] - rect[1]) > 200:
                    matches.append(rect)

    win32gui.EnumWindows(enum_cb, None)
    return matches[0] if matches else None


def screenshot(params):
    """Capture the Vulcan window and compress to small JPEG to save LLM tokens."""
    try:
        from PIL import ImageGrab
    except ImportError:
        raise CommandError("PIL.ImageGrab is not available in Vulcan's Python")

    max_width = int(params.get("max_width") or 800)
    quality = int(params.get("quality") or 70)
    bbox = _find_vulcan_bbox()
    img = ImageGrab.grab(bbox=bbox) if bbox else ImageGrab.grab()
    w, h = img.size
    if w > max_width:
        new_h = max(1, int(h * (float(max_width) / float(w))))
        img = img.resize((max_width, new_h))
    img = img.convert("RGB")
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=quality, optimize=True)
    raw = buf.getvalue()
    return {
        "mime_type": "image/jpeg",
        "width": img.size[0],
        "height": img.size[1],
        "bytes": len(raw),
        "data": base64.b64encode(raw).decode("ascii"),
    }


def run_macro(params):
    cmd = require(params, "macro")
    vg = vulcan_gui()
    ok = vg.workbench_macro(str(cmd))
    return {"executed": bool(ok), "macro": cmd}


def report_message(params):
    msg = require(params, "text")
    vg = vulcan_gui()
    if hasattr(vg, "print_message"):
        vg.print_message(str(msg) + "\n")
    return {"printed": True, "text": msg}


ACTIONS = {"screenshot": screenshot, "macro": run_macro, "report": report_message}


@command("canvas", timeout=20)
def canvas(params):
    return run_action(ACTIONS, params)
