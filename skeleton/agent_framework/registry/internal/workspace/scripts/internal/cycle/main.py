"""
cycle/main.py — APD Cycle Script

Runs every time the Orchestrator starts its loop. Performs four steps in order:
  1. Merge agents.json from internal/ and project/ registries.
  2. Sync workspace files from both registries into agent_framework/.
  3. Sync .roomodes and .roo/rules-{slug}/ from the merged agent definitions.
  4. Scan inbox/unread/message.md and print the next recipient slug (or status).

Output (stdout, last line):
  APD_CONFLICT:{slug}  — duplicate slug detected between internal and project agents.json
  user                 — unread/message.md exists and to: user
  {agent-slug}         — unread/message.md exists and to: {slug}
  empty                — no unread/message.md or no to: field
"""

import json
import os
import re
import shutil
from pathlib import Path


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_json(path: Path) -> dict:
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


# ---------------------------------------------------------------------------
# Step 1 — Merge agents.json
# ---------------------------------------------------------------------------

def load_agents_file(agents_json_path: Path) -> dict:
    """Load a single agents.json. Returns {'profiles': [], 'agents': []} on missing."""
    data = load_json(agents_json_path)
    return {
        "profiles": data.get("profiles", []),
        "agents": data.get("agents", []),
    }


def merge_agents(internal_data: dict, project_data: dict) -> dict | None:
    """
    Merge internal and project agents.json.
    Profiles are kept separate per source (not shared across files).
    Returns merged dict, or None if a slug conflict is detected (prints error).
    """
    internal_slugs = {a["roo"]["slug"] for a in internal_data["agents"]}
    project_slugs = {a["roo"]["slug"] for a in project_data["agents"]}

    conflicts = internal_slugs & project_slugs
    if conflicts:
        conflict_slug = next(iter(conflicts))
        print(f"APD_CONFLICT:{conflict_slug}")
        return None

    return {
        "internal": internal_data,
        "project": project_data,
    }


# ---------------------------------------------------------------------------
# Step 2 — Sync workspace
# ---------------------------------------------------------------------------

def sync_workspace(src_workspace: Path, agent_framework_dir: Path) -> None:
    """
    Recursively sync files from src_workspace into agent_framework_dir.
    Rules:
      - If destination does not exist → copy.
      - If destination exists → keep the newer file (by mtime).
    """
    if not src_workspace.exists():
        return

    for src_file in src_workspace.rglob("*"):
        if not src_file.is_file():
            continue

        relative = src_file.relative_to(src_workspace)
        dst_file = agent_framework_dir / relative

        if not dst_file.exists():
            dst_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_file, dst_file)
        else:
            src_mtime = src_file.stat().st_mtime
            dst_mtime = dst_file.stat().st_mtime
            if src_mtime > dst_mtime:
                shutil.copy2(src_file, dst_file)


# ---------------------------------------------------------------------------
# Step 3 — Sync .roomodes and .roo/rules-{slug}/
# ---------------------------------------------------------------------------

def resolve_agent_files(agent: dict, source_data: dict, agents_json_dir: Path) -> list[Path]:
    """
    Resolve the effective list of rule files for an agent.
    Profiles are resolved from the same agents.json source (not cross-file).
    File paths are relative to the agents.json directory.
    Returns list of absolute Paths.
    """
    profiles_map = {p["name"]: p["files"] for p in source_data["profiles"]}
    files = []

    for profile_name in agent["apd"].get("profiles", []):
        for f in profiles_map.get(profile_name, []):
            files.append(agents_json_dir / f)

    for f in agent["apd"].get("files", []):
        files.append(agents_json_dir / f)

    return files


def build_roomodes_entry(agent: dict) -> dict:
    """Build a single .roomodes customModes entry from the agent's roo block."""
    roo = agent["roo"]
    return {
        "slug": roo["slug"],
        "name": roo["name"],
        "roleDefinition": roo["roleDefinition"],
        "groups": roo.get("groups", []),
        "customInstructions": roo.get("customInstructions", ""),
    }


