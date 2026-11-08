"""Execute arbitrary Python inside Vulcan's live session (Python 3.5 compatible)."""
import sys
import traceback

try:
    from io import StringIO
except ImportError:
    from StringIO import StringIO

from .common import command, project_dir, require


@command("execute_code", timeout=60)
def execute_code(params):
    code = require(params, "code")
    old_out, old_err = sys.stdout, sys.stderr
    buf_out, buf_err = StringIO(), StringIO()
    sys.stdout, sys.stderr = buf_out, buf_err

    scope = {"__name__": "__vulcan_mcp__", "project_dir": project_dir()}
    try:
        import maptek.vulcan as v
        import maptek.vulcan_gui as vg
        scope["vulcan"] = v
        scope["vulcan_gui"] = vg
    except ImportError:
        pass

    try:
        exec(code, scope, scope)
        return {
            "executed": True,
            "stdout": buf_out.getvalue(),
            "stderr": buf_err.getvalue(),
            "result": scope.get("result"),
        }
    except Exception:
        return {
            "executed": False,
            "stdout": buf_out.getvalue(),
            "stderr": buf_err.getvalue(),
            "traceback": traceback.format_exc(),
        }
    finally:
        sys.stdout, sys.stderr = old_out, old_err
