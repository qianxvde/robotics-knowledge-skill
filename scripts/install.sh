#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: ./scripts/install.sh [--force]

Install the robotics-tutorial skill into ${CODEX_HOME:-$HOME/.codex}/skills.
Use --force to move an existing installation to a timestamped backup.
EOF
}

force=0
case "${1:-}" in
  "") ;;
  --force) force=1 ;;
  -h|--help)
    usage
    exit 0
    ;;
  *)
    usage >&2
    exit 2
    ;;
esac

resolve_path() {
  python3 - "$1" <<'PY'
from pathlib import Path
import sys

print(Path(sys.argv[1]).expanduser().resolve(strict=False))
PY
}

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd -- "$script_dir/.." && pwd)"
source_dir="$repo_root/skill/robotics-tutorial"
codex_home="${CODEX_HOME:-$HOME/.codex}"
skills_dir="$codex_home/skills"
target="$skills_dir/robotics-tutorial"

git -C "$repo_root" submodule update --init --recursive

mkdir -p "$skills_dir"
if [[ -e "$target" || -L "$target" ]]; then
  current="$(resolve_path "$target")"
  expected="$(resolve_path "$source_dir")"
  if [[ "$current" == "$expected" ]]; then
    printf 'Already installed: %s -> %s\n' "$target" "$source_dir"
    exit 0
  fi
  if (( force == 0 )); then
    printf 'Existing installation found: %s\n' "$target" >&2
    printf 'Re-run with --force to preserve it as a backup and install this skill.\n' >&2
    exit 1
  fi
  backup="${target}.backup.$(date +%Y%m%d%H%M%S)"
  mv -- "$target" "$backup"
  printf 'Preserved existing installation at %s\n' "$backup"
fi

ln -s "$source_dir" "$target"
printf 'Installed robotics-tutorial: %s -> %s\n' "$target" "$source_dir"
printf 'Start a new Codex session to load the skill.\n'
