# APD Agents

## Overview

APD agents are specialized AI modes powered by the Roo VS Code extension. Each agent has a fixed role, a defined domain (the files it may touch), and communicates exclusively through the filesystem inbox. The agent roster is defined by two `agents.json` files that `cycle/main.py` merges on every Orchestrator loop.

There are two agent categories:

| Category | Description |
|---|---|
| **Internal** | Always present regardless of project. Defined in `registry/internal/agents/agents.json`. Manages the pipeline itself. |
| **Project** | Defined at runtime in `registry/project/agents/agents.json`. Written by the Headhunter during team provisioning. Performs actual project work. |

---

## Agent Reference

### `apd-orchestrator` — Orchestrator

| Property | Value |
|---|---|
| **Slug** | `apd-orchestrator` |
| **Category** | Internal |
| **Roo Group** | `command` |
| **Domain** | No file writes — read-only pipeline manager |

**Role:** The infrastructure manager. Its sole purpose is to run the cycle script and delegate execution to the correct agent or pause for human intervention.

**Inputs:** None — the Orchestrator does not have an inbox and does not read from one. It is triggered by the human typing `Start`.

**Outputs:** Invokes sub-agents via Roo's `new_task` tool with the command `Start`.

**Execution Loop:**
1. Run `python agent_framework/scripts/internal/cycle/main.py`.
2. If output starts with `APD_CONFLICT:` → pause and notify the human to resolve the agent slug conflict.
3. If output is `user` → pause and notify the human.
4. If output is `empty` → report "Queue Empty" and stop.
5. If output is an agent slug → invoke that agent via `new_task`.
6. When the sub-task returns `Done` → repeat from step 1.

**Constraints:**
- Does not read files, execute logic scripts, or write code.
- Relies entirely on `cycle/main.py` output for routing decisions.

---

### `apd-headhunter` — Boot Architect

| Property | Value |
|---|---|
| **Slug** | `apd-headhunter` |
| **Category** | Project / Initialization |
| **Domain** | `agent_framework/registry/project/` |

**Role:** The initialization specialist. Transforms a project briefing into a fully provisioned execution environment by designing the team and writing the agent roster.

**Inputs:** Reads from `agent_framework/inbox/unread/` — expects a project briefing in `message.md`.

**Outputs:** Writes a task briefing to `agent_framework/inbox/draft/message.md` addressed to the first operational agent, then runs `post_work`.

**Execution Pipeline:**
1. **Read Briefing:** Read the project briefing from `agent_framework/inbox/unread/message.md`.
2. **Design the Team:** Think about the ideal team for the project. Use `agent_framework/registry/examples/` as reference.
3. **Create Agent Instructions:** For each operational agent, create an instructions file at `agent_framework/registry/project/agents/{agent-name}/instructions.md`.
4. **Create Team Rules:** Create a team rules file at `agent_framework/registry/project/agents/rules/`.
5. **Write `agents.json`:** Write `agent_framework/registry/project/agents/agents.json` with the full agent roster using the APD `agents.json` format (profiles + agents). Create a dedicated profile for the team that includes the team rules file.
6. **Handoff:** Write a task briefing to `agent_framework/inbox/draft/message.md` addressed to the first operational agent.

---

### `apd-coder` — Senior Software Engineer *(example team)*

| Property | Value |
|---|---|
| **Slug** | `apd-coder` |
| **Category** | Project / Development |
| **Domain** | `src/` (application source code) |

**Role:** Implements features and fixes bugs based on the task briefing and the project's tech stack. Writes production-ready code strictly within the `src/` directory.

**Inputs:** Reads from `agent_framework/inbox/unread/` — expects a task briefing in `message.md` with objective, success criteria, and constraints.

**Outputs:** Writes an execution report to `agent_framework/inbox/draft/message.md` (addressed `to: apd-tester`) upon completion, or escalates (`to: user`) if a blocker is encountered.

