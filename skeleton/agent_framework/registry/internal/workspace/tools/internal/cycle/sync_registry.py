"""
cycle/sync_registry.py — Steps 1, 2, 3

  1. Merge agents.json from shared/, internal/ and project/ registries.
  2. Sync workspace files from all three registries into agent_framework/.
  3. Sync .roomodes and .roo/rules-{slug}/ from the merged agent definitions.

Public entry point:
  run(base_dir, registry_dir, agent_framework_dir) -> dict | None
    Returns the merged dict on success, or None if a slug conflict is detected
    (conflict slug is printed to stdout as APD_CONFLICT:{slug}).
"""

import json
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


def merge_agents(shared_data: dict, internal_data: dict, project_data: dict) -> dict | None:
    """
    Merge shared, internal and project agents.json.
    Profiles are scoped per source; agents reference profiles by name+source.
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
        "shared": shared_data,
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

def build_profiles_map(merged: dict, agents_dirs: dict) -> dict:
    """
    Build a map of { (source, profile_name): [absolute Path, ...] } from all sources.
    agents_dirs: { "shared": Path, "internal": Path, "project": Path }
    """
    profiles_map = {}
    for source_key, source_data in merged.items():
        agents_dir = agents_dirs[source_key]
        for profile in source_data["profiles"]:
            name = profile["name"]
            key = (source_key, name)
            profiles_map[key] = [agents_dir / f for f in profile.get("files", [])]
    return profiles_map


def resolve_agent_files(agent: dict, source_key: str, agents_json_dir: Path, profiles_map: dict) -> list:
    """
    Resolve the effective list of rule files for an agent.
    Profiles are resolved by (source, name) from the global profiles_map.
    apd.profiles entries may be strings (legacy) or objects with 'name' and 'source'.
    File paths in apd.files are relative to the agent's own agents.json directory.
    Returns list of absolute Paths.
    """
    files = []

    for profile_ref in agent["apd"].get("profiles", []):
        if isinstance(profile_ref, str):
            # Legacy format: string profile name resolved from own source
            key = (source_key, profile_ref)
        else:
            # New format: { "name": "...", "source": "..." }
            key = (profile_ref.get("source", source_key), profile_ref["name"])

        for f in profiles_map.get(key, []):
            files.append(f)

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


def sync_roo_environment(merged: dict, base_dir: Path, agents_dirs: dict) -> None:
    """
    Rebuild .roomodes and .roo/rules-{slug}/ from the merged agent definitions.
    Only updates entries that have changed.
    agents_dirs: { "shared": Path, "internal": Path, "project": Path }
    """
    roomodes_path = base_dir / ".roomodes"
    roo_dir = base_dir / ".roo"

    # Load existing .roomodes
    existing_roomodes = load_json(roomodes_path)
    existing_modes = {m["slug"]: m for m in existing_roomodes.get("customModes", [])}

    # Build global profiles map across all sources
    profiles_map = build_profiles_map(merged, agents_dirs)

    new_modes = []

    # Process internal and project agents (shared has no agents by convention)
    for source_key in ("internal", "project"):
        source_data = merged[source_key]
        agents_json_dir = agents_dirs[source_key]

        for agent in source_data["agents"]:
            slug = agent["roo"]["slug"]
            mode_entry = build_roomodes_entry(agent)
            new_modes.append(mode_entry)

            # Resolve rule files using the global profiles map
            rule_files = resolve_agent_files(agent, source_key, agents_json_dir, profiles_map)

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
# Public entry point
# ---------------------------------------------------------------------------

def run(base_dir: Path, registry_dir: Path, agent_framework_dir: Path) -> dict | None:
    """
    Execute steps 1, 2, and 3.
    Returns the merged agents dict on success, or None on slug conflict.
    """
    shared_agents_path = registry_dir / "shared/agents/agents.json"
    internal_agents_path = registry_dir / "internal/agents/agents.json"
    project_agents_path = registry_dir / "project/agents/agents.json"

    shared_data = load_agents_file(shared_agents_path)
    internal_data = load_agents_file(internal_agents_path)
    project_data = load_agents_file(project_agents_path)

    merged = merge_agents(shared_data, internal_data, project_data)
    if merged is None:
        return None

    sync_workspace(registry_dir / "shared/workspace", agent_framework_dir)
    sync_workspace(registry_dir / "internal/workspace", agent_framework_dir)
    sync_workspace(registry_dir / "project/workspace", agent_framework_dir)

    agents_dirs = {
        "shared": shared_agents_path.parent,
        "internal": internal_agents_path.parent,
        "project": project_agents_path.parent,
    }
    sync_roo_environment(merged, base_dir, agents_dirs)

    return merged
