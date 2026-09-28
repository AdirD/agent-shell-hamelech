#!/bin/sh
# Usage: sh evals/setup-fixture.sh <fixture-name> <workdir>
# Commits fixtures/<name>/base as the baseline, then overlays fixtures/<name>/after
# as uncommitted changes, so /melech-tidy sees a real working-tree diff.
set -eu

fixture_dir="$(cd "$(dirname "$0")/fixtures/$1" && pwd)"
workdir="$2"

mkdir -p "$workdir"
cp -R "$fixture_dir/base/." "$workdir/"
cd "$workdir"
git init -q -b main
git add -A
git -c user.name=eval -c user.email=eval@example.invalid commit -qm "base"
cp -R "$fixture_dir/after/." "$workdir/"
