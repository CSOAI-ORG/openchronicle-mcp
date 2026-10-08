# MIGRATION_NOTE - MCP 2026-07-28 wire - class `header-add` (SDK pin BLOCKED)

**Date:** 2026-10-08 - **Lane:** M4 MCP-migration (header-add wave 2, batch 5) - **Branch:** `mcp-2026-wire-header-add`
**Runbook:** `MCP_2026_WIRE_MIGRATION_PLAN_2026-10-07.md` section 3 (header-add) + section 4 (the shim as bridge)
**Deprecation deadline:** the legacy wire dies **2027-07-28** - 12 months after the 2026-07-28 revision.

## 1. Transport reality

Entry `src/openchronicle/interfaces/mcp/__main__.py` runs `server.run(transport=config.transport)`
(stdio or FastMCP's own streamable-HTTP); the server object is built by
`src/openchronicle/interfaces/mcp/server.py::create_server()` and mounted by the FastAPI host.
There is no root `server.py`.

## 2. Class note (honesty)

The census row for this repo is `header-add`, but a local audit of the reconstructed default
branch reads **`pre-2025-06 / full`** - the `protocol-2025-03-26` + `initialize-handshake`
signals come from `tests/test_unified_asgi.py` and `scripts/smoke_test.py` (client-side handshake
fixtures), not from the serving path. The handshake-removal half of class `full` (those fixtures)
is **not** addressed on this branch and stays a follow-up.

## 3. What changed in this branch - and what was tried and reverted

1. **`mcp2026_shim.py` vendored at the repo root** (Python stdlib, 665 lines, zero third-party
   deps). It applies where plan section 4 says it does - one instance per ingress (reverse proxy /
   gateway) - not inside the process. The scanner excludes it by design (`SELF_FILES`), so it
   contributes no signals below.
2. **This PR is documentation + shim only.** Two runbook steps were applied, CI was run, the
   result was red, and both were reverted:
   * `pyproject.toml`: `"mcp>=1.0.0"` (optional extra `[mcp]`) -> `"mcp>=2.0.0"` - **reverted**;
   * `server.py`: `from mcp.server.fastmcp import FastMCP` ->
     `from mcp.server.mcpserver import MCPServer as FastMCP` - **reverted**.

   Receipt: https://github.com/CSOAI-ORG/openchronicle-mcp/actions/runs/37722454245/job/113133007633
   - `ubuntu-latest` / `macos-latest` / `windows-latest` / `lint + format + types` all failed:
   `TypeError: MCPServer.__init__() got an unexpected keyword argument 'host'`
   (**29 failed, 41 errors, 316 passed**).
   `create_server()` passes `host=`, `port=`, `streamable_http_path=` and `transport_security=`;
   `MCPServer.__init__` in mcp 2.x accepts none of them, so the pin alone breaks construction at
   runtime (`py_compile` was green - the failure is at first server build).

   A red branch on the only serving path is worse than a documented blocker, so the pin and the
   rename are not shipped. No packaging include list exists here either (setuptools
   `packages.find` under `src/`), so the shim is in-tree only and is **not** claimed to ship in
   the wheel.

**To unblock class `header-add`:** adapt `create_server()` to the mcp 2.x `MCPServer` constructor
(drop or relocate `host` / `port` / `streamable_http_path` / `transport_security`), keep the
repo's own suite green, then apply `mcp>=2.0.0` + the rename. That is an SDK-API adaptation,
outside the header-add runbook, and it gets its own PR (Art. 21).

## 4. Verify

```bash
PYTHONPATH= /opt/homebrew/bin/python3.11 ~/clawd/mcp_wire_audit.py audit --local openchronicle-mcp
```

| state | era | migration |
|---|---|---|
| before (default branch) | pre-2025-06 | full |
| **after (this branch)** | **pre-2025-06** | **full** |
| control (migration-note block removed) | pre-2025-06 | full |

All three rows are identical on purpose: with the pin reverted this branch adds a vendored shim
and documentation only, and the note block that did exist sat in
`src/openchronicle/interfaces/mcp/__main__.py` - below the scanner's depth cap - so it never
moved these rows either. **After-rows are note-text-driven until post-merge re-audit**, and here
they are simply unchanged: **this PR is not evidence that `openchronicle-mcp` speaks 2026-07-28.**

## 5. Follow-ups (not in this branch)

* mcp 2.x API adaptation of `create_server()` -> then the pin + rename (see section 3).
* The handshake fixtures in `tests/` / `scripts/` that produce the `full` class reading.
* Static declaration surfaces (`.well-known/*.json`, `docs/`, `README.md`) still declare an older
  wire - follow-ups, not silent-edited (Art. 21: a declaration change gets its own commit).
* A live probe per plan section 6.5 is owed before anyone quotes `migration: none`.

Plan: `MCP_2026_WIRE_MIGRATION_PLAN_2026-10-07.md` - deadline 2027-07-28 - measurement, not certification.