**Execution Pipeline:**
1. Read the task briefing from `unread/`.
2. Implement the required feature or bug fix in `src/`.
3. Write a report to `draft/message.md`.
4. Run `post_work` and output `Done`.

> **Note:** This agent is part of the built-in `simple_code_project` example. Real projects will have agents defined by the Headhunter with custom slugs and instructions.

---

### `apd-tester` — QA Engineer *(example team)*

| Property | Value |
|---|---|
| **Slug** | `apd-tester` |
| **Category** | Project / Development |
| **Domain** | `tests/` (test files) |

**Role:** Validates the implementation by creating and running tests. Determines whether the feature passes or fails and routes accordingly.

**Inputs:** Reads from `agent_framework/inbox/unread/` — expects an execution report in `message.md` from the coder.

**Outputs:** Writes a test report to `agent_framework/inbox/draft/message.md` addressed `to: user` (tests passed) or `to: apd-coder` (bug found).

**Execution Pipeline:**
1. Read the execution report from `unread/`.
2. Create or update test files in `tests/`.
3. Run the test suite and validate results.
4. Write a report to the appropriate recipient based on the outcome.
5. Run `post_work` and output `Done`.

> **Note:** This agent is part of the built-in `simple_code_project` example. Real projects will have agents defined by the Headhunter with custom slugs and instructions.

---

## Profiles-Based Rules System

Every agent's effective ruleset is assembled by `cycle/main.py` from the **profiles** declared in its `agents.json` source file. Profiles are scoped by source (`shared`, `internal`, or `project`) and referenced by agents using `{ "name": "...", "source": "..." }` objects.

### Shared registry profiles (`registry/shared/agents/agents.json`)

The shared registry defines the two core profiles available to **all agents** regardless of which source (`internal` or `project`) they belong to:

| Profile | Files | Applied to |
|---|---|---|
| `apd-core` | `rules/global_rules.md`, `rules/xml_rules.md` | All agents (internal + project) |
| `operational` | `rules/operational_rules.md` | All operational agents |

The `internal` and `project` registries do **not** define their own `apd-core` or `operational` profiles. They reference the shared ones via `{ "name": "apd-core", "source": "shared" }`.

Team-specific profiles (e.g., `simple-team`) are defined locally in the example or project `agents.json` and reference files relative to that file's directory.

Each agent also lists its own specific instruction file under `apd.files`, which is appended after all profile files.

**Resolution order per agent:**
1. Files from each profile in `apd.profiles` (in order), resolved from the profile's declared source.
2. Files from `apd.files` (agent-specific instructions), resolved relative to the agent's own `agents.json` directory.

All resolved files are copied into `.roo/rules-{slug}/`.

---

## Key Behavioral Rules

### Full Autonomy
Agents **never ask the user for confirmation**. The only way an agent communicates with the user is by writing a message to `inbox/draft/message.md` with `to: user` — the Orchestrator will then pause and notify the human. This is enforced by [`global_rules.md`](../skeleton/agent_framework/registry/shared/agents/rules/global_rules.md).

### The "Done" Protocol
Every operational agent must conclude its task by calling `attempt_completion` with `result` set to exactly `"Done"` — no punctuation, no summary, no additional text. This signals the Orchestrator that the sub-task has completed and the loop should continue.

### Post-Work Mandatory
Before outputting `Done`, every operational agent **must**:
1. Write the outgoing message to `agent_framework/inbox/draft/message.md` with valid `from`, `to`, and `subject` metadata fields.
2. Run `python agent_framework/scripts/shared/post_work/main.py`.
3. If the script prints an error, correct `draft/message.md` and re-run the command.

This validates the draft, archives the current `unread/` contents into `read/`, and promotes the draft to `unread/` for the next agent.

### No Direct Mode Switching
Agents **cannot** invoke other agents directly or switch Roo modes. Handoff is achieved solely by writing a message to `agent_framework/inbox/draft/` and running `post_work`. The Orchestrator detects the new `unread/message.md` on its next cycle and performs the invocation.
