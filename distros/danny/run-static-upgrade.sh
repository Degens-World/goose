#!/bin/bash
set -euo pipefail

if [ $# -lt 2 ]; then
  echo "Usage: $0 <project_dir> <project_name>"
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

goose run \
  --recipe "$REPO_ROOT/workflow_recipes/danny_static_site_upgrade/recipe.yaml" \
  --params "project_dir=$1,project_name=$2"

