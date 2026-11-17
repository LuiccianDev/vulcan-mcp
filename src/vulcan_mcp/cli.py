"""Command-line interface for Vulcan MCP."""

import argparse
import json
import sys

from vulcan_mcp import __version__
from vulcan_mcp.client import VulcanMCPClient
from vulcan_mcp.models.responses import VulcanPingResponse
from vulcan_mcp.protocol import (
    generate_and_save_token,
    get_auth_token,
    get_host,
    get_port,
)


def build_cli_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser for Vulcan MCP."""
    parser = argparse.ArgumentParser(
        prog="luiccian-vulcan-mcp",
        description="Model Context Protocol (MCP) server for Maptek Vulcan 12 Desktop.",
    )
    parser.add_argument(
        "--version",
        action="store_true",
        help="Print the MCP server package version and exit.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Run a live TCP health check against the Maptek Vulcan listener and exit.",
    )
    parser.add_argument(
        "--generate-token",
        action="store_true",
        help="Generate a shared HMAC auth token in ~/.vulcan_mcp/token and print client config.",
    )
    return parser


def run_health_check() -> int:
    """Run a live TCP ping against the Maptek Vulcan listener and print JSON status."""
    host = get_host()
    port = get_port()
    token_configured = bool(get_auth_token())
    client = VulcanMCPClient(host=host, port=port, timeout=3.0, max_retries=0)
    try:
        ping_raw = client.send_command("system", {"action": "ping"})
        ping = VulcanPingResponse.model_validate(ping_raw)
    except Exception as exc:
        print(
            json.dumps(
                {
                    "ok": False,
                    "mcp_version": __version__,
                    "host": host,
                    "port": port,
                    "token_configured": token_configured,
                    "error": str(exc),
                },
                indent=2,
            ),
            file=sys.stderr,
        )
        return 1

    listener_ver = ping.listener_version
    report = {
        "ok": True,
        "mcp_version": __version__,
        "listener_version": listener_ver,
        "protocol_version": ping.protocol_version,
        "version_match": listener_ver == __version__ if listener_ver else None,
        "host": host,
        "port": port,
        "token_configured": token_configured,
        "vulcan_python": ping.python,
        "project_dir": ping.project_dir,
        "domains": ping.domains,
    }
    print(json.dumps(report, indent=2))
    if listener_ver and listener_ver != __version__:
        print(
            f"Warning: MCP version ({__version__}) != listener version ({listener_ver}).",
            file=sys.stderr,
        )
    return 0


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint; imports FastMCP lazily only when launching the server."""
    parser = build_cli_parser()
    args = parser.parse_args(argv)
    if args.version:
        print(f"luiccian-vulcan-mcp {__version__}")
        return 0
    if args.generate_token:
        token, token_path = generate_and_save_token()
        print(f"Generated shared HMAC token and saved to: {token_path}")
        print(f"Token: {token}")
        print("\nOptional explicit AI client env block:")
        print(json.dumps({"env": {"VULCAN_MCP_TOKEN": token}}, indent=2))
        return 0
    if args.check:
        return run_health_check()

    from vulcan_mcp.server import run_server

    run_server()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
