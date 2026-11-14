#!/usr/bin/env bash
# Idempotent updater for video-lora-kb. See UPDATING.md. Flags: --dry-run --no-civitai --no-push --allow-dirty --max-minutes N --pages N
# Last stdout line is a single JSON summary. Logs go to stderr.
set -u
cd "$(dirname "$0")/.."
unset GITHUB_TOKEN GH_TOKEN GH_ENTERPRISE_TOKEN GITHUB_ENTERPRISE_TOKEN
exec python3 scripts/update.py "$@"
