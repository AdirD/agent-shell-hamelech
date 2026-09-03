# melech-debug-mode skill -- `dm` command (bash + zsh).
#
# Source this file from your shell rc, e.g.:
#   source /path/to/melech-debug-mode/scripts/dm.sh
# or run the installer once:
#   sh /path/to/melech-debug-mode/scripts/install-dm.sh
#
# Usage:
#   dm                live doctor TUI (running sessions, health, log tail, kill)
#   dm help           list every command
#   dm start          start a new collector session
#   dm status <dir>   show one session's status
#   dm logs <dir>     print collected events as compact JSONL
#   dm stop <dir>     stop and remove one session

# Resolve this file's own directory so `dm` finds the co-located launcher,
# regardless of where the skill is installed.
if [ -n "${ZSH_VERSION:-}" ]; then
	_dm_self="${(%):-%x}"
elif [ -n "${BASH_VERSION:-}" ]; then
	_dm_self="${BASH_SOURCE[0]}"
else
	_dm_self="$0"
fi
_DM_SCRIPT="$(cd "$(dirname "$_dm_self")" >/dev/null 2>&1 && pwd)/debug_session.py"
unset _dm_self

dm() {
	local script="$_DM_SCRIPT"
	if [ ! -f "$script" ]; then
		printf 'dm: melech-debug-mode launcher not found at %s\n' "$script" >&2
		return 1
	fi
	if [ "$#" -eq 0 ]; then
		python3 "$script" doctor
		return $?
	fi
	case "$1" in
		help | -h | --help)
			python3 "$script" --help
			;;
		*)
			python3 "$script" "$@"
			;;
	esac
}
