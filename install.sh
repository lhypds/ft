#!/usr/bin/env bash
# Run ./setup.sh first. Installs third-party deps into .venv and adds ~/.local/bin/ft
# (wrapper around ft.py using that venv). Does not install this repo as a pip package.
#
#   ./install.sh                 install, then print the settings notice
#   FT_KEY_NOTICE=0 ./install.sh install, staying quiet about settings
#   ./install.sh --key-notice    print the settings notice only, install nothing
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

VENV_DIR=".venv"
LAUNCHER_DIR="$HOME/.local/bin"
LAUNCHER="$LAUNCHER_DIR/ft"
MARKER="# ft-launcher:REPO=$ROOT_DIR"
VENV_PY="$VENV_DIR/bin/python"

# ── settings notice ─────────────────────────────────────────────────────────
# A missing key is not fatal — ft prompts for one on first use and saves the
# answer — so this is a heads-up, not an error. It stays quiet about a key that
# is already there, which is the usual case on an upgrade.
#
# get.sh runs the install with FT_KEY_NOTICE=0 and asks for the notice
# afterwards with --key-notice, so the warning lands after its own summary
# rather than scrolling away above it.

CONFIG_ENV="${XDG_CONFIG_HOME:-$HOME/.config}/ft/.env"

# The first uncommented assignment of $1 in file $2, unquoted and trimmed.
# Commented lines are skipped by the anchor: `# NAME=` does not match.
env_file_value() {
    [ -f "$2" ] || return 0
    sed -n -E "s/^[[:space:]]*$1[[:space:]]*=[[:space:]]*(.*)\$/\1/p" "$2" |
        head -n1 |
        sed -E "s/[[:space:]]+\$//; s/^\"(.*)\"\$/\1/; s/^'(.*)'\$/\1/"
}

# setup.sh seeds the file from .env.example, which assigns every key an empty
# value — so "the line exists" says nothing. Only a non-empty value counts.
key_is_set() {
    if [ -n "${!1:-}" ]; then
        return 0
    fi
    [ -n "$(env_file_value "$1" "$CONFIG_ENV")" ]
}

print_key_notice() {
    if key_is_set OPENAI_API_KEY; then
        cat <<EOF

Settings: $CONFIG_ENV — edit with \`ft config\`
  OPENAI_API_KEY is set.
EOF
        return
    fi

    cat <<EOF

warning: OPENAI_API_KEY is not set — \`ft summarize\` needs it, and so does
\`ft search\` unless BRAVE_API_KEY is set.

  Set it up now:
      ft config
  \`ft\` also asks for the key the first time it needs one and saves it for
  you, so skipping this is fine.

  Settings file: $CONFIG_ENV
  OPENAI_API_KEY  https://platform.openai.com/api-keys
  BRAVE_API_KEY   https://api-dashboard.search.brave.com/app/keys
                  optional — the better backend for \`ft search\`
EOF
}

case "${1:-}" in
    "") ;;
    --key-notice) print_key_notice; exit 0 ;;
    *) echo "error: unknown option: $1" >&2; exit 1 ;;
esac

# ── install ─────────────────────────────────────────────────────────────────

if [ ! -x "$VENV_PY" ]; then
    echo "error: $VENV_DIR is missing or incomplete. Run ./setup.sh first." >&2
    exit 1
fi

if ! "$VENV_PY" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)' 2>/dev/null; then
    echo "error: $VENV_DIR was built with Python < 3.11. Remove it and run ./setup.sh again." >&2
    exit 1
fi

# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

echo "==> Installing dependencies into $VENV_DIR"
pip install -r requirements.txt

echo "==> Installing Playwright's Chromium browser (used to fetch JS-rendered pages)"
python -m playwright install chromium

mkdir -p "$LAUNCHER_DIR"

echo "==> Writing $LAUNCHER"
cat >"$LAUNCHER" <<EOF
#!/usr/bin/env bash
$MARKER
set -euo pipefail
exec "$ROOT_DIR/$VENV_DIR/bin/python" "$ROOT_DIR/ft.py" "\$@"
EOF
chmod +x "$LAUNCHER"

cat <<EOF

Install complete. \`ft\` runs from:
  $LAUNCHER

If the command is not found, add this to ~/.zshrc and open a new terminal:
  export PATH="\$HOME/.local/bin:\$PATH"
EOF

if [ "${FT_KEY_NOTICE:-1}" = "1" ]; then
    print_key_notice
fi
