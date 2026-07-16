#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: ./scripts/install.sh [--force] [--codex] [--cursor] [--all]
                            [--cursor-project DIR]

Install the robotics-tutorial skill into Codex and/or Cursor skill directories.
With no host flag, installs to both Codex and Cursor personal skills.

  --codex              Install only under ${CODEX_HOME:-$HOME/.codex}/skills
  --cursor             Install under $HOME/.cursor/skills
  --all                Install to both Codex and Cursor personal skills (default)
  --cursor-project DIR Also link DIR/.cursor/skills/robotics-tutorial
  --force              Move an existing installation to a timestamped backup

Examples:
  ./scripts/install.sh
  ./scripts/install.sh --cursor --force
  ./scripts/install.sh --cursor-project /path/to/repo --force
  ./scripts/install.sh --cursor --cursor-project /path/to/repo --force
EOF
}

force=0
install_codex=0
install_cursor_personal=0
cursor_project=""
host_flags=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --force) force=1 ;;
    --codex)
      install_codex=1
      host_flags=1
      ;;
    --cursor)
      install_cursor_personal=1
      host_flags=1
      ;;
    --all)
      install_codex=1
      install_cursor_personal=1
      host_flags=1
      ;;
    --cursor-project)
      if [[ $# -lt 2 ]]; then
        printf '%s\n' '--cursor-project requires DIR' >&2
        exit 2
      fi
      cursor_project=$2
      host_flags=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      usage >&2
      exit 2
      ;;
  esac
  shift
done

if (( host_flags == 0 )); then
  install_codex=1
  install_cursor_personal=1
fi

resolve_path() {
  python3 - "$1" <<'PY'
from pathlib import Path
import sys

print(Path(sys.argv[1]).expanduser().resolve(strict=False))
PY
}

install_link() {
  local target=$1
  local label=$2
  local skills_dir
  skills_dir=$(dirname -- "$target")

  mkdir -p "$skills_dir"
  if [[ -e "$target" || -L "$target" ]]; then
    local current expected
    current="$(resolve_path "$target")"
    expected="$(resolve_path "$source_dir")"
    if [[ "$current" == "$expected" ]]; then
      printf 'Already installed: %s -> %s\n' "$target" "$source_dir"
      return 0
    fi
    if (( force == 0 )); then
      printf 'Existing installation found: %s\n' "$target" >&2
      printf 'Re-run with --force to preserve it as a backup and install this skill.\n' >&2
      return 1
    fi
    local backup="${target}.backup.$(date +%Y%m%d%H%M%S)"
    mv -- "$target" "$backup"
    printf 'Preserved existing installation at %s\n' "$backup"
  fi

  ln -s "$source_dir" "$target"
  printf 'Installed robotics-tutorial (%s): %s -> %s\n' "$label" "$target" "$source_dir"
}

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd -- "$script_dir/.." && pwd)"
source_dir="$repo_root/skill/robotics-tutorial"

git -C "$repo_root" submodule update --init --recursive

status=0

if (( install_codex )); then
  codex_home="${CODEX_HOME:-$HOME/.codex}"
  install_link "$codex_home/skills/robotics-tutorial" "Codex" || status=1
fi

if (( install_cursor_personal )); then
  install_link "$HOME/.cursor/skills/robotics-tutorial" "Cursor personal" || status=1
fi

if [[ -n "$cursor_project" ]]; then
  project_root="$(resolve_path "$cursor_project")"
  install_link "$project_root/.cursor/skills/robotics-tutorial" "Cursor project" || status=1
fi

if (( status != 0 )); then
  exit "$status"
fi

printf 'Start a new Codex/Cursor session to load the skill.\n'
