#!/usr/bin/env python3
"""Search Robotics_Tutorial Markdown and Robotics_Theory LaTeX sources."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT_SPECS = {
    "tutorial": {
        "directory": "Robotics_Tutorial",
        "environment": "ROBOTICS_TUTORIAL_ROOT",
        "config": "tutorial_root",
    },
    "theory": {
        "directory": "Robotics_Theory",
        "environment": "ROBOTICS_THEORY_ROOT",
        "config": "theory_root",
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Search Markdown engineering notes and LaTeX robotics theory sources. "
            "Multiple literal queries are combined with OR by default."
        )
    )
    parser.add_argument("query", nargs="*", help="Literal terms, or one regex with --regex")
    parser.add_argument(
        "--root",
        choices=("both", "tutorial", "theory"),
        default="both",
        help="Knowledge base to search (default: both)",
    )
    parser.add_argument("--tutorial-root", type=Path, help="Override Robotics_Tutorial root")
    parser.add_argument("--theory-root", type=Path, help="Override Robotics_Theory root")
    parser.add_argument(
        "--print-roots",
        action="store_true",
        help="Print resolved roots and exit; no query is required",
    )
    parser.add_argument(
        "--regex",
        action="store_true",
        help="Treat the joined query as a regular expression instead of literals",
    )
    parser.add_argument("--context", type=int, default=0, help="Context lines around each match")
    parser.add_argument(
        "--limit",
        type=int,
        default=160,
        help="Maximum output lines per knowledge base",
    )
    parser.add_argument(
        "--case-sensitive",
        action="store_true",
        help="Use case-sensitive matching",
    )
    args = parser.parse_args()
    if not args.query and not args.print_roots:
        parser.error("at least one query is required unless --print-roots is used")
    return args


def expanded_path(value: str | os.PathLike[str]) -> Path:
    return Path(os.path.expandvars(os.path.expanduser(os.fspath(value)))).resolve()


def config_path() -> Path:
    override = os.environ.get("ROBOTICS_KNOWLEDGE_CONFIG")
    if override:
        return expanded_path(override)
    config_home = os.environ.get("XDG_CONFIG_HOME")
    base = expanded_path(config_home) if config_home else Path.home() / ".config"
    return base / "robotics-knowledge-skill" / "paths.json"


def load_config() -> dict[str, Any]:
    path = config_path()
    if not path.is_file():
        return {}
    try:
        content = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"cannot read configuration {path}: {error}") from error
    if not isinstance(content, dict):
        raise ValueError(f"configuration {path} must contain a JSON object")
    return content


def discovery_bases() -> list[Path]:
    starts = [Path(__file__).resolve().parent, Path.cwd().resolve()]
    bases: list[Path] = []
    seen: set[Path] = set()
    for start in starts:
        for candidate in (start, *start.parents):
            if candidate not in seen:
                seen.add(candidate)
                bases.append(candidate)
    return bases


def valid_root(root_name: str, path: Path) -> bool:
    if root_name == "tutorial":
        return path.is_dir() and any(path.glob("*.md"))
    return (path / "src").is_dir()


def resolve_root(
    root_name: str,
    explicit: Path | None,
    config: dict[str, Any],
) -> Path:
    spec = ROOT_SPECS[root_name]
    attempts: list[tuple[str, Path]] = []

    if explicit is not None:
        attempts.append(("command-line argument", expanded_path(explicit)))

    environment_value = os.environ.get(spec["environment"])
    if environment_value:
        attempts.append((spec["environment"], expanded_path(environment_value)))

    directory = spec["directory"]
    for base in discovery_bases():
        attempts.append(("relative discovery", base / "knowledge" / directory))
        attempts.append(("relative discovery", base / directory))

    config_value = config.get(spec["config"])
    if config_value:
        if not isinstance(config_value, str):
            raise ValueError(f"configuration key {spec['config']} must be a string")
        attempts.append((str(config_path()), expanded_path(config_value)))

    seen: set[Path] = set()
    for source, candidate in attempts:
        candidate = candidate.resolve()
        if candidate in seen:
            continue
        seen.add(candidate)
        if valid_root(root_name, candidate):
            return candidate

    checked = ", ".join(str(path) for _, path in attempts)
    raise FileNotFoundError(
        f"cannot locate {directory}. Initialize the repository submodules, set "
        f"{spec['environment']}, pass --{root_name}-root, or configure {config_path()}. "
        f"Checked: {checked or '(no candidates)'}"
    )


def build_pattern(queries: list[str], regex: bool) -> str:
    if regex:
        return " ".join(queries)

    def literal_pattern(query: str) -> str:
        escaped = re.escape(query)
        # Keep short acronyms such as AMP, MPC, PPO, and ROS from matching
        # unrelated words. CJK terms remain substring matches intentionally.
        if re.fullmatch(r"[A-Za-z0-9_][A-Za-z0-9_ .+/-]*", query):
            prefix = r"\b" if re.match(r"[A-Za-z0-9_]", query[0]) else ""
            suffix = r"\b" if re.match(r"[A-Za-z0-9_]", query[-1]) else ""
            return f"{prefix}{escaped}{suffix}"
        return escaped

    return "(?:" + "|".join(literal_pattern(query) for query in queries) + ")"


def rg_command(
    pattern: str,
    root_name: str,
    root: Path,
    context: int,
    case_sensitive: bool,
) -> list[str]:
    command = ["rg", "--line-number", "--color", "never"]
    if not case_sensitive:
        command.append("--ignore-case")
    if context > 0:
        command.extend(("--context", str(context)))
    command.extend(("--glob", "!**/.git/**", "--glob", "!**/.claude/**"))

    if root_name == "tutorial":
        command.extend(("--glob", "*.md", pattern, str(root)))
    else:
        command.extend(
            (
                "--glob",
                "*.tex",
                "--glob",
                "*.md",
                "--glob",
                "!build/**",
                "--glob",
                "!src/figures/**",
                "--glob",
                "!figures/**",
                pattern,
                str(root / "src"),
            )
        )
        if (root / "README.md").is_file():
            command.append(str(root / "README.md"))
    return command


def search_with_rg(
    pattern: str,
    root_name: str,
    root: Path,
    context: int,
    limit: int,
    case_sensitive: bool,
) -> tuple[list[str], bool]:
    result = subprocess.run(
        rg_command(pattern, root_name, root, context, case_sensitive),
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode not in (0, 1):
        raise RuntimeError(result.stderr.strip() or f"rg exited with {result.returncode}")
    lines = result.stdout.splitlines()
    return lines[:limit], len(lines) > limit


def candidate_files(root_name: str, root: Path) -> list[Path]:
    if root_name == "tutorial":
        return [
            path
            for path in root.rglob("*.md")
            if ".git" not in path.parts and ".claude" not in path.parts
        ]
    files = [root / "README.md"] if (root / "README.md").is_file() else []
    files.extend(
        path for path in (root / "src").rglob("*.tex") if "figures" not in path.parts
    )
    return files


def search_with_python(
    pattern: str,
    root_name: str,
    root: Path,
    context: int,
    limit: int,
    case_sensitive: bool,
) -> tuple[list[str], bool]:
    flags = 0 if case_sensitive else re.IGNORECASE
    matcher = re.compile(pattern, flags)
    output: list[str] = []
    for path in candidate_files(root_name, root):
        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        emitted: set[int] = set()
        for index, line in enumerate(lines):
            if not matcher.search(line):
                continue
            start = max(0, index - context)
            end = min(len(lines), index + context + 1)
            for line_index in range(start, end):
                if line_index in emitted:
                    continue
                emitted.add(line_index)
                output.append(f"{path}:{line_index + 1}:{lines[line_index]}")
                if len(output) >= limit:
                    return output, True
    return output, False


def main() -> int:
    args = parse_args()
    if args.context < 0 or args.limit <= 0:
        raise ValueError("--context must be non-negative and --limit must be positive")

    selected = ["tutorial", "theory"] if args.root == "both" else [args.root]
    config = load_config()
    explicit = {"tutorial": args.tutorial_root, "theory": args.theory_root}
    roots = {name: resolve_root(name, explicit[name], config) for name in selected}

    if args.print_roots:
        for name in selected:
            print(f"{name}={roots[name]}")
        return 0

    pattern = build_pattern(args.query, args.regex)
    use_rg = shutil.which("rg") is not None
    total_matches = 0

    for root_name in selected:
        print(f"## {root_name}")
        if use_rg:
            lines, truncated = search_with_rg(
                pattern,
                root_name,
                roots[root_name],
                args.context,
                args.limit,
                args.case_sensitive,
            )
        else:
            lines, truncated = search_with_python(
                pattern,
                root_name,
                roots[root_name],
                args.context,
                args.limit,
                args.case_sensitive,
            )
        if lines:
            print("\n".join(lines))
            total_matches += len(lines)
        else:
            print("(no matches)")
        if truncated:
            print(f"... truncated at {args.limit} output lines; narrow the query")

    if total_matches == 0:
        print("No matches. Try bilingual synonyms or a broader subsystem term.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (FileNotFoundError, RuntimeError, ValueError, re.error) as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(2) from error
