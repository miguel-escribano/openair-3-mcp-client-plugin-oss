# Linode / Anne — deploy automation

## What already auto-deploys from **this** repo

One **GitHub webhook** on `miguel-escribano/openair-3-mcp-client-plugin-oss` → **anne-app-deployer** (`/anne-deployer/webhook`, port 4001 on the Linode).

On push to `main`, the deployer:

1. `git pull` → `/root/anne/openair-3-mcp-client-plugin-oss`
2. `deploy/install-hermes-plugin.sh` → Hermes plugin **`openair-client`** (skills)
3. `inbiot-anne-hermes/deploy/sync-anne-profile.sh` → SOUL + profile `config.yaml` (MCP URLs unchanged)

You do **not** need a GitHub Action in this repo for Anne unless you want CI checks before the webhook runs.

## What does **not** deploy from this repo

| Target | Repo | Deployer |
|--------|------|----------|
| MCP server `:3007` | `openair-3-mcp-server-oss` | **mcp-deployer** (separate webhook) |

Anne’s Hermes profile already points at `http://127.0.0.1:3007/mcp`; when the **server** repo deploys, tools update without touching this client repo.

## One repo, several deploy targets?

Yes, in general:

- **Several webhooks** on the same GitHub repo (each URL = one deployer).
- **One webhook handler** that runs multiple steps (your deployers already do pull + install + sync).
- **GitHub Actions** that call several HTTP deploy endpoints with secrets (duplicate of webhooks if you already use them).

This binomio intentionally uses **two repos → two webhooks**:

- Server push → MCP only (fast, no Hermes restart).
- Client push → Hermes skills + profile sync (no MCP Python redeploy).

### Optional: server push also refreshes Hermes

Not configured today. If you want it:

1. **Light:** second webhook on `openair-3-mcp-server-oss` to anne-app-deployer with a new route that only runs `sync-anne-profile.sh` (no skill reinstall), or
2. **Heavy:** post-hook in mcp-deployer that shells out to the sync script after `openair-3-mcp-server-oss` deploy.

Usually unnecessary: new MCP tools appear without skill changes; bump **this** repo when `SKILL.md` or routing changes.

## Manual check on Linode

```bash
git -C /root/anne/openair-3-mcp-client-plugin-oss log -1 --oneline
ls /root/.hermes/profiles/anne/plugins/openair-client/skills/
tail -20 /root/anne/app-deployer/deploy.log
```