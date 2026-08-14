#!/usr/bin/env bash
# Preparation for ./install.sh: create .venv with Python >= 3.11, upgrade pip,
# and seed the settings file in ~/.config/ft.
# Does not install project dependencies or the global ft command — run ./install.sh after this.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

VENV_DIR=".venv"

PY=""
for cmd in "${PYTHON:-}" python3.13 python3.12 python3.11 python3; do
    [ -z "$cmd" ] && continue
    command -v "$cmd" >/dev/null 2>&1 || continue
    if "$cmd" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)' 2>/dev/null; then
        PY="$cmd"
        break
    fi
done

if [ -z "$PY" ]; then
    echo "error: need Python >= 3.11 for this project." >&2
    echo "  PYTHON=/opt/homebrew/bin/python3.12 ./setup.sh" >&2
    exit 1
fi

if [ ! -d "$VENV_DIR" ]; then
    echo "==> Creating virtualenv at $VENV_DIR ($PY)"
    "$PY" -m venv "$VENV_DIR"
else
    echo "==> Reusing existing virtualenv at $VENV_DIR"
fi

# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

echo "==> Upgrading pip"
pip install --upgrade pip

# Settings live in ~/.config/ft/.env so the installed `ft` finds its keys from
# any directory. A .env in this checkout still takes precedence, for development.
CONFIG_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/ft"
CONFIG_ENV="$CONFIG_DIR/.env"
if [ -f "$CONFIG_ENV" ]; then
    echo "==> Keeping existing $CONFIG_ENV"
else
    mkdir -p "$CONFIG_DIR"
    if [ -f ".env.example" ]; then
        cp ".env.example" "$CONFIG_ENV"
    else
        : >"$CONFIG_ENV"
    fi
    chmod 600 "$CONFIG_ENV"
    echo "==> Created $CONFIG_ENV"
fi

cat <<EOF

Setup complete — ready for ./install.sh

Next step (installs Python deps + global \`ft\` command):
    ./install.sh

API keys go in $CONFIG_ENV
(OPENAI_API_KEY is required; BRAVE_API_KEY is optional). \`ft\` asks for a
missing key the first time it needs one.

Optional: activate the venv only (no global \`ft\` yet):
    source $VENV_DIR/bin/activate
EOF
