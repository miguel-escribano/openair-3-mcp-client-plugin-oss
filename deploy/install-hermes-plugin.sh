#!/usr/bin/env bash
# Install or refresh the portable Hermes plugin (Anne Linode / local Hermes).
set -euo pipefail
HERMES="${HERMES_BIN:-/root/.local/bin/hermes}"
REPO="${OPENAIR_PLUGIN_REPO:-miguel-escribano/openair-3-mcp-client-plugin-oss}"
export PATH="/root/.local/bin:$PATH"

"$HERMES" plugins install "$REPO" --force --enable --yes-deps
echo "✓ Hermes plugin openair-client installed and enabled from $REPO"
