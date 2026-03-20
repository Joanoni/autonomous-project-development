#!/usr/bin/env python3
import shutil
import subprocess
import json
import sys
from pathlib import Path

# Path Configuration
SCRIPT_DIR = Path(__file__).parent.resolve()
REPO_ROOT = SCRIPT_DIR.parent.parent.resolve()
SKELETON_DIR = REPO_ROOT / "skeleton"
CONFIG_FILE = SCRIPT_DIR / "config.json"

def load_config() -> dict:
    """Load config.json from the script directory. Returns empty dict on failure."""
    if CONFIG_FILE.exists():
        try:
            return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {}

def run(cmd: list[str], cwd: Path) -> None:
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout.rstrip())
    if result.returncode != 0:
        raise RuntimeError(f"Command error: {' '.join(cmd)}\n{result.stderr}")

def framework_extra_steps(root: Path, chosen_team: str) -> None:
    print("[4/4] Executing framework provisioner...")

    # Write chosen_team into the provisioner input before running
    provisioner_input = root / "agent_framework/scripts/provisioner/input.json"
    provisioner_input.write_text(json.dumps({"chosen_team": chosen_team}, indent=2), encoding="utf-8")

    # Using sys.executable ensures we use the same Python environment running this script
    provisioner_cmd = [sys.executable, "agent_framework/scripts/provisioner/main.py"]
    
    try:
        print("  → Running Provisioner...")
        run(provisioner_cmd, cwd=root)
    except RuntimeError as e:
        print(f"ERROR executing framework provisioner script:\n{e}")
        sys.exit(1)

def main() -> None:
    print("=== APD Project Initializer (v1.0.0) ===")
    
    config = load_config()
    default_dest = config.get("default_destination", "").strip()
    default_team = config.get("default_team", "").strip()

    if default_dest:
        dest_input = input(f"Destination folder (full path) [{default_dest}]: ").strip()
        dest = dest_input if dest_input else default_dest
    else:
        dest = input("Destination folder (full path): ").strip()

    if default_team:
        team_input = input(f"Team to provision [{default_team}]: ").strip()
        chosen_team = team_input if team_input else default_team
    else:
        chosen_team = input("Team to provision: ").strip()
    
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
        
        print(f"\n[1/4] Cloning remote repository into: {root}")
        try:
            run(["git", "clone", git_url, str(root)], cwd=dest_path)
        except RuntimeError as e:
            print(f"ERROR cloning repository:\n{e}")
            sys.exit(1)
    else:
        project_type = "local"
        project_name = input("Project name: ").strip()
        root = dest_path / project_name
        
        print(f"\n[1/4] Creating local directory: {root}")
        root.mkdir(parents=True, exist_ok=True)
    
    # Step 2: Copy Framework
    print("[2/4] Copying framework skeleton...")
    if SKELETON_DIR.exists():
        # Copy recursively, injecting the skeleton files into the directory
        shutil.copytree(SKELETON_DIR, root, dirs_exist_ok=True)
    else:
        print(f"ERROR: Skeleton folder not found at {SKELETON_DIR}")
        sys.exit(1)

    # Step 3: Final Configuration
    print("[3/4] Generating config.json...")
    agent_framework_dir = root / "agent_framework"
    agent_framework_dir.mkdir(exist_ok=True)
    
    config_out = {
        "project_name": project_name,
        "framework_name": "APD",
        "framework_version": "1.0.0",
        "project_type": project_type
    }
    (agent_framework_dir / "config.json").write_text(json.dumps(config_out, indent=2))
    
    # Step 4: Provisioning
    framework_extra_steps(root, chosen_team)
    
    print(f"\n✅ APD successfully initialized at: {root}")

if __name__ == "__main__":
    main()
