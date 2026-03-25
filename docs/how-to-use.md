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
python tools/new_project/main.py
```

You will be prompted for:

1. **Destination folder** — the parent directory where the project will be created (e.g., `C:/Projects` or `/home/user/projects`).
2. **Project type:**
   - `[1] Local` — creates a new empty directory.
   - `[2] Remote` — clones an existing Git repository.
3. **Project name** (local only) or **Git SSH URL** (remote only).

The tool will:
- Copy the APD skeleton into the new project directory.
- Generate `agent_framework/config.json` with project metadata.
- Call `sync_registry.run()` directly to generate the initial agent files (`.roomodes`, `.roo/rules-*/`, workspace files).

**Example output:**
```
=== APD Project Initializer (v2.0.0) ===
Destination folder (full path): C:/Projects
Is the project local or remote?
[1] Local
[2] Remote
Choice (1/2): 1
Project name: my-api

[1/3] Creating local directory: C:/Projects/my-api
[2/3] Copying framework skeleton...
[3/3] Generating config.json...
[4/5] Syncing registry (agents, workspace, roo environment)...

✅ APD successfully initialized at: C:/Projects/my-api

[5/5] Opening project in VS Code: C:/Projects/my-api
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

1. Open `agent_framework/templates/project_briefing/template.md`.
2. Fill in the `<message_body>` section with your project description, tech stack, and success criteria.
3. Copy the entire filled-in template (including the `<message_metadata>` block).

**Tips for a good briefing:**
- Be specific about the tech stack and constraints.
- Define clear, testable success criteria.
- Keep it focused — the Headhunter will handle team design and environment setup.

---

## Step 4: Start the Orchestrator

In Roo, switch to the **APD Orchestrator** mode and **paste your filled-in briefing message** directly in the chat. The message must be in the standard XML format:

```
<message_metadata>
from: user
to: apd-headhunter
subject: New Project Briefing
</message_metadata>

<message_body>
(your briefing content here)
</message_body>
```

The Orchestrator will:
1. Write your message to `agent_framework/inbox/draft/message.md`.
2. Run `cycle/main.py` — sync the environment and promote the message.
3. Detect the message addressed to the Headhunter and invoke it.

The Headhunter will then:
1. Read your briefing from the `new_task` instructions.
2. Design the appropriate team.
3. Write agent instructions and `agents.json` to provision the full environment.
4. Return a task briefing to the first agent via `attempt_completion`.

The Orchestrator resumes, `cycle/main.py` picks up the new `agents.json` and rebuilds the Roo environment, invokes the next agent with the message as instructions, and the cycle continues autonomously.

---

## Step 5: The Autonomous Cycle

Once started, the system runs without human intervention. The core flow is:

```
Orchestrator runs cycle → Headhunter inbox has message
  → Headhunter designs team, writes agents.json, returns task briefing via attempt_completion
Orchestrator runs cycle → rebuilds .roomodes + .roo/rules-*/ → promotes message → agent receives it via new_task
  → Agent does its work, returns report via attempt_completion
Orchestrator runs cycle → ... (cycle continues per team routing table)
Orchestrator runs cycle → to: user → PAUSE
```

The exact agents involved and the routing between them depend on the team that was provisioned. Each team defines its own routing table in `agent_framework/registry/project/agents/rules/team_instructions.md`.

**You do not need to do anything** during this cycle. The agents handle implementation, testing, and bug-fixing autonomously.

---

## Step 6: Human Intervention

The Orchestrator pauses and notifies you when `cycle/main.py` returns `user` — meaning an agent sent a message with `to: user`. This happens when:

- An agent has completed its work and the result is ready for your review.
- An agent needs input it cannot determine autonomously (e.g., a major architectural decision).
- The project is finished.

**To respond:**
1. Read the message displayed by the Orchestrator (or open `agent_framework/inbox/unread/message.md`).
2. Take whatever action is needed (review the output, make a decision, etc.).
3. If the cycle should continue, paste your reply in the Orchestrator chat in the standard XML format:
   ```
   <message_metadata>
   from: user
   to: {next-agent-slug}
   subject: {brief description}
   </message_metadata>

   <message_body>
   (your reply here)
   </message_body>
   ```
   The Orchestrator will write it to `draft/`, run `cycle/main.py`, and invoke the next agent automatically.

---

## Tips

### Viewing Message History
All processed messages are preserved in `agent_framework/inbox/read/`. Each entry is a timestamped subfolder named `{YYYYMMDD_HHMMSS}_{from}_{to}/` containing the archived `message.md` and any attachments.

### Checking Technical State
- `agent_framework/memory/tech_stack.md` — the canonical record of the project's technology choices (available when using the `simple_code_project` example team or any team that includes it).
- `agent_framework/memory/decisions.md` — a log of significant architectural decisions made during the project.
- `agent_framework/memory/lessons_learned.md` — a log of recurring errors (technical and behavioral) and their solutions, shared across all agents to prevent repeated mistakes.

### Re-provisioning the Environment
If you need to change the team or reset the environment, update `agent_framework/registry/project/agents/agents.json` with the new roster. On the next Orchestrator loop, `cycle/main.py` will automatically detect the change and rebuild `.roomodes` and `.roo/rules-{slug}/` for the new team.

> **Warning:** Removing an agent from `agents.json` will delete its `.roo/rules-{slug}/` directory on the next cycle. Any message currently in `inbox/unread/` addressed to that agent will be orphaned.

### Debugging Agent Behavior
If an agent behaves unexpectedly, check:
- The agent's rules in `.roo/rules-{slug}/` — these are the actual instructions Roo is using.
- The message history in `agent_framework/inbox/read/` — each archived folder contains the message that was processed.
- The `agent_framework/memory/decisions.md` for any logged decisions.
- The `agent_framework/memory/lessons_learned.md` for known errors and their solutions.
- The `agent_framework/registry/project/agents/agents.json` — verify the agent roster and profile assignments are correct.
