#!/usr/bin/env bash
# Remove local build outputs and Python bytecode caches (.venv and .git are left intact).
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

echo "==> Removing dist/, build/, release/, and *.egg-info"
rm -rf dist build release
# Editable installs or local builds may leave these at the repo root.
shopt -s nullglob
rm -rf ./*.egg-info

echo "==> Removing __pycache__ (except under .venv and .git)"
while IFS= read -r -d '' dir; do
    rm -rf "$dir"
done < <(find . -type d -name "__pycache__" ! -path "./.venv/*" ! -path "./.git/*" -print0)

echo "==> Removing downloaded .txt and .summary.md files (except README.md, requirements.txt, .venv, .git)"
while IFS= read -r -d '' file; do
    rm -f "$file"
done < <(find . -type f \( -name "*.txt" -o -name "*.md" \) ! -path "./.venv/*" ! -path "./.git/*" ! -name "README.md" ! -name "requirements.txt" -print0)

echo "Clear complete."
