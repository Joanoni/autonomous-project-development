#!/usr/bin/env python3
import json
import subprocess
import sys
from pathlib import Path


def run(cmd: str) -> None:
    print(f"\n$ {cmd}")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"Command failed with exit code {result.returncode}: {cmd}", file=sys.stderr)
        sys.exit(result.returncode)


def main() -> None:
    input_path = Path(__file__).parent / "input.json"
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    current_branch: str = data["current_branch"]
    commit_message: str = data["commit_message"]
    merge_message: str = data["merge_message"]

    # Step 1: add, commit and push current branch
    run(
        f'git add . && git commit -m "{commit_message}" && git push --set-upstream origin {current_branch}'
    )

    # Step 2: merge into main, push, delete branch locally and remotely
    run(
        f'git checkout main && git merge {current_branch} --no-ff -m "{merge_message}" && '
        f'git push origin main && git branch -d {current_branch} && git push origin --delete {current_branch}'
    )

    # Step 3: create new improvements branch
    run("git checkout -b improvements")

    # Reset input.json fields to empty strings
    empty = {key: "" for key in data}
    with open(input_path, "w", encoding="utf-8") as f:
        json.dump(empty, f, indent=2)
        f.write("\n")
    print("\ninput.json reset to empty strings.")


if __name__ == "__main__":
    main()
