#!/usr/bin/env python3
"""Reproduce the openair book's canonical Marylebone Road NOx polar plot,
through the MCP pipeline instead of a local R session.

Source example (David Carslaw's openair book, Polar plots chapter):
    library(openair)
    polarPlot(mydata, pollutant = "nox")
https://openair-project.github.io/book/sections/directional-analysis/polar-plots.html

The book's `mydata` is a bundled historical snapshot of Marylebone Road
(AURN site MY1) data, 1998-01-01 to 2005-06-23 (hourly), with wind already
merged in. This script does not use that snapshot — it builds the same
inputs live:

  - NOx: `import_aurn` (MY1) — the AURN roadside record.
  - Wind: MY1 does not report wind on-site (`import_aurn` for MY1 has no
    ws/wd — verified live: co, nox, no2, no, o3, so2, pm10, pm2.5 only).
    Wind speed/direction come from Open-Meteo's ERA5 archive
    (archive-api.open-meteo.com, free, no key) at MY1's coordinates
    (51.5225, -0.1546 — from this kit's own `import_meta` tool). This
    mirrors how the book's own `mydata` was assembled (merged from more
    than one source) and the pattern this kit's `multi-mcp` skill supports
    for pairing a pollutant source with an external wind source.

Expect the same qualitative pattern the book describes — highest NOx with
wind from the south-west, evidence of street-canyon recirculation, since
the monitor sits on the south side of the street — not numerically
identical figures, since the underlying year differs from 1998-2005.

Usage:
    export OPENAIR_MCP_TOKEN=...
    python reproductions/reproduce_marylebone_polarplot.py [YEAR]

YEAR defaults to 2019 (last complete pre-pandemic year — 2020/2021 traffic
volumes are not representative of the "normal" street-canyon pattern the
book describes).
"""
from __future__ import annotations

import base64
import json
import sys
from pathlib import Path

import httpx

REPRO_DIR = Path(__file__).resolve().parent
TESTS_DIR = REPRO_DIR.parent / "tests"
OUT_DIR = REPRO_DIR / "output"
sys.path.insert(0, str(TESTS_DIR))

from mcp_remote import McpClient, extract_tool_payload  # noqa: E402

SITE = "MY1"  # AURN: London Marylebone Road
SITE_LAT, SITE_LON = 51.5225, -0.1546  # from this kit's import_meta tool
POLLUTANT = "nox"
BOOK_URL = "https://openair-project.github.io/book/sections/directional-analysis/polar-plots.html"
OPEN_METEO_URL = "https://archive-api.open-meteo.com/v1/archive"


def fetch_open_meteo_wind(start_date: str, end_date: str) -> dict[str, tuple[float, float]]:
    """Hour -> (wind_speed_ms, wind_direction_deg) lookup, keyed by 'YYYY-MM-DDTHH:00:00Z'."""
    r = httpx.get(
        OPEN_METEO_URL,
        params={
            "latitude": SITE_LAT,
            "longitude": SITE_LON,
            "start_date": start_date,
            "end_date": end_date,
            "hourly": "wind_speed_10m,wind_direction_10m",
            "wind_speed_unit": "ms",
            "timezone": "UTC",
        },
        timeout=60,
    )
    r.raise_for_status()
    hourly = r.json()["hourly"]
    lookup = {}
    for ts, ws, wd in zip(hourly["time"], hourly["wind_speed_10m"], hourly["wind_direction_10m"]):
        if ws is None or wd is None:
            continue
        lookup[f"{ts}:00Z"] = (ws, wd)
    return lookup


def _find(series: list[dict], name: str) -> dict | None:
    for col in series:
        if col["name"].lower() == name.lower():
            return col
    return None


def main() -> int:
    year = int(sys.argv[1]) if len(sys.argv) > 1 else 2019
    start_date, end_date = f"{year}-01-01", f"{year}-12-31"
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"1. import_aurn(site='{SITE}', {start_date}..{end_date}) — pollutants (MY1 has no on-site wind)")
    mcp = McpClient()
    try:
        mcp.start()
        print(f"   MCP session OK — {mcp.url}\n")

        raw = extract_tool_payload(
            mcp.call_tool(
                "import_aurn",
                {"params": {"site": SITE, "start_date": start_date, "end_date": end_date}},
            )
        )
        if raw.get("error"):
            print(f"   FAILED: {raw['error']}", file=sys.stderr)
            return 1
        nox_col = _find(raw["series"], POLLUTANT)
        if nox_col is None:
            print(f"   FAILED: no '{POLLUTANT}' for {SITE} in {year}.", file=sys.stderr)
            return 1
        print(f"   OK — {len(raw['timestamps'])} hourly timestamps, series: {[c['name'] for c in raw['series']]}")

        print(f"\n2. Open-Meteo ERA5 wind — lat={SITE_LAT}, lon={SITE_LON}, {start_date}..{end_date}")
        wind_lookup = fetch_open_meteo_wind(start_date, end_date)
        ws_vals, wd_vals, matched = [], [], 0
        for ts in raw["timestamps"]:
            hit = wind_lookup.get(ts)
            if hit:
                matched += 1
            ws_vals.append(hit[0] if hit else None)
            wd_vals.append(hit[1] if hit else None)
        print(f"   OK — {matched}/{len(raw['timestamps'])} hours matched to ERA5 wind")

        merged = {
            "timestamps": raw["timestamps"],
            "series": [
                nox_col,
                {"name": "ws", "unit": "m/s", "values": ws_vals},
                {"name": "wd", "unit": "degrees", "values": wd_vals},
            ],
            "meta": {**(raw.get("meta") or {}), "wind_source": "open-meteo-era5"},
        }

        print("\n3. prepare_series_for_openair — hourly, UTC, DST-safe alignment")
        prepared = extract_tool_payload(
            mcp.call_tool(
                "prepare_series_for_openair",
                {"data": merged, "granularity": "hourly", "timezone_name": "UTC"},
            )
        )
        if prepared.get("error"):
            print(f"   FAILED: {prepared['error']}", file=sys.stderr)
            return 1
        print(f"   OK — coverage {prepared['coverage_ratio']:.1%}, {prepared['actual_points']}/{prepared['expected_points']} hours")

        nox_p = _find(prepared["series"], POLLUTANT)
        ws_p = _find(prepared["series"], "ws")
        wd_p = _find(prepared["series"], "wd")
        wind_payload = {
            "timestamps": prepared["timestamps"],
            "series": [nox_p],
            "ws": ws_p["values"],
            "wd": wd_p["values"],
            "meta": prepared.get("meta"),
        }

        print(f"\n4. polar_plot(pollutant='{POLLUTANT}') — same call as the book's polarPlot(mydata, pollutant='nox')")
        result = mcp.call_tool("polar_plot", {"data": wind_payload})
        png_path = OUT_DIR / f"marylebone_{SITE.lower()}_{POLLUTANT}_polarplot_{year}.png"
        for block in result.get("content") or []:
            if block.get("type") == "image" and block.get("data"):
                png_path.write_bytes(base64.b64decode(block["data"]))
                print(f"   OK -> {png_path}")
                break
        else:
            print(f"   FAILED: no image in response — {json.dumps(result)[:500]}", file=sys.stderr)
            return 1

    finally:
        mcp.close()

    print(
        f"\nCompare against the openair book's own figure:\n  {BOOK_URL}\n"
        "Expect the same qualitative pattern: highest NOx with wind from the south-west "
        "(street-canyon recirculation — the monitor is on the south side of the street)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
