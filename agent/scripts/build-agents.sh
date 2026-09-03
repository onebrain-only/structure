#!/bin/sh
# Build .claude/agents/<name>.md from a tool-neutral role + a Claude-specific binding.
#
#   agent/roles/<name>.md            neutral markdown, no frontmatter — the ROLE
#   .claude/bindings/<name>.yml      YAML frontmatter body           — the BINDING
#   .claude/agents/<name>.md         generated: fence + binding + fence + banner + role
#
# Only agents that have a binding are generated; every other file in
# .claude/agents/ is left untouched.
#
# Usage:
#   agent/scripts/build-agents.sh          regenerate
#   agent/scripts/build-agents.sh --check  verify regeneration is a no-op (exit 1 if not)
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)
BINDINGS="$ROOT/.claude/bindings"
ROLES="$ROOT/agent/roles"
AGENTS="$ROOT/.claude/agents"

CHECK=0
[ "${1:-}" = "--check" ] && CHECK=1

[ -d "$BINDINGS" ] || { echo "ERROR: no $BINDINGS"; exit 1; }
mkdir -p "$AGENTS"

status=0
found=0
for binding in "$BINDINGS"/*.yml; do
  [ -e "$binding" ] || continue
  found=$((found + 1))
  name=$(basename "$binding" .yml)
  role="$ROLES/$name.md"
  out="$AGENTS/$name.md"

  if [ ! -f "$role" ]; then
    echo "ERROR: binding $name has no role at $role"
    status=1
    continue
  fi

  tmp=$(mktemp)
  printf -- '---\n'  >  "$tmp"
  cat "$binding"     >> "$tmp"
  printf -- '---\n'  >> "$tmp"
  printf -- '<!-- GENERATED FILE — do not edit. -->\n'                                       >> "$tmp"
  printf -- '<!-- Source: agent/roles/%s.md + .claude/bindings/%s.yml -->\n' "$name" "$name" >> "$tmp"
  printf -- '<!-- Rebuild: agent/scripts/build-agents.sh -->\n'                              >> "$tmp"
  printf -- '\n'                                                                >> "$tmp"
  cat "$role"        >> "$tmp"

  if [ "$CHECK" -eq 1 ]; then
    if [ -f "$out" ] && cmp -s "$tmp" "$out"; then
      echo "ok      $name"
    else
      echo "STALE   $name  ($out differs from generated output)"
      status=1
    fi
    rm -f "$tmp"
  else
    mv "$tmp" "$out"
    echo "built   $name"
  fi
done

[ "$found" -eq 0 ] && { echo "ERROR: no bindings found in $BINDINGS"; exit 1; }
exit "$status"
