#!/usr/bin/env python3
import shutil
import json
import subprocess
import sys
from pathlib import Path

# Path Configuration
SCRIPT_DIR = Path(__file__).parent.resolve()
REPO_ROOT = SCRIPT_DIR.parent.parent.resolve()
SKELETON_DIR = REPO_ROOT / "skeleton"
INPUT_FILE = SCRIPT_DIR / "input.json"

def load_input() -> dict:
    """Load input.json from the script directory. Returns empty dict on failure."""
    if INPUT_FILE.exists():
        try:
            return json.loads(INPUT_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {}

def main() -> None:
    print("=== APD Project Initializer (v2.0.0) ===")
    
    config = load_input()
    default_dest = config.get("default_destination", "").strip()

    if default_dest:
        dest_input = input(f"Destination folder (full path) [{default_dest}]: ").strip()
        dest = dest_input if dest_input else default_dest
    else:
        dest = input("Destination folder (full path): ").strip()
    
    dest_path = Path(dest).expanduser().resolve()
    dest_path.mkdir(parents=True, exist_ok=True)
    
    while True:
        choice = input("Is the project local or remote?\n[1] Local\n[2] Remote\nChoice (1/2): ").strip()
        if choice in ['1', '2']:
            break
        print("Invalid choice. Please enter 1 or 2.")
        
    # Step 1: Create structure or Clone Repository
    if choice == '2':
        project_type = "remote"
        git_url = input("Git repository SSH URL: ").strip()
        
        # Automatically derive project name from the Git URL
        project_name = git_url.rstrip('/').split('/')[-1]
        if project_name.endswith('.git'):
            project_name = project_name[:-4]
            
        root = dest_path / project_name
        
        print(f"\n[1/3] Cloning remote repository into: {root}")
        result = subprocess.run(["git", "clone", git_url, str(root)], cwd=dest_path, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"ERROR cloning repository:\n{result.stderr}")
            sys.exit(1)
    else:
        project_type = "local"
        project_name = input("Project name: ").strip()
        root = dest_path / project_name
        
        print(f"\n[1/3] Creating local directory: {root}")
        root.mkdir(parents=True, exist_ok=True)
    
    # Step 2: Copy Framework Skeleton
    print("[2/3] Copying framework skeleton...")
    if SKELETON_DIR.exists():
        shutil.copytree(SKELETON_DIR, root, dirs_exist_ok=True)
    else:
        print(f"ERROR: Skeleton folder not found at {SKELETON_DIR}")
        sys.exit(1)

    # Step 3: Generate config.json
    print("[3/3] Generating config.json...")
    agent_framework_dir = root / "agent_framework"
    agent_framework_dir.mkdir(exist_ok=True)
    
    config_out = {
        "project_name": project_name,
        "framework_name": "APD",
        "framework_version": "2.0.0",
        "project_type": project_type
    }
    (agent_framework_dir / "config.json").write_text(json.dumps(config_out, indent=2))
    
    # Step 4: Run sync_registry to generate initial agent files in the new project
    cycle_dir = root / "agent_framework/registry/internal/workspace/scripts/internal/cycle"
    print("[4/4] Syncing registry (agents, workspace, roo environment)...")
    sys.path.insert(0, str(cycle_dir))
    import sync_registry
    merged = sync_registry.run(root, root / "agent_framework/registry", root / "agent_framework")
    if merged is None:
        print("WARNING: sync_registry detected a slug conflict.")
    
    print(f"\n✅ APD successfully initialized at: {root}")
    print("   Open the project in VS Code, switch to APD Orchestrator mode, and type 'Start'.")

    # Step 5: Open the new project in VS Code
    print(f"\n[5/5] Opening project in VS Code: {root}")
    subprocess.run(["code", str(root)], shell=True)

if __name__ == "__main__":
    main()
