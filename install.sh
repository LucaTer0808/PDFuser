#!/usr/bin/env bash
set -euo pipefail

APP_NAME="pdfuse"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DATA_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/$APP_NAME"
VENV_DIR="$DATA_DIR/venv"
BIN_DIR="$DATA_DIR/bin"
SHELL_BLOCK_START="# >>> pdfuse >>>"
SHELL_BLOCK_END="# <<< pdfuse <<<"

if ! command -v uv >/dev/null 2>&1; then
    echo "Fehler: uv wird benötigt (https://docs.astral.sh/uv/)." >&2
    exit 1
fi

uv tool uninstall pdfuser >/dev/null 2>&1 || true

rm -rf "$VENV_DIR"
UV_PROJECT_ENVIRONMENT="$VENV_DIR" uv sync --project "$PROJECT_DIR" --frozen --no-editable --quiet

mkdir -p "$BIN_DIR"
ln -sfn "$VENV_DIR/bin/$APP_NAME" "$BIN_DIR/$APP_NAME"

case "$(basename "${SHELL:-}")" in
    zsh) RC_FILE="$HOME/.zshrc" ;;
    *) RC_FILE="$HOME/.bashrc" ;;
esac

touch "$RC_FILE"
sed -i "/^# >>> pdfuse >>>\$/,/^# <<< pdfuse <<<\$/d" "$RC_FILE"
{
    echo ""
    echo "$SHELL_BLOCK_START"
    echo "export PATH=\"$BIN_DIR:\$PATH\""
    echo "$SHELL_BLOCK_END"
} >> "$RC_FILE"

"$BIN_DIR/$APP_NAME" --help >/dev/null

echo "$APP_NAME installiert: $BIN_DIR/$APP_NAME"
echo "Shell-Eintrag geschrieben nach: $RC_FILE"
echo "Neues Terminal öffnen oder 'source $RC_FILE' ausführen."
echo "Deinstallation: $APP_NAME --uninstall"