def sync_roo_environment(merged: dict, base_dir: Path, internal_agents_dir: Path, project_agents_dir: Path) -> None:
    """
    Rebuild .roomodes and .roo/rules-{slug}/ from the merged agent definitions.
    Only updates entries that have changed.
    File paths in agents.json are resolved relative to each agents.json directory.
    """
    roomodes_path = base_dir / ".roomodes"
    roo_dir = base_dir / ".roo"

    # Load existing .roomodes
    existing_roomodes = load_json(roomodes_path)
    existing_modes = {m["slug"]: m for m in existing_roomodes.get("customModes", [])}

    new_modes = []

    all_sources = [
        (merged["internal"], internal_agents_dir),
        (merged["project"], project_agents_dir),
    ]

    for source_data, agents_json_dir in all_sources:
        for agent in source_data["agents"]:
            slug = agent["roo"]["slug"]
            mode_entry = build_roomodes_entry(agent)
            new_modes.append(mode_entry)

            # Resolve rule files relative to agents.json directory
            rule_files = resolve_agent_files(agent, source_data, agents_json_dir)

            rules_dir = roo_dir / f"rules-{slug}"

            # Check if rules need updating
            needs_update = False
            if not rules_dir.exists():
                needs_update = True
            else:
                # Check if mode entry changed
                if existing_modes.get(slug) != mode_entry:
                    needs_update = True
                else:
                    # Check if any source file is newer than the rules dir
                    rules_mtime = rules_dir.stat().st_mtime
                    for rf in rule_files:
                        if rf.exists() and rf.stat().st_mtime > rules_mtime:
                            needs_update = True
                            break

            if needs_update:
                if rules_dir.exists():
                    shutil.rmtree(rules_dir)
                rules_dir.mkdir(parents=True, exist_ok=True)

                for rf in rule_files:
                    if rf.exists():
                        shutil.copy2(rf, rules_dir / rf.name)

    # Write .roomodes if changed
    new_roomodes = {"customModes": new_modes}
    if new_roomodes != existing_roomodes:
        save_json(roomodes_path, new_roomodes)


# ---------------------------------------------------------------------------
# Step 4 — Scan inbox
# ---------------------------------------------------------------------------

def read_to_field(message_path: Path) -> str | None:
    try:
        content = message_path.read_text(encoding="utf-8")
    except OSError:
        return None

    meta_match = re.search(
        r"<message_metadata>(.*?)</message_metadata>", content, re.DOTALL | re.IGNORECASE
    )
    if not meta_match:
        return None

    to_match = re.search(r"^to\s*:\s*(.+)$", meta_match.group(1), re.MULTILINE | re.IGNORECASE)
    if not to_match:
        return None

    return to_match.group(1).strip()


def scan_inbox(base_dir: Path) -> str:
    message_path = base_dir / "agent_framework/inbox/unread/message.md"

    if not message_path.exists():
        return "empty"

    recipient = read_to_field(message_path)
    if not recipient:
        return "empty"

    return recipient  # "user" or agent slug


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    base_dir = Path(os.getcwd())
    registry_dir = base_dir / "agent_framework/registry"
    agent_framework_dir = base_dir / "agent_framework"

    # --- Step 1: Merge agents.json ---
    internal_agents_path = registry_dir / "internal/agents/agents.json"
    project_agents_path = registry_dir / "project/agents/agents.json"

    internal_data = load_agents_file(internal_agents_path)
    project_data = load_agents_file(project_agents_path)

    merged = merge_agents(internal_data, project_data)
    if merged is None:
        # Conflict already printed by merge_agents
        return

    # --- Step 2: Sync workspace ---
    sync_workspace(registry_dir / "internal/workspace", agent_framework_dir)
    sync_workspace(registry_dir / "project/workspace", agent_framework_dir)

    # --- Step 3: Sync .roomodes and .roo/rules-{slug}/ ---
    sync_roo_environment(merged, base_dir, internal_agents_path.parent, project_agents_path.parent)

    # --- Step 4: Scan inbox ---
    result = scan_inbox(base_dir)
    print(result)


if __name__ == "__main__":
    main()
