---
name: ingest-network
description: >-
  This skill should be used when importing air quality data from live public monitoring
  networks via openair MCP. Triggers: import AURN, import europe, import ukaq, public
  network, monitoring station, site code, MY1. Not for local CSV/Excel files on disk.
---

# Ingest network — public data

**Invoke:** `@ingest-network` (Cursor/VS Code) · Claude Code: `/openair-3-mcp-client-plugin-oss:ingest-network` · keywords: *AURN, import europe, UK AQ, public network, site code*

Read `../../agents/openair-agent.md` for guardrails and the analyst contract.

## When to use

- User wants data from UK AURN, UK wider networks, or European monitoring networks.
- Not for local CSV/Excel files — use [`ingest-local`](../ingest-local/SKILL.md).

## Steps

1. Choose the import tool (ask user for region, site code, pollutant, dates if missing):
   - UK AURN → `import_aurn`
   - UK wider → `import_ukaq`
   - Europe → `import_europe`
   - Metadata / site lookup → `import_meta` (no dates required; supports `code`, `site`, `site_type`, `meta_pollutant`, `year`, `lat`/`lng`, `max_dist`, `max_n`, `all_meta` — see server `ImportParamsV1`)

2. Pass site code, pollutant, and date range per import tool schema (`import_meta` is metadata-only). **Do not shrink the user's date range** without asking.

3. For plotting: [`prepare-plot`](../prepare-plot/SKILL.md) — `prepare_series_for_openair` → one plot tool.

   **Chain MCP only:** pass the **full** `import_*` structured result as `data` to `prepare_series_for_openair` in the next tool call. Do not re-read import JSON from disk, terminal, or VS Code `workspaceStorage` paths.

4. Cite data source and date range in the reply.

## VS Code / large date ranges

Quarter-long hourly imports (~2k+ rows, ~100 KB SeriesV1) may spill tool output to IDE session files. Copilot then loops on PowerShell/scripts instead of chaining MCP.

| Situation | Approach |
|-----------|----------|
| Chat smoke test | 1–2 weeks of hourly data |
| Full quarter in chat | Prompt: *MCP tools only — no terminal or scripts — chain import → prepare → plot using the previous tool result* |
| Long range, reliable | Run [examples/aurn-time-plot.md](../../examples/aurn-time-plot.md) via `tests/mcp_remote.py` pattern, or shorten the asked range |

Do not create ad-hoc scripts in the repo to workaround IDE payload limits.

## Pattern recipe

Full walkthrough: [`public-network-plot`](../workflows/public-network-plot/SKILL.md) · [examples/aurn-time-plot.md](../../examples/aurn-time-plot.md)

## Notes

- Network imports may be slow; wait for MCP result.
- If import fails, report the MCP error; do not invent substitute data.

## Errors

On failure: `health_r` → report error → stop. Do not invent substitute data.
