#!/usr/bin/env python3
"""Autonomous Version Bumper & Multi-File Synchronizer for Vulcan MCP.

Synchronizes version across:
  1. pyproject.toml ([project] version = "...")
  2. src/vulcan_mcp/__init__.py (__version__ = "...")
  3. .agents/plugins/vulcan-mcp/plugin.json ("version": "...")
  4. uv.lock (version = "..." for luiccian-vulcan-mcp)
  5. CHANGELOG.md (converts ## [Unreleased] to ## [X.Y.Z] - YYYY-MM-DD)

Usage:
  python scripts/bump_version.py patch
  python scripts/bump_version.py minor
  python scripts/bump_version.py major
  python scripts/bump_version.py 0.4.0
  python scripts/bump_version.py patch --dry-run
"""

from __future__ import annotations

import argparse
import datetime
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

PYPROJECT_FILE = ROOT / "pyproject.toml"
INIT_FILE = ROOT / "src" / "vulcan_mcp" / "__init__.py"
UV_LOCK_FILE = ROOT / "uv.lock"
CHANGELOG_FILE = ROOT / "CHANGELOG.md"
TEST_FILE = ROOT / "tests" / "test_vulcan_mcp.py"


def get_current_version() -> str:
    content = PYPROJECT_FILE.read_text(encoding="utf-8")
    m = re.search(r'(?m)^version\s*=\s*["\']([^"\']+)["\']', content)
    if not m:
        raise ValueError("Could not find version in pyproject.toml")
    return m.group(1)


def calculate_next_version(current: str, bump_type: str) -> str:
    m = re.match(r"^(\d+)\.(\d+)\.(\d+)(.*)$", current)
    if not m:
        raise ValueError("Current version '{}' does not match SemVer MAJOR.MINOR.PATCH".format(current))

    major, minor, patch = int(m.group(1)), int(m.group(2)), int(m.group(3))

    if bump_type.lower() == "patch":
        return "{}.{}.{}".format(major, minor, patch + 1)
    elif bump_type.lower() == "minor":
        return "{}.{}.0".format(major, minor + 1)
    elif bump_type.lower() == "major":
        return "{}.0.0".format(major + 1)
    elif re.match(r"^\d+\.\d+\.\d+", bump_type):
        return bump_type
    else:
        raise ValueError("Invalid bump argument '{}'. Expected patch, minor, major, or explicit X.Y.Z".format(bump_type))


def update_pyproject(new_version: str, dry_run: bool = False) -> None:
    text = PYPROJECT_FILE.read_text(encoding="utf-8")
    new_text = re.sub(
        r'(?m)^version\s*=\s*["\'][^"\']+["\']',
        'version = "{}"'.format(new_version),
        text,
        count=1,
    )
    if not dry_run:
        PYPROJECT_FILE.write_text(new_text, encoding="utf-8")


def update_init_py(new_version: str, dry_run: bool = False) -> None:
    text = INIT_FILE.read_text(encoding="utf-8")
    new_text = re.sub(
        r'(?m)^__version__\s*=\s*["\'][^"\']+["\']',
        '__version__ = "{}"'.format(new_version),
        text,
        count=1,
    )
    if not dry_run:
        INIT_FILE.write_text(new_text, encoding="utf-8")




def update_uv_lock(new_version: str, dry_run: bool = False) -> None:
    if not UV_LOCK_FILE.exists():
        return
    text = UV_LOCK_FILE.read_text(encoding="utf-8")
    pattern = r'(\[\[package\]\]\s*\nname\s*=\s*"luiccian-vulcan-mcp"\s*\nversion\s*=\s*")[^"]+(")'
    new_text = re.sub(pattern, r'\g<1>' + new_version + r'\g<2>', text, count=1)
    if not dry_run:
        UV_LOCK_FILE.write_text(new_text, encoding="utf-8")


def update_test_py(new_version: str, dry_run: bool = False) -> None:
    if not TEST_FILE.exists():
        return
    text = TEST_FILE.read_text(encoding="utf-8")
    new_text = re.sub(
        r'(?m)assert pkg_version == "[^"]+"',
        'assert pkg_version == "{}"'.format(new_version),
        text,
        count=1,
    )
    if not dry_run:
        TEST_FILE.write_text(new_text, encoding="utf-8")


def update_changelog(new_version: str, dry_run: bool = False) -> None:
    if not CHANGELOG_FILE.exists():
        return
    text = CHANGELOG_FILE.read_text(encoding="utf-8")
    today = datetime.date.today().isoformat()
    release_header = "## [{}] - {}".format(new_version, today)

    if release_header in text:
        print("[CHANGELOG] Section for {} already exists; skipping header injection.".format(new_version))
        return

    unreleased_pattern = r"(## \[Unreleased\]\s*\n)"
    replacement = r"\g<1>\n---\n\n" + release_header + "\n"
    new_text = re.sub(unreleased_pattern, replacement, text, count=1)

    if not dry_run:
        CHANGELOG_FILE.write_text(new_text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Synchronize version and CHANGELOG across Vulcan MCP files.")
    parser.add_argument("bump", help="Bump type (patch, minor, major) or explicit version (e.g. 0.4.0)")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without modifying files")
    parser.add_argument("--no-changelog", action="store_true", help="Skip updating CHANGELOG.md")

    args = parser.parse_args()

    current = get_current_version()
    next_ver = calculate_next_version(current, args.bump)

    prefix = "[DRY-RUN] " if args.dry_run else ""
    print("{}Bumping version: {} -> {}".format(prefix, current, next_ver))

    update_pyproject(next_ver, dry_run=args.dry_run)
    print("  [x] pyproject.toml -> {}".format(next_ver))

    update_init_py(next_ver, dry_run=args.dry_run)
    print("  [x] src/vulcan_mcp/__init__.py -> {}".format(next_ver))


    update_uv_lock(next_ver, dry_run=args.dry_run)
    print("  [x] uv.lock -> {}".format(next_ver))

    update_test_py(next_ver, dry_run=args.dry_run)
    print("  [x] tests/test_vulcan_mcp.py -> {}".format(next_ver))

    if not args.no_changelog:
        update_changelog(next_ver, dry_run=args.dry_run)
        print("  [x] CHANGELOG.md (injected ## [{}] - {})".format(next_ver, datetime.date.today().isoformat()))


    print("\n{}Successfully synchronized all 5 version targets to {}!".format(prefix, next_ver))
    if not args.dry_run:
        print("Next steps:")
        print("  1. git commit -am 'chore(release): bump version to {}'".format(next_ver))
        print("  2. git tag -a v{} -m 'Release v{}'".format(next_ver, next_ver))
        print("  3. git push origin master --tags")
    return 0


if __name__ == "__main__":
    sys.exit(main())
