import json
import os
import shutil

def safe_delete(path):
    if os.path.exists(path):
        shutil.rmtree(path) if os.path.isdir(path) else os.remove(path)

def copy_md_files_flat(src_dir, dst_dir):
    """Copies ONLY .md files from src_dir directly into dst_dir (flat structure)."""
    if not os.path.exists(src_dir):
        return
    os.makedirs(dst_dir, exist_ok=True)
    for file in os.listdir(src_dir):
        src_file = os.path.join(src_dir, file)
        dst_file = os.path.join(dst_dir, file)
        if os.path.isfile(src_file) and file.endswith(".md"):
            shutil.copy2(src_file, dst_file)

def main():
    base_dir = os.getcwd()
    registry_dir = os.path.join(base_dir, "agent_framework/registry")
    input_path = os.path.join(base_dir, "agent_framework/scripts/provisioner/input.json")

    if not os.path.exists(input_path):
        print("Provisioner input not found.")
        return

    with open(input_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    chosen_team = config.get("chosen_team")
    if not chosen_team:
        print("Error: No team chosen in input.json")
        return

    print("--- Phase 1: Wipe Total ---")
    safe_delete(os.path.join(base_dir, ".roo"))
    safe_delete(os.path.join(base_dir, ".roomodes"))
    safe_delete(os.path.join(base_dir, "agent_framework/memory"))

    os.makedirs(os.path.join(base_dir, "agent_framework/memory"), exist_ok=True)

    # Global inbox structure: draft/, unread/, read/ (only creates if not exists)
    inbox_dir = os.path.join(base_dir, "agent_framework/inbox")
    os.makedirs(os.path.join(inbox_dir, "internal_templates"), exist_ok=True)
    os.makedirs(os.path.join(inbox_dir, "draft"), exist_ok=True)
    os.makedirs(os.path.join(inbox_dir, "unread"), exist_ok=True)
    os.makedirs(os.path.join(inbox_dir, "read"), exist_ok=True)

    team_path = os.path.join(registry_dir, f"teams/{chosen_team}")
    with open(os.path.join(team_path, "agents.json"), 'r', encoding='utf-8') as f:
        team_agents = json.load(f).get("agents", [])

    final_modes = {"customModes": []}

    print("--- Processing Agents & Modes ---")

    # 1. Global Common Rules -> .roo/rules/
    global_common_src = os.path.join(registry_dir, "agents", "common")
    global_common_dst = os.path.join(base_dir, ".roo", "rules")
    copy_md_files_flat(global_common_src, global_common_dst)

    for agent in team_agents:
        slug = agent["slug"]
        path = agent["path"]

        # Base target for this agent's rules
        rules_target = os.path.join(base_dir, f".roo/rules-{slug}")

        # 2. Dynamic Hierarchical Common Rules Traverse
        parts = path.replace("\\", "/").split('/')
        current_src = os.path.join(registry_dir, "agents")

        # Loop through parent paths (excluding the agent's specific folder)
        for part in parts[:-1]:
            current_src = os.path.join(current_src, part)
            common_src = os.path.join(current_src, "common")
            copy_md_files_flat(common_src, rules_target)

        # 3. Agent Specific Files
        agent_src = os.path.join(registry_dir, "agents", *parts)
        copy_md_files_flat(agent_src, rules_target)

        # 4. Team Workflow (skipped for adp-orchestrator)
        if slug != "adp-orchestrator":
            copy_md_files_flat(team_path, rules_target)

        # 5. Build Mode directly from the agent's mode.json
        agent_mode_path = os.path.join(agent_src, "mode.json")
        if os.path.exists(agent_mode_path):
            with open(agent_mode_path, 'r', encoding='utf-8') as f:
                new_mode = json.load(f)
            new_mode["slug"] = slug
            final_modes["customModes"].append(new_mode)

    with open(os.path.join(base_dir, ".roomodes"), 'w', encoding='utf-8') as f:
        json.dump(final_modes, f, indent=2)

    print("--- Initializing Memory & Templates ---")
    for t_file in ["tech_stack.md", "decisions.md"]:
        src = os.path.join(registry_dir, f"internal_templates/{t_file}")
        dst = os.path.join(base_dir, f"agent_framework/memory/{t_file}")
        if os.path.exists(src):
            shutil.copy2(src, dst)

    for i_file in ["message_briefing.md", "message_report.md"]:
        src = os.path.join(registry_dir, f"internal_templates/{i_file}")
        dst = os.path.join(base_dir, f"agent_framework/inbox/internal_templates/{i_file}")
        if os.path.exists(src):
            shutil.copy(src, dst)

    # Auto-Reset Input
    with open(input_path, 'w', encoding='utf-8') as f:
        json.dump({"chosen_team": ""}, f, indent=2)

    print("--- APD Provisioning Complete. Input reset. ---")

if __name__ == "__main__":
    main()
