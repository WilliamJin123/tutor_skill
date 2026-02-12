"""
Git pre-commit hook helper: auto-bump patch version in plugin.json
for any skill directory that has staged changes.

Usage: python scripts/bump_versions.py
  - Detects staged files via `git diff --cached --name-only`
  - For each plugin dir with changes, bumps the patch version in its plugin.json
  - Stages the updated plugin.json so it's included in the commit
"""

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Each key is a top-level skill directory, value is its plugin.json path
PLUGIN_DIRS = {}
for plugin_json in REPO_ROOT.glob("*/.claude-plugin/plugin.json"):
    skill_dir = plugin_json.parent.parent
    PLUGIN_DIRS[skill_dir.name] = plugin_json


def get_staged_files():
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        capture_output=True, text=True, cwd=REPO_ROOT
    )
    return result.stdout.strip().splitlines()


def bump_patch(version: str) -> str:
    parts = version.split(".")
    parts[-1] = str(int(parts[-1]) + 1)
    return ".".join(parts)


def main():
    staged = get_staged_files()
    if not staged:
        return 0

    # Determine which skill directories have staged changes
    changed_dirs = set()
    for filepath in staged:
        parts = filepath.replace("\\", "/").split("/")
        if parts[0] in PLUGIN_DIRS:
            changed_dirs.add(parts[0])

    if not changed_dirs:
        return 0

    for dir_name in sorted(changed_dirs):
        plugin_path = PLUGIN_DIRS[dir_name]

        # Don't bump if the only staged file IS the plugin.json itself
        dir_staged = [
            f for f in staged
            if f.replace("\\", "/").startswith(dir_name + "/")
        ]
        rel_plugin = plugin_path.relative_to(REPO_ROOT).as_posix()
        if dir_staged == [rel_plugin]:
            continue

        data = json.loads(plugin_path.read_text(encoding="utf-8"))
        old_version = data["version"]
        new_version = bump_patch(old_version)
        data["version"] = new_version
        plugin_path.write_text(
            json.dumps(data, indent=2) + "\n", encoding="utf-8"
        )

        # Stage the bumped file
        subprocess.run(
            ["git", "add", str(plugin_path)],
            cwd=REPO_ROOT
        )
        print(f"[version-bump] {dir_name}: {old_version} -> {new_version}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
