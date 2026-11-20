# Changelog

All notable changes to this project are documented here. Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versioning follows [SemVer](https://semver.org/).

This repo is versioned together with [openair-3-mcp-server-oss](https://github.com/miguel-escribano/openair-3-mcp-server-oss) — pair matching releases.

## [Unreleased]

## [0.2.6] - 2026-11-20

### Changed

- Pairs with server **v0.2.6** (`time_variation` display labels + title fix; `plot_options.theme` validation; optional `plot_options.dendrogram` for `cor_plot`).

## [0.2.5] - 2026-11-20

### Changed

- Pairs with server **v0.2.5** (`time_variation` drops monthly panel when span under 60 days).

## [0.2.4] - 2026-11-20

### Changed

- Release pairs with server **v0.2.4** (`time_plot` ylab + display `name.pol` from series units). Skills unchanged; require MCP host **≥ v0.2.4** for labelled Y axes on `time_plot`.

## [0.2.2] - 2026-11-20

### Changed

- Document Linode Anne auto-deploy (`deploy/LINODE.md`). Pair with server **≥ v0.2.3** on the MCP host (Anne uses loopback `:3007`; skills unchanged vs 0.2.1 except deploy docs).

## [0.2.1] - 2026-11-20

### Changed

- Pairs with server **v0.2.1**: `dist_plot`, openair 3.2 `import_meta` filters, optional `plot_options.theme` on prepare → plot chain.

## [0.2.0] - 2026-11-20

### Changed

- Release pairs with server **v0.2.0** and **CRAN openair 3.2.0** on the MCP host. Re-run `tests/run_series_exercises.py` after server R upgrade.

### Added

- `CITATION.cff` — machine-readable citation metadata (GitHub "Cite this repository").
- `CONTRIBUTING.md` — dev setup, skill-adding guide, testing gate, PR process.
- `reproductions/` — Marylebone Road NOx polar plot reproduction (AURN + ERA5 wind).

## [0.1.0] - 2026-06-30

Initial public release of the client plugin.

### Added

- `openair-agent` persona and guardrails O1–O6 (`agents/openair-agent.md`) — analyst contract, routing rules, no client-side date parsing or array building.
- Router skill (`skills/openair/`) — auto-routes by data modality to specialist skills.
- Manual skills — `ingest-local`, `ingest-local-export`, `ingest-network`, `prepare-plot`, `multi-mcp`.
- Workflow recipes (`skills/workflows/`) — regional Excel, public-network plot, remote upload.
- Acceptance test harness — `tests/run_series_exercises.py` (12 checks) + `tests/run_wind_exercises.py` (4 checks) against a deployed MCP server.
- Felisa `WindSeriesV1` golden fixture (`tests/fixtures/felisa_munarriz.json`) — real Open-Meteo ERA5 wind data, Pamplona station.
- `.mcp.json.example` (Claude/Cursor/Codex) and `.vscode/mcp.json` example (VS Code) — local stdio, local HTTP, and remote HTTP + token setups.
- Example walkthroughs — AURN time plot, CSV calendar plot, regional Excel (Spain), VS Code remote-MCP smoke test, plot catalog.
- Multi-IDE plugin manifests — `.claude-plugin/`, `.codex-plugin/`, `.cursor-plugin/`, `.github/copilot-instructions.md`.

