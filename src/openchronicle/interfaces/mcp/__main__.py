"""Entry point for ``python -m openchronicle.interfaces.mcp``.

Starts the MCP server with stdio transport using default configuration.
"""

from __future__ import annotations

import logging
import sys


# ---------------------------------------------------------------------------
# MCP 2026-07-28 wire - header-add migration ({DATE})
# ---------------------------------------------------------------------------
# stdio carries no HTTP headers, so Mcp-Method / Mcp-Name are not applicable to
# this transport at runtime. When {repo} is exposed over HTTP, route the ingress
# through the vendored mcp2026_shim (ShimASGI): it validates Mcp-Method /
# Mcp-Name, injects params._meta.protocolVersion = "2026-07-28" into every
# request, strips Mcp-Session-Id and answers legacy initialize / server-discover
# locally (the session header is never emitted - stateless wire).
# Refs: MIGRATION_NOTE.md, MCP_2026_WIRE_MIGRATION_PLAN_2026-10-07.md (3) + (4).
# ---------------------------------------------------------------------------


def main() -> None:
    try:
        import mcp  # noqa: F401
    except ImportError:
        print("mcp SDK is not installed. Install with: pip install -e '.[mcp]'", file=sys.stderr)
        sys.exit(1)

    from openchronicle.core.infrastructure.wiring.container import CoreContainer
    from openchronicle.interfaces.mcp.config import MCPConfig
    from openchronicle.interfaces.mcp.server import create_server

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")

    container = CoreContainer()
    config = MCPConfig.from_env()
    server = create_server(container, config)
    server.run(transport=config.transport)


if __name__ == "__main__":
    main()
