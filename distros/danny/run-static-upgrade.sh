#!/bin/bash
set -euo pipefail

if [ $# -lt 2 ]; then
  echo "Usage: $0 <project_dir> <project_name> [description]"
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DESCRIPTION="${3:-}"

python3 "$SCRIPT_DIR/run_static_upgrade.py" "$1" \
  --project-name "$2" \
  --description "$DESCRIPTION"
