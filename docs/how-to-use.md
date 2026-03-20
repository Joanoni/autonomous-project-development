# How to Use APD

This guide walks you through creating a new APD-managed project and running the autonomous development cycle from start to finish.

---

## Prerequisites

| Requirement | Notes |
|---|---|
| **Python 3.10+** | Must be available on your `PATH` |
| **VS Code** | Any recent version |
| **Roo extension** | Install from the VS Code Marketplace: search "Roo Code" |
| **Git** | Required only for remote (cloned) projects |
| **An LLM API key** | Configured in Roo's settings (e.g., Anthropic, OpenAI) |

---

## Step 1: Create a New Project

From the APD repository root, run:

```bash
python new_project.py
```

You will be prompted for:

1. **Destination folder** — the parent directory where the project will be created (e.g., `C:/Projects` or `/home/user/projects`).
2. **Project type:**
   - `[1] Local` — creates a new empty directory.
   - `[2] Remote` — clones an existing Git repository.
3. **Project name** (local only) or **Git SSH URL** (remote only).

The script will:
- Copy the APD skeleton into the new project directory.
- Generate `.apd/config.json` with project metadata.
- Run the provisioner pipeline (Scout + Assembler) to bootstrap the initial environment.

**Example output:**
```
=== APD Project Initializer (v1.0.0) ===
Destination folder (full path): C:/Projects
Is the project local or remote?
[1] Local
[2] Remote
Choice (1/2): 1
Project name: my-api

[1/4] Creating local directory: C:/Projects/my-api
[2/4] Copying framework skeleton...
[3/4] Generating config.json...
[4/4] Executing framework extra steps (Scout & Assembler)...

✅ APD successfully initialized at: C:/Projects/my-api
```

---

## Step 2: Open the Project in VS Code

Open the **generated project folder** (not the APD repository) in VS Code:

```bash
code C:/Projects/my-api
```

Roo will automatically detect the `.roomodes` file and load the custom agent modes. You should see the APD agents available in Roo's mode selector.

> **Important:** Open the generated project root, not a subdirectory. Roo reads `.roomodes` from the workspace root.

---

## Step 3: Write a Project Briefing

Before starting the autonomous cycle, you need to give the Headhunter its initial instructions.

1. Use the template at `agent_framework/templates/team_briefing/template.md` as a starting point.
2. Create `agent_framework/inbox/unread/message.md` using the `<message_metadata>` block format followed by your briefing content:

```
<message_metadata>
from: user
to: apd-headhunter
subject: Project Briefing
</message_metadata>

Your briefing content here...
```

**Tips for a good briefing:**
- Be specific about the tech stack and constraints.
- Define clear, testable success criteria.
- Keep it focused — the Headhunter will handle team selection and environment setup.

---

## Step 4: Start the Orchestrator

In Roo, switch to the **APD Orchestrator** mode and type:

```
Start
```

That's it. The Orchestrator will begin its loop:
1. Scan the inbox queue.
2. Detect the message in the Headhunter's inbox.
3. Invoke the Headhunter.

The Headhunter will then:
1. Read your briefing.
2. Select the appropriate team.
3. Run Scout and Assembler to provision the full environment.
4. Write a task briefing to the first agent's inbox.
5. Output `Done`.

The Orchestrator resumes, detects the next agent's message, invokes it, and the cycle continues autonomously.

---

## Step 5: The Autonomous Cycle

Once started, the system runs without human intervention. The core flow is:

```
Orchestrator scans → Headhunter inbox has message
  → Headhunter provisions environment, writes to next agent's inbox → Done
Orchestrator scans → agent inbox has message
  → Agent does its work, writes to next agent's inbox → Done
Orchestrator scans → ... (cycle continues per team workflow)
Orchestrator scans → user inbox has message → PAUSE
```

The exact agents involved and the routing between them depend on the team that was provisioned. Each team defines its own workflow.

**You do not need to do anything** during this cycle. The agents handle implementation, testing, and bug-fixing autonomously.

---

## Step 6: Human Intervention

The Orchestrator pauses and notifies you when `scan_inbox` returns `user` — meaning `agent_framework/inbox/unread/message.md` has `to: user`. This happens when:

- An agent has completed its work and the result is ready for your review.
- An agent needs input it cannot determine autonomously (e.g., a major architectural decision).
- The project is finished.

**To respond:**
1. Read the message in `agent_framework/inbox/unread/message.md`.
2. Take whatever action is needed (review the output, make a decision, etc.).
3. If the cycle should continue, write your reply to `agent_framework/inbox/unread/message.md` (replacing it) with the appropriate `to:` field pointing to the next agent, or write a new `message.md` to `agent_framework/inbox/draft/` and run `post_work` manually.
4. Type `Start` in the Orchestrator again to resume the cycle.

---

## Tips

### Viewing Message History
All processed messages are preserved in `agent_framework/inbox/read/`. Each entry is a timestamped subfolder named `{YYYYMMDD_HHMMSS}_{from}_{to}/` containing the archived `message.md` and any attachments.

### Checking Technical State
- `agent_framework/memory/tech_stack.md` — the canonical record of the project's technology choices.
- `agent_framework/memory/decisions.md` — a log of significant architectural decisions made during the project.

### Re-provisioning the Environment
If you need to change the team or reset the environment, you can manually trigger the provisioner:
1. Set `chosen_team` in `agent_framework/scripts/provisioner/scout/input.json`.
2. Run `python agent_framework/scripts/provisioner/scout/main.py` from the project root.
3. Fill in the slots in `agent_framework/scripts/provisioner/assembler/input.json`.
4. Run `python agent_framework/scripts/provisioner/assembler/main.py` from the project root.

> **Warning:** The assembler performs a full wipe of `.roo/`, `.roomodes`, `inbox/`, and `memory/`. Any message currently in `inbox/unread/` will be lost.

### Debugging Agent Behavior
If an agent behaves unexpectedly, check:
- The agent's rules in `.roo/rules-{slug}/` — these are the actual instructions Roo is using.
- The message history in `agent_framework/inbox/read/` — each archived folder contains the message that was processed.
- The `agent_framework/memory/decisions.md` for any logged decisions.
