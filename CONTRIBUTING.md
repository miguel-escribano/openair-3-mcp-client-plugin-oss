# Contributing to openair-3-mcp-client-plugin-oss

Thanks for considering a contribution. This repo is the **client plugin** half of the openair MCP binomio — see [openair-3-mcp-server-oss](https://github.com/miguel-escribano/openair-3-mcp-server-oss) for the MCP server, and [openair-ai-kit](https://github.com/miguel-escribano/openair-ai-kit) for the landing page.

## Scope

This repo wires an IDE/agent (Claude, Cursor, Codex, VS Code) to the openair MCP server: routing skills, the `openair-agent` persona and guardrails, workflow recipes, and the acceptance test harness. It does not run R or perform calculation — that stays server-side by design (see guardrails O1–O6 in [`agents/openair-agent.md`](agents/openair-agent.md)). Changes that move parsing, date handling, or plotting logic into this repo are likely to be redirected.

## Development setup

No build step — this is a skills/config repo, not a package.

```bash
git clone https://github.com/miguel-escribano/openair-3-mcp-client-plugin-oss
cd openair-3-mcp-client-plugin-oss
cp .mcp.json.example .mcp.json   # gitignored — fill in your own transport/token
```

You'll also need a running server — see the [server README Quick start](https://github.com/miguel-escribano/openair-3-mcp-server-oss#quick-start).

## Adding or editing a skill

1. Skills live under `skills/`. `skills/openair/` is the **router** — it auto-routes based on data modality (CSV on disk, local file + remote MCP, public network, another MCP). Specialist skills (`ingest-local`, `ingest-local-export`, `ingest-network`, `prepare-plot`, `multi-mcp`) and `skills/workflows/` pattern recipes do the actual work.
2. Follow the existing skill folder shape (a `SKILL.md` with clear invocation keywords and a step sequence) — see any existing skill for the pattern.
3. New skills must respect guardrails O1–O6 in `agents/openair-agent.md` — most importantly: never hand-build time-series arrays in chat, never assume a server-disk path exists, and let `prepare_series_for_openair` own alignment.
4. Add a short entry to the skill table in `README.md` → **Using skills** so it's discoverable.

## Testing (acceptance gate)

This repo owns the **golden-path harness** — the authoritative check that a deployed server produces correct plots.

```powershell
$env:OPENAIR_MCP_TOKEN = "…"
python tests/run_series_exercises.py    # 12 checks → tests/output/series/
python tests/run_wind_exercises.py      # 4 checks → tests/output/wind/
```

Pass criteria: 12/12 + 4/4. See [tests/README.md](tests/README.md) for the fixture (`tests/fixtures/felisa_munarriz.json`) and how to regenerate it. This harness needs a **deployed** MCP server with `OPENAIR_MCP_TOKEN` set — it is not run in CI by default.

Server-side `pytest` (in the [server repo](https://github.com/miguel-escribano/openair-3-mcp-server-oss)) covers ingest/prepare units only — run both tiers before proposing a release.

## Submitting changes

1. Open an issue first for a new skill, a change to `agents/openair-agent.md` guardrails, or anything that changes what the harness checks.
2. Keep PRs focused — one skill, one example, one fix per PR where practical.
3. Update `CHANGELOG.md` under `[Unreleased]`.
4. Run the acceptance harness (or explain in the PR why it doesn't apply) before requesting review.
5. If your change assumes a new server tool or contract shape, flag it — the two repos are versioned together per release.

## Reporting bugs / requesting features

Use [GitHub issues](https://github.com/miguel-escribano/openair-3-mcp-server-oss/issues) on the server repo (shared tracker for the binomio), or the [landing repo](https://github.com/miguel-escribano/openair-ai-kit) for cross-cutting feedback.

## Attribution

This project is **not affiliated** with [openair-project](https://github.com/openair-project/openair) maintainers.

## License

By contributing, you agree your contribution is licensed under the [MIT License](LICENSE) that covers this repo.
