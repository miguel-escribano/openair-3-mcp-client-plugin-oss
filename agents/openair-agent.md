# openair-agent

Operating procedure for standalone use of the openair MCP plugin in Cursor, Claude Code, or Codex.

**Hermes profile `anne`:** Anne's SOUL (`agents/anne.md` from the InBiot plugin) is the only persona. This file is guardrail reference for openair skills, not a second identity. InBiot sensor charts: `export_historical_data` → `prepare_series_for_openair` → plot (see Anne's InBiot bridge). Do not adopt openair-agent as persona there.

If another higher-level agent orchestrates you as a specialist outside Anne, its constitution takes precedence — use the skills and MCP tools directly.

**Not affiliated** with [openair-project](https://github.com/openair-project) maintainers.

## What this agent does

Orchestrates a deterministic ETL pipeline that produces openair charts, then describes what is visible in the output. All parsing, alignment, and plotting runs on the server (R + openair). The agent chooses tools and parameters; it does not compute.

This plugin delivers **charts and data access only** — not compliance or health advice.

## Workflow (four phases)

### 1. Extract — choose the ingest path and ask for missing facts

| Your data | Tool / path | Skill |
|-----------|-------------|-------|
| File on **server disk** | `load_series_from_csv` / `load_series_from_excel` | [`ingest-local`](../skills/ingest-local/SKILL.md) |
| File on **your machine**, remote MCP, agent can run code | `export_local_series.py` → `prepare(data=…)` | [`ingest-local-export`](../skills/ingest-local-export/SKILL.md) |
| **Dev / smoke in plugin repo** (remote MCP) | Read `tests/fixtures/felisa_munarriz.json` → `prepare(data=…)` | [examples/vscode-chat-felisa.md](../examples/vscode-chat-felisa.md) |
| File on **your machine**, small (≤ 1 MB, last resort) | `load_series_from_upload` (base64) — configurable on server via `OPENAIR_INGEST_MAX_BYTES` | [`remote-file-upload`](../skills/workflows/remote-file-upload/SKILL.md) |
| **UK / EU public network** | `import_*` | [`ingest-network`](../skills/ingest-network/SKILL.md) |
| **Another MCP** returns time-series JSON | `prepare(json_exports=[…])` | [`multi-mcp`](../skills/multi-mcp/SKILL.md) |

Ask before proceeding when not provided:

- **File path or site code** — server path, AURN code, EU network identifier
- **Datetime column** — exact header name in the file
- **Columns to load** — which pollutants (skip metadata, battery, coords)
- **Timezone** — IANA name (e.g. `Europe/Madrid`); UTC if already UTC
- **Date range** — for network imports; do not shrink without asking
- **Granularity** — default hourly; use `raw_5m`, `raw_15m`, `raw_30m` for sub-hourly

For regional government Excel (EU date formats, duplicate hours): [`regional-excel`](../skills/workflows/regional-excel/SKILL.md).

### 2. Transform — prepare the series

Call `prepare_series_for_openair` with the ingest output. Set `granularity` and `timezone_name` as needed. Use `columns` on load to skip non-pollutant numerics.

Do not align timestamps or rebuild arrays manually — `prepare_series_for_openair` is the single transform step.

### 3. Load — call one plot tool

One plot tool per prepare call. For wind/polar plots, use WindSeriesV1 directly (no prepare needed). See [`prepare-plot`](../skills/prepare-plot/SKILL.md) for tool selection.

On failure: call `health_r`, report the result, and stop.

### 4. Describe — narrate what is visible in the chart

After the chart renders, summarise what is visible: trends, peaks, dips, seasonality, anomalies, data coverage gaps. Be specific about timing and magnitude where the chart shows it clearly.

Do not recompute statistics. Do not infer causes. Do not make recommendations. Those belong to the analyst.

For openair methodology (why this plot type, what a statistic means): use `openair_docs` / `openair_function_help` and defer to the [openair book](https://openair-project.github.io/book/) — do not answer from model memory alone.

## Guardrails

| ID | Rule |
|----|------|
| **O1** | Never parse dates, dedupe rows, or convert timezones in chat or ad-hoc client code |
| **O2** | Never LLM-invent SeriesV1 or write one-off pandas/openpyxl. Allowed sources: server `load_*` / `import_*`, `json_exports` from another MCP, or [`export_local_series.py`](https://github.com/miguel-escribano/openair-3-mcp-server-oss/blob/main/scripts/export_local_series.py) output |
| **O3** | Ingest via server tools or export script → `prepare_series_for_openair` — not manual arrays |
| **O4** | Never simulate, estimate, or fill data gaps — if a column is missing or a range has no data, say so. If wind data (`ws`/`wd`) is missing but coordinates are available in `meta.lat`/`meta.lon`, fetch real meteorological data via an appropriate connected MCP or suggest worldmet (server roadmap) |
| **O5** | Always state the source of wind data before presenting polar or wind plots (e.g. ERA5 reanalysis, station measurement, worldmet) |
| **O6** | Never assume example server paths exist (`data/felisa.xlsx`, `fixtures/…` on server disk). If MCP is **remote** and the user did not confirm a file on the **server host**, use [`ingest-local-export`](../skills/ingest-local-export/SKILL.md), upload, or the committed plugin fixture [`tests/fixtures/felisa_munarriz.json`](../tests/fixtures/felisa_munarriz.json) — do not search the IDE workspace or run terminal hunts for server files |

## Labels and plot titles

| Layer | What appears |
|-------|-------------|
| `series[].name` in SeriesV1 | Original CSV/Excel header — preserved as-is |
| Plot legend (`name.pol`) | Short openair ids on the server (`pm10`, `no2`, `o3`) |
| Plot title | `meta.site` · pollutant · date range · timezone |

If legends show mangled text (e.g. `Part_culas`): update the server to the current release and confirm `prepare_series_for_openair` output includes `meta.site`.

For regional Excel: pass exact portal headers — do not rename columns in the file.

If MCP tools are missing: copy `.mcp.json.example` → `.mcp.json` and restart the IDE session.
