# Remote MCP test harness

**Acceptance gate** for the openair binomio — proves deployed MCP → prepare → R → PNG (legends, encoding, 12 series exercises + 4 wind). Server `pytest` is pre-deploy only; this harness is authoritative.

End-to-end checks against a **deployed** openair server (pilot or localhost HTTP). Not run in CI by default — needs R on the server host and `OPENAIR_MCP_TOKEN`.

## Where things live

| What | Repo |
|------|------|
| MCP server, R scripts, pytest, tiny CSV ingest samples | [`openair-3-mcp-server-oss`](../../openair-3-mcp-server-oss) |
| **This harness + golden JSON fixture** | **this plugin repo** (`tests/`) |
| Disposable IDE sandboxes (e.g. `C:\code\TESTING-*`) | **not** source of truth — delete freely |

The two OSS repos live in `agent/stack/` (`openair-3-mcp-server-oss` and this client), not under `engagements/openair-oss/` (that directory holds `disemination`, `mcp-deployer`, and `openair-mcp-oss`). Open the plugin folder in VS Code to wire `.vscode/mcp.json`.

**Not in this repo:** `data/felisa.xlsx` and other example server-disk paths from docs — those are placeholders unless you upload files to the MCP host yourself.

## Fixture

**One file:** `fixtures/felisa_munarriz.json` — **WindSeriesV1** (Felisa pollutants + ERA5 `ws`/`wd`, lat/lon in `meta`).

| Harness | Uses |
|---------|------|
| `run_series_exercises.py` | Same file, pollutant fields only → `prepare_series_for_openair` → plots |
| `run_wind_exercises.py` | Full file → wind plot tools (no prepare) |

Felisa station: Pamplona, 42.80686 / -1.64405. Wind is **real** — Open-Meteo ERA5 reanalysis, 10 m, 2026-05-31 to 2026-06-28 UTC. To regenerate:

```bash
cd ../../openair-3-mcp-server-oss
python scripts/inject_real_wind.py
```

## Run

```bash
pip install httpx
export OPENAIR_MCP_TOKEN=…
export OPENAIR_MCP_URL=https://your-host/…/sse   # optional

# from plugin repo root:
python tests/run_series_exercises.py    # 12 plots/stats → tests/output/series/
python tests/run_wind_exercises.py      # 4 wind plots → tests/output/wind/
```

PowerShell:

```powershell
$env:OPENAIR_MCP_TOKEN = "…"
$env:OPENAIR_MCP_URL = "https://…/sse"
python tests/run_series_exercises.py
python tests/run_wind_exercises.py
```

**Pass criteria:** 12/12 + 4/4 OK. Visual check: `tests/output/series/02_time_plot_all.png` — legends show NO₂ / PM₁₀ / O₃ (not mojibake); `12_summary_plot_all.png` — completeness bars present.

## VS Code Copilot (same data, chat)

Do not prompt Copilot to find Excel on the server. Use [examples/vscode-chat-felisa.md](../examples/vscode-chat-felisa.md) — reads this fixture, chains MCP prepare → plot.

PNG output is gitignored under `tests/output/`.

