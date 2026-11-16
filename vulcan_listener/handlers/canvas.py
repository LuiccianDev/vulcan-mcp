"""Canvas, viewport screenshot (token-optimised JPEG), and GUI macro commands."""
import base64
import io

from .common import CommandError, command, require, run_action, vulcan_gui


def _find_vulcan_bbox():
    """Find Vulcan / Envisage window bounding box using ctypes (native Windows API)."""
    try:
        import ctypes
        import ctypes.wintypes
        user32 = ctypes.windll.user32
    except Exception:
        return None

    matches = []

    def enum_cb(hwnd, _):
        if user32.IsWindowVisible(hwnd) and not user32.IsIconic(hwnd):
            length = user32.GetWindowTextLengthW(hwnd)
            if length > 0:
                buff = ctypes.create_unicode_buffer(length + 1)
                user32.GetWindowTextW(hwnd, buff, length + 1)
                title = buff.value.lower()
                # Match main Vulcan workspace or Envisage OpenGL window
                if "vulcan" in title or "envisage" in title:
                    rect = ctypes.wintypes.RECT()
                    user32.GetWindowRect(hwnd, ctypes.byref(rect))
                    width = rect.right - rect.left
                    height = rect.bottom - rect.top
                    # Filter out small toolbars or non-main dialogs
                    if width > 400 and height > 300 and rect.left >= 0 and rect.top >= 0:
                        matches.append((rect.left, rect.top, rect.right, rect.bottom))
        return True

    try:
        WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.wintypes.HWND, ctypes.wintypes.LPARAM)
        user32.EnumWindows(WNDENUMPROC(enum_cb), 0)
    except Exception:
        return None

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
