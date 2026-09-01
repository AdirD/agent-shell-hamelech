#!/usr/bin/env sh
# Install the melech-debug-mode `dm` command by sourcing dm.sh from your shell rc.
#
# Usage:
#   sh install-dm.sh            # auto-detect ~/.zshrc or ~/.bashrc from $SHELL
#   sh install-dm.sh ~/.zshrc   # or target a specific rc file
#
# Re-running rewrites the managed block in place and strips any earlier dm line,
# so a moved or renamed skill directory is repaired instead of duplicated.
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

# Keep the rc readable, and stable if $HOME is ever remounted elsewhere.
dm_sh_rc="$dm_sh"
case "$dm_sh" in
"$HOME"/*) dm_sh_rc="\$HOME${dm_sh#"$HOME"}" ;;
esac

begin='# >>> melech-debug-mode dm >>>'
end='# <<< melech-debug-mode dm <<<'

tmp="$rc.dm-install.$$"
trap 'rm -f "$tmp" "$tmp.trim"' EXIT INT TERM
: >"$tmp"

# Drop the managed block plus any legacy dm lines from earlier installer
# versions, which wrote a bare `source <abs-path>` under a plain comment.
if [ -f "$rc" ]; then
	awk -v begin="$begin" -v end="$end" '
		$0 == begin { inblock = 1; next }
		$0 == end { inblock = 0; next }
		inblock { next }
		index($0, "debug-mode/scripts/dm.sh") { next }
		/^# (melech-)?debug-mode skill -- dm command$/ { next }
		{ print }
	' "$rc" >"$tmp"

	# Removal can leave the file ending in blank lines; trim them back.
	while [ -s "$tmp" ] && [ -z "$(tail -n 1 "$tmp")" ]; do
		sed '$d' "$tmp" >"$tmp.trim"
		mv "$tmp.trim" "$tmp"
	done
fi

# The -f guard is the whole point: a renamed or uninstalled skill must never
# break shell startup, which is how the stale-path error got shipped before.
{
	if [ -s "$tmp" ]; then echo ""; fi
	echo "$begin"
	printf 'if [ -f "%s" ]; then\n\t. "%s"\nfi\n' "$dm_sh_rc" "$dm_sh_rc"
	echo "$end"
} >>"$tmp"

if [ -f "$rc" ] && cmp -s "$tmp" "$rc"; then
	echo "dm already installed in $rc"
else
	cat "$tmp" >"$rc"
	echo "Installed dm in $rc"
fi

echo "Reload your shell:  . \"$rc\""
echo "Then run:           dm        (or 'dm help')"
