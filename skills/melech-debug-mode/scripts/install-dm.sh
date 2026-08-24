#!/usr/bin/env sh
# Install the melech-debug-mode `dm` command by sourcing dm.sh from your shell rc.
#
# Usage:
#   sh install-dm.sh            # auto-detect ~/.zshrc or ~/.bashrc from $SHELL
#   sh install-dm.sh ~/.zshrc   # or target a specific rc file
#
# Idempotent: re-running will not add duplicate lines.
set -eu

dir="$(cd "$(dirname "$0")" >/dev/null 2>&1 && pwd)"
dm_sh="$dir/dm.sh"
if [ ! -f "$dm_sh" ]; then
	echo "install-dm: dm.sh not found at $dm_sh" >&2
	exit 1
fi

rc="${1:-}"
if [ -z "$rc" ]; then
	case "${SHELL:-}" in
	*zsh) rc="$HOME/.zshrc" ;;
	*bash) rc="$HOME/.bashrc" ;;
	*) rc="$HOME/.profile" ;;
	esac
fi

if [ -f "$rc" ] && grep -Fq "$dm_sh" "$rc"; then
	echo "dm already installed in $rc"
else
	printf '\n# melech-debug-mode skill -- dm command\nsource "%s"\n' "$dm_sh" >>"$rc"
	echo "Added dm to $rc"
fi

echo "Reload your shell:  source \"$rc\""
echo "Then run:           dm        (or 'dm help')"
