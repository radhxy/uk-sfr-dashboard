#!/usr/bin/env bash
# Deploys this folder to Vercel as a static site. Needs VERCEL_TOKEN in the environment.
set -euo pipefail
cd "$(dirname "$0")"
: "${VERCEL_TOKEN:?Set VERCEL_TOKEN (vercel.com > Account Settings > Tokens)}"
python3 -I build.py
npx --yes vercel@39.3.0 deploy --prod --yes --token "$VERCEL_TOKEN" --name uk-sfr-market-monitor
