# APD Tools

## Overview

APD tools are Python utilities that power the framework's automation. They fall into two groups:

| Group | Tools | Purpose |
|---|---|---|
| **Root Entry Point** | `tools/new_project/main.py` | Creates a new APD-managed project |
| **Root Entry Point** | `tools/git_flow/main.py` | Commits, merges, and resets the git flow for a stable release |
| **Runtime Tools** | `cycle/main.py` | Supports the autonomous agent loop |

Runtime tools live inside a generated project under `agent_framework/tools/` and are run from the **project root** (not from the tool's own directory). They are synced from the registry workspace on every cycle.

---

## Root Entry Point

### `tools/new_project/main.py`

**Location:** [`tools/new_project/main.py`](../tools/new_project/main.py)

**Purpose:** Interactive CLI wizard that creates a new APD-managed project by copying the skeleton and bootstrapping the runtime environment.

**Configuration:** [`tools/new_project/input.json`](../tools/new_project/input.json)

Before running the wizard, you can set a default destination folder in `input.json` so you don't have to type it every time:

```json
{
  "default_destination": "/path/to/your/projects"
}
```

When `default_destination` is set, the prompt will show it as the default value and accept it with a simple Enter keypress. Leave the field as an empty string `""` to always be prompted.

**Inputs (interactive prompts):**
1. Destination folder (full path) — pre-filled from `input.json` if `default_destination` is set
2. Project type: `[1] Local` or `[2] Remote`
3. If local: project name
4. If remote: Git repository SSH URL (project name is derived automatically)

**Outputs:**
- A new project directory at `{destination}/{project_name}/`
- `agent_framework/config.json` with project metadata
- All skeleton files copied into the project root
- A fully bootstrapped runtime environment (`.roomodes`, `.roo/rules-*/`, `agent_framework/inbox/`, `agent_framework/memory/`)

**Steps executed:**
1. `[1/5]` Create local directory or clone remote Git repository.
2. `[2/5]` Copy the `skeleton/` directory into the project root (`shutil.copytree`).
3. `[3/5]` Generate `agent_framework/config.json`.
4. `[4/5]` Call `sync_registry.run()` directly to generate initial agent files.
5. `[5/5]` Open the generated project in VS Code (`code {project_path}`).

**Side effects:** None on the APD repository itself. All changes are made in the destination directory.

**When called:** Manually by the developer, once per project.

---

## Root Entry Point

### `tools/git_flow/main.py`

**Location:** [`tools/git_flow/main.py`](../tools/git_flow/main.py)

**Purpose:** Automates the full git release flow — commits and pushes the current branch, merges it into `main`, cleans up the branch locally and remotely, creates a fresh `improvements` branch, and resets `input.json` to empty strings.

**Configuration:** [`tools/git_flow/input.json`](../tools/git_flow/input.json)

Fill in all three fields before running:

```json
{
  "current_branch": "improvements",
  "commit_message": "your commit message here",
  "merge_message": "your merge message here"
}
```

**Inputs:** Read from `tools/git_flow/input.json` — no interactive prompts.

| Field | Description |
|---|---|
| `current_branch` | The branch to commit, push, and merge into `main` |
| `commit_message` | Message for the commit on the current branch |
| `merge_message` | Message for the `--no-ff` merge commit into `main` |

**Steps executed:**
1. `git add . && git commit -m "{commit_message}" && git push --set-upstream origin {current_branch}`
2. `git checkout main && git merge {current_branch} --no-ff -m "{merge_message}" && git push origin main && git branch -d {current_branch} && git push origin --delete {current_branch}`
3. `git checkout -b improvements` — recreates the improvements branch for the next cycle; resets all `input.json` fields to empty strings.

**Side effects:**
- Pushes commits to the remote repository.
- Deletes `{current_branch}` both locally and on the remote.
- Creates a new local `improvements` branch.
- Resets `tools/git_flow/input.json` fields to `""`.

**When called:** Manually by the developer when a branch is ready to be merged into `main`.

---

## Runtime Tools

### `cycle/main.py`

**Location (registry source):** [`skeleton/agent_framework/registry/internal/workspace/tools/internal/cycle/main.py`](../skeleton/agent_framework/registry/internal/workspace/tools/internal/cycle/main.py)

**Location (in generated project):** `agent_framework/tools/internal/cycle/main.py`

**Purpose:** The core runtime tool. Runs every time the Orchestrator starts its loop. Performs five steps in order:
1. **Merge agents** — loads `registry/shared/agents/agents.json`, `registry/internal/agents/agents.json`, and `registry/project/agents/agents.json`, checks for slug conflicts between internal and project agents, and produces a merged agent roster.
2. **Sync workspace** — copies files from `registry/shared/workspace/`, `registry/internal/workspace/`, and `registry/project/workspace/` (in that order) into `agent_framework/`, keeping the newer version of any file that already exists.
3. **Sync Roo environment** — rebuilds `.roomodes` and `.roo/rules-{slug}/` from the merged agent definitions. Only updates entries that have changed (compares mtimes and mode entries).
4. **Promote messages** — if `inbox/draft/` has content: archives the current `inbox/unread/` contents into a timestamped folder inside `inbox/read/` (skipped if `unread/` contains only a `.gitkeep`), then moves all files from `draft/` into `unread/`.
5. **Scan inbox** — reads `agent_framework/inbox/unread/message.md` and returns the `to` field value.

**Input:** None — reads the filesystem directly. The Orchestrator writes `inbox/draft/message.md` before calling this tool.

**Output (stdout, last line):**

| Output | Meaning |
|---|---|
| `APD_CONFLICT:{slug}` | Duplicate slug detected between `internal` and `project` `agents.json` |
| `user` | `agent_framework/inbox/unread/message.md` exists and its `to` field is `user` |
| `{agent-slug}` | `agent_framework/inbox/unread/message.md` exists and its `to` field is `{agent-slug}` |
| `empty` | `agent_framework/inbox/unread/message.md` does not exist or has no `to` field |

**Side effects:**
- Updates `.roomodes` if the agent roster has changed.
- Rebuilds `.roo/rules-{slug}/` for any agent whose rules or mode entry have changed.
- Syncs new or updated workspace files into `agent_framework/`.
- Archives `inbox/unread/` and promotes `inbox/draft/` → `inbox/unread/` when a draft message is present.

**When called:**
- By `tools/new_project/main.py` during initial project creation.
- By `apd-orchestrator` at the start of every loop iteration.

---

## Tool Relationships

```mermaid
sequenceDiagram
    participant HU as human (or agent)
    participant OR as apd-orchestrator
    participant CY as cycle/main.py
    participant AG as next agent

    HU-->>OR: XML message (chat or attempt_completion result)

    loop Orchestrator Loop
        OR->>OR: Writes XML to inbox/draft/message.md
        OR->>CY: python agent_framework/tools/internal/cycle/main.py
        Note over CY: 1. Merge agents.json (shared + internal + project)
        Note over CY: 2. Sync workspace files
        Note over CY: 3. Sync .roomodes + .roo/rules-{slug}/
        Note over CY: 4. Archive unread→read/ → promote draft→unread/
        Note over CY: 5. Scan inbox/unread/message.md
        CY-->>OR: "agent-slug" (or user / empty / APD_CONFLICT:slug)
        OR->>AG: new_task(instructions = XML message)
        AG->>AG: Does work
        AG-->>OR: attempt_completion(result = XML message)
    end
```
