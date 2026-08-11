"""Generate (or validate) the structural skeleton of a harness.

Structure only: every file is a stub, empty by design. The scaffold grants no
authority — the harness contract does that.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]

STUB_NOTE = "(stub — intentionally empty; filling it is human work)"

ROLES = {
    "architect": "judgment — reviews plans, reads everything, no bash, writes nothing",
    "developer": "execution — builds only inside the contract's writable paths",
}


def slug(stack: list[str]) -> str:
    return "-".join(stack)


def plan_files(stack: list[str]) -> dict[str, str]:
    files: dict[str, str] = {}
    for role, job in ROLES.items():
        files[f"agents/{role}.md"] = f"# {role}\n\n> {job}\n\n{STUB_NOTE}\n"
    for item in stack:
        files[f"kb/{item}/README.md"] = f"# KB · {item}\n\n{STUB_NOTE}\n"
        files[f"rules/{item}.md"] = f"# rules · {item}\n\n{STUB_NOTE}\n"
    files["skills/README.md"] = f"# skills\n\n{STUB_NOTE}\n"
    return files


def generate(stack: list[str], dest: Path) -> Path:
    root = dest / slug(stack)
    files = plan_files(stack)
    for rel, content in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    manifest = {
        "stack": stack,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "files": sorted(files),
        "note": "structure only — every stub is empty by design; no authority granted",
    }
    (root / "MANIFEST.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    return root


def check(stack: list[str], dest: Path) -> list[str]:
    root = dest / slug(stack)
    problems: list[str] = []
    if not root.is_dir():
        return [f"missing scaffold root: {root}"]
    expected = set(plan_files(stack)) | {"MANIFEST.json"}
    for rel in sorted(expected):
        path = root / rel
        if not path.is_file():
            problems.append(f"missing: {rel}")
        elif rel.endswith(".md") and STUB_NOTE not in path.read_text(encoding="utf-8"):
            problems.append(f"not a stub (content added?): {rel}")
    return problems


def tree(root: Path) -> str:
    lines = [str(root.relative_to(REPO_ROOT)) if root.is_relative_to(REPO_ROOT) else str(root)]
    for path in sorted(root.rglob("*")):
        depth = len(path.relative_to(root).parts)
        lines.append("  " * depth + path.name + ("/" if path.is_dir() else ""))
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stack", required=True, help="comma-separated stack, e.g. dbt,duckdb,fastapi,mcp")
    parser.add_argument("--dest", default="tmp/harness-scaffold", help="output directory (kept under tmp/)")
    parser.add_argument("--check", action="store_true", help="validate an existing scaffold instead of writing")
    args = parser.parse_args()

    stack = [s.strip() for s in args.stack.split(",") if s.strip()]
    dest = Path(args.dest)
    if not dest.is_absolute():
        dest = REPO_ROOT / dest

    if args.check:
        problems = check(stack, dest)
        if problems:
            print("CHECK_SCAFFOLD=FAIL")
            for p in problems:
                print(f"  - {p}")
            return 1
        print("CHECK_SCAFFOLD=PASS — structure valid, all stubs empty by design")
        return 0

    root = generate(stack, dest)
    print(tree(root))
    print(f"\ngenerated {sum(1 for _ in root.rglob('*') if _.is_file())} files under {root}")
    print("every stub is empty by design — structure, not content, not authority")
    return 0


if __name__ == "__main__":
    sys.exit(main())
