#!/usr/bin/env python3
"""
ETL Deploy - Smoke runner

- Reads settings.json (handles UTF-8 with or without BOM)
- Performs minimal sanity checks
- Prints a concise summary to stdout
- Exits with non-zero code on errors

Stdlib-only. No external deps.
"""

from __future__ import annotations

import json
import sys
import traceback
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


SETTINGS_FILE = Path("settings.json")
DEFAULT_REQUIRED_KEYS: Tuple[str, ...] = (
    # Adjust this tuple to your actual schema as it evolves:
    "project",
    "instance",
    "repos",     # expected: list of repos to clone/use
    "secrets",   # expected: dict of secret names -> values/placeholders
)


def load_settings(path: Path = SETTINGS_FILE) -> Dict[str, Any]:
    """
    Load JSON settings, accepting UTF-8 with or without BOM.
    Raises SystemExit with code 2 on failure.
    """
    if not path.exists():
        print(f"[ERROR] Settings file not found: {path.resolve()}", file=sys.stderr)
        raise SystemExit(2)

    try:
        # utf-8-sig handles BOM transparently
        with path.open("r", encoding="utf-8-sig") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"[ERROR] Invalid JSON in {path}: {e}", file=sys.stderr)
        raise SystemExit(2)
    except OSError as e:
        print(f"[ERROR] Cannot read {path}: {e}", file=sys.stderr)
        raise SystemExit(2)

    if not isinstance(data, dict):
        print(f"[ERROR] Root of {path} must be a JSON object (dict).", file=sys.stderr)
        raise SystemExit(2)

    return data


def coalesce_required_keys(cfg: Dict[str, Any]) -> Tuple[str, ...]:
    """
    Determine which keys are required.
    If the JSON contains "required_keys": ["a","b",...], use that.
    Otherwise, fall back to DEFAULT_REQUIRED_KEYS.
    """
    rk = cfg.get("required_keys")
    if isinstance(rk, list) and all(isinstance(k, str) for k in rk):
        # de-duplicate while preserving order
        seen = set()
        ordered: List[str] = []
        for k in rk:
            if k not in seen:
                ordered.append(k)
                seen.add(k)
        return tuple(ordered)
    return DEFAULT_REQUIRED_KEYS


def validate_settings(cfg: Dict[str, Any]) -> None:
    """
    Minimal sanity checks. Exit(3) if validation fails.
    """
    required = coalesce_required_keys(cfg)
    missing = [k for k in required if k not in cfg]
    if missing:
        print(f"[ERROR] Missing required keys in settings.json: {', '.join(missing)}", file=sys.stderr)
        raise SystemExit(3)

    # Optional deeper checks based on conventional schema:
    if "repos" in cfg:
        repos = cfg["repos"]
        if not isinstance(repos, list):
            print("[ERROR] 'repos' must be a list.", file=sys.stderr)
            raise SystemExit(3)
        for i, r in enumerate(repos):
            if not isinstance(r, dict):
                print(f"[ERROR] repos[{i}] must be an object.", file=sys.stderr)
                raise SystemExit(3)
            for key in ("name", "url"):
                if key not in r or not isinstance(r[key], str) or not r[key].strip():
                    print(f"[ERROR] repos[{i}].{key} must be a non-empty string.", file=sys.stderr)
                    raise SystemExit(3)

    if "secrets" in cfg and not isinstance(cfg["secrets"], dict):
        print("[ERROR] 'secrets' must be an object (dict).", file=sys.stderr)
        raise SystemExit(3)


def summarize_settings(cfg: Dict[str, Any]) -> None:
    """
    Print a concise, stable summary for logs.
    Avoid printing secret values; show only keys/counts.
    """
    project = cfg.get("project", "<unknown>")
    instance = cfg.get("instance", "<unknown>")

    print("=== ETL Deploy :: Settings Summary ===")
    print(f"Project:  {project}")
    print(f"Instance: {instance}")

    # Repos
    repos = cfg.get("repos", [])
    if isinstance(repos, list):
        print(f"Repos:    {len(repos)}")
        for r in repos:
            if isinstance(r, dict):
                name = r.get("name", "<noname>")
                url = r.get("url", "<nourl>")
                branch = r.get("branch", "main")
                print(f"  - {name} :: {url} @ {branch}")
    else:
        print("Repos:    <invalid type>")

    # Secrets
    secrets = cfg.get("secrets", {})
    if isinstance(secrets, dict):
        print(f"Secrets:  {len(secrets)} keys")
        if secrets:
            print(f"  keys: {', '.join(sorted(map(str, secrets.keys())))}")
    else:
        print("Secrets:  <invalid type>")

    # Arbitrary extra fields
    extra = sorted(k for k in cfg.keys() if k not in {"project", "instance", "repos", "secrets", "required_keys"})
    if extra:
        print(f"Other keys: {', '.join(extra)}")

    print("=== End Summary ===")


def main() -> int:
    """
    Returns:
        0 on success
        2 on load/read errors
        3 on validation errors
        4 on unexpected exceptions
    """
    try:
        cfg = load_settings(SETTINGS_FILE)
        validate_settings(cfg)
        summarize_settings(cfg)

        # Place any additional smoke logic here, e.g.:
        # - verify directories exist
        # - dry-run commands
        # - check that required executables are on PATH
        # For now we just succeed if validation passed.
        print("[OK] Smoke run completed successfully.")
        return 0

    except SystemExit as e:
        # Re-raise SystemExit to preserve our explicit exit codes (2/3)
        raise e
    except Exception:
        print("[ERROR] Unexpected exception:", file=sys.stderr)
        traceback.print_exc()
        return 4


if __name__ == "__main__":
    sys.exit(main())
