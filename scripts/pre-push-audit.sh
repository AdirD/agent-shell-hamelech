#!/usr/bin/env bash
# Scan tracked files and push hygiene before sending commits to origin.
# Usage:  bash scripts/pre-push-audit.sh
# Hook:   ln -sf ../../scripts/pre-push-audit.sh .git/hooks/pre-push

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

fail=0
warn() { printf '\033[1;33m[!] %s\033[0m\n' "$*"; fail=1; }
ok()   { printf '\033[1;32m[ok] %s\033[0m\n' "$*"; }

say() { printf '\n\033[1;36m==> %s\033[0m\n' "$*"; }

# Extend locally in .ops/pre-push-audit.local (gitignored) with extra patterns
# or paths — e.g. employer domains you never want in a public repo.
LOCAL_EXT="$ROOT/.ops/pre-push-audit.local"
if [[ -f "$LOCAL_EXT" ]]; then
  # shellcheck disable=SC1090
  source "$LOCAL_EXT"
fi

SECRET_PATTERN="${SECRET_PATTERN:-sk-ant-|sk-[A-Za-z0-9]{20,}|gh[pousr]_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|BEGIN (RSA |EC |OPENSSH )?PRIVATE}"

say "Staged paths must not include gitignored agent state"
STAGED="$(git diff --cached --name-only 2>/dev/null || true)"
if [[ -n "$STAGED" ]]; then
  BAD_STAGED="$(printf '%s\n' "$STAGED" | grep -E '^\.(claude|codex|cursor|entire|gemini|serena|superset|ops)/' || true)"
  if [[ -n "$BAD_STAGED" ]]; then
    warn "Staged files under local agent/ops dirs:"
    printf '%s\n' "$BAD_STAGED"
  else
    ok "no gitignored agent/ops paths staged"
  fi
else
  ok "nothing staged"
fi

say "Tracked tree must not match secret patterns"
TRACKED="$(git ls-tree -r HEAD --name-only)"
if [[ -n "$TRACKED" ]]; then
  SECRET_HITS="$(printf '%s\n' "$TRACKED" | xargs grep -aE "$SECRET_PATTERN" 2>/dev/null || true)"
  if [[ -n "$SECRET_HITS" ]]; then
    warn "Possible secrets in tracked files:"
    printf '%s\n' "$SECRET_HITS"
  else
    ok "no secret-shaped strings in tracked files"
  fi
else
  ok "empty tree"
fi

if [[ -n "${EXTRA_PATTERN:-}" ]]; then
  say "Extra local pattern scan"
  EXTRA_FILES="$(printf '%s\n' "$TRACKED" | grep -v 'pre-push-audit\.local\.example$' || true)"
  if [[ -n "$EXTRA_FILES" ]]; then
    # -i: employer names often appear as bare words, not only as domains.
    EXTRA_HITS="$(printf '%s\n' "$EXTRA_FILES" | xargs grep -aiE "$EXTRA_PATTERN" 2>/dev/null || true)"
  else
    EXTRA_HITS=""
  fi
  if [[ -n "$EXTRA_HITS" ]]; then
    warn "Matches for EXTRA_PATTERN from .ops/pre-push-audit.local:"
    printf '%s\n' "$EXTRA_HITS"
  else
    ok "no extra-pattern matches"
  fi
fi

say "Commit identity on unpushed commits (author and committer)"
if git rev-parse --verify origin/main >/dev/null 2>&1; then
  UNPUSHED="$(git log origin/main..HEAD --format='%H %ae %ce' 2>/dev/null || true)"
else
  UNPUSHED="$(git log --format='%H %ae %ce')"
fi
if [[ -n "$UNPUSHED" ]]; then
  if [[ -n "${WORK_EMAIL_PATTERN:-}" ]]; then
    BAD_IDENTITY="$(printf '%s\n' "$UNPUSHED" | awk '{print $2"\n"$3}' | grep -E "$WORK_EMAIL_PATTERN" || true)"
    if [[ -n "$BAD_IDENTITY" ]]; then
      warn "Work/internal email in author or committer on commits about to push:"
      printf '%s\n' "$BAD_IDENTITY" | sort -u
    else
      ok "no work/internal author or committer emails in unpushed commits"
    fi
  else
    ok "WORK_EMAIL_PATTERN not configured (.ops/pre-push-audit.local)"
  fi

  if [[ -n "${PERSONAL_EMAIL:-}" ]]; then
    CONFIG_EMAIL="$(git config user.email 2>/dev/null || true)"
    if [[ "$CONFIG_EMAIL" != "$PERSONAL_EMAIL" ]]; then
      warn "git config user.email is '$CONFIG_EMAIL' (expected '$PERSONAL_EMAIL' for this repo)"
    else
      ok "git config user.email matches PERSONAL_EMAIL"
    fi
  fi
else
  ok "nothing new to push"
fi

say "Remote branch hygiene"
if git remote get-url origin >/dev/null 2>&1; then
  EXTRA_BRANCHES="$(git ls-remote origin 2>/dev/null | awk '{print $2}' | grep '^refs/heads/' | grep -v '^refs/heads/main$' || true)"
  if [[ -n "$EXTRA_BRANCHES" ]]; then
    warn "Unexpected remote branches (side branches can leak agent sessions):"
    printf '%s\n' "$EXTRA_BRANCHES"
  else
    ok "only main on origin (or origin unreachable)"
  fi
else
  warn "no origin remote configured"
fi

say "Auto-push agent hooks"
ENTIRE_HOOKS="$(grep -l 'entire hooks' .git/hooks/* 2>/dev/null || true)"
if [[ -d .entire || -n "$ENTIRE_HOOKS" ]]; then
  warn "'entire' is installed — it can auto-push session transcripts. Run: entire disable --uninstall --force"
else
  ok "entire auto-push hooks not present"
fi

if [[ "$fail" -ne 0 ]]; then
  printf '\n\033[1;31mAudit failed. Fix the items above before pushing.\033[0m\n'
  exit 1
fi

printf '\n\033[1;32mPre-push audit passed.\033[0m\n'
