---
name: prepare-plot
description: >-
  This skill should be used when SeriesV1 data is already loaded and the user wants
  an openair chart via MCP. Triggers: plot, chart, time_plot, calendar_plot,
  time_variation, cor_plot, polar_plot, wind_rose, diurnal, trend. Not for raw file
  ingest (route to ingest-local, ingest-network, or multi-mcp first).
---

# Prepare and plot

**Invoke:** `@prepare-plot` (Cursor/VS Code) · Claude Code: `/openair-3-mcp-client-plugin-oss:prepare-plot` · keywords: *plot, chart, calendar, time_plot, wind rose, polar, diurnal*

Read `../../agents/openair-agent.md` for guardrails.

## Prerequisites

- **openair-3-mcp** connected (see `.mcp.json.example`).
- SeriesV1 JSON from a prior step: `load_series_from_*`, `load_series_from_upload`, `import_*`, or `json_exports` from another MCP.

If data is not loaded yet, route to [`ingest-local`](../ingest-local/SKILL.md), [`ingest-network`](../ingest-network/SKILL.md), or [`multi-mcp`](../multi-mcp/SKILL.md) first.

## Steps

1. **Pollutant time series:** call **`prepare_series_for_openair`** with:
   - `data` = SeriesV1 from ingest, **or** `json_exports` from another MCP
   - `series_name` when multiple pollutant columns (e.g. `PM25`)
   - `granularity`: `hourly` (or as appropriate)
   - `timezone_name`: omit for UTC; set IANA zone for local/diurnal views

2. Call **exactly one** plot tool after prepare.

   Optional **openair 3.2 themes**: set `plot_options.theme` (or `meta.theme`) on the SeriesV1 you pass to the plot tool — presets `default`, `dark`, `modern`, `soft`, `print`. Survives `prepare_series_for_openair` when you chain prepare output → plot.

3. Summarise the PNG — range, timezone, main pattern. Describe visible patterns (trends, peaks, coverage gaps) — see the Describe phase in openair-agent.md.

## Wind / polar exception

If ingest output is **WindSeriesV1** with `ws` and `wd` columns (e.g. from load or import with wind fields):

- Call `polar_plot` or `wind_rose` **directly** — **do not** call `prepare_series_for_openair` first.
- Enforce **O5**: always state the source of wind data before presenting the plot.

Pollutant time-series plots still follow prepare → one plot tool.

## Labels and titles (server-side)

You pass **exact Excel/CSV headers** to ingest/export — the analyst does not need to rename columns in the file for plotting.

On the **server**, R scripts map common regional headers to short openair column ids (`pm10`, `pm25`, `no2`, `o3`, …) for `name.pol` legends. MCP text summaries may use short ids or original SeriesV1 names.

**Plot title** (when the server supports it): `meta.site` · pollutant · date range · `(timezone)`.

### Troubleshooting mangled legends

If a PNG legend shows broken text (e.g. `Part_culas` instead of PM10):

1. Confirm the server is reachable (`health_r`).
2. Pass `site` on export/load for titles.
3. Chain `prepare_series_for_openair` — do not hand-build SeriesV1.
4. Do not pass `built$labels` or portal headers as `name.pol`; the server uses lowercase ids.

Server responsibility: column-id mapping and `auto.text`. Plugin responsibility: correct tool chain and analyst parameters only.

| analyst should supply | Why |
|--------------------|-----|
| `--site` / `site=` on export or load | Title shows station name (e.g. Felisa Munarriz, Pamplona) |
| `timezone` / `timezone_name=Europe/Madrid` | Axis labels and title timezone |
| `series_name` on prepare when multiple columns | Which series is primary; legends still show all prepared series |

Do not pass mangled internal column names to the user — describe pollutants in plain language or use the MCP tool summary text.

## Plot routing (hints only)

| User intent (rough) | MCP tool |
|---------------------|----------|
| First look / coverage overview | `summary_plot` |
| Trend over time | `time_plot` |
| Calendar / daily pattern | `calendar_plot` |
| Diurnal / weekday | `time_variation` |
| Correlation matrix | `cor_plot` (≥2 series in prepare) |
| Value distribution | `dist_plot` | Optional `plot_options.dist_method`: histogram, density, freqpoly, ecdf |
| Model vs observation numbers | `mod_stats` (model series first, obs second) |
| Polar / wind | `polar_plot`, `wind_rose` (WindSeriesV1 with ws/wd — no prepare) |

Full catalog: [examples/plot-catalog.md](../../examples/plot-catalog.md).

**Unsure which openair function fits?** Call `openair_docs` or `openair_function_help("timePlot")` — the [openair book](https://openair-project.github.io/book/) is the authoritative manual. Do not teach openair methodology in chat.

## Errors

On failure: `health_r` → report error → stop. No manual substitutes.
