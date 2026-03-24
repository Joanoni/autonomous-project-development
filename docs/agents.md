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
| **Domain** | `agent_framework/inbox/draft/` (writes draft messages only) |

**Role:** The infrastructure manager. Its sole purpose is to run the cycle script and delegate execution to the correct agent or pause for human intervention.

**Inputs:** Receives an XML message in the standard format — either pasted by the human in chat (first run) or returned by an agent via `attempt_completion` (subsequent runs).

**Outputs:** Invokes sub-agents via Roo's `new_task` tool, passing the full XML message as task instructions.

**Execution Loop:**
1. Write the received XML message verbatim to `agent_framework/inbox/draft/message.md`.
2. Run `python agent_framework/scripts/internal/cycle/main.py`.
3. If output starts with `APD_CONFLICT:` → pause and notify the human to resolve the agent slug conflict.
4. If output is `user` → pause and notify the human.
5. If output is `empty` → report "Queue Empty" and stop.
6. If output is an agent slug → invoke that agent via `new_task`, passing the full XML message as instructions.
7. When the sub-task returns its result (a new XML message) → repeat from step 1.

**Constraints:**
- Writes only `agent_framework/inbox/draft/message.md` — no other file writes.
- Relies entirely on `cycle/main.py` output for routing decisions.
- Relies entirely on the received message for content — never modifies or summarizes it.
- Does not populate any `input.json` — the cycle script reads the filesystem directly.

---

### `apd-headhunter` — Boot Architect

| Property | Value |
|---|---|
| **Slug** | `apd-headhunter` |
| **Category** | Project / Initialization |
| **Domain** | `agent_framework/registry/project/` |

**Role:** The initialization specialist. Transforms a project briefing into a fully provisioned execution environment by designing the team and writing the agent roster.

**Inputs:** Receives the project briefing via `new_task` instructions in the standard XML message format (`<message_metadata>` + `<message_body>`).

**Outputs:** Returns a task briefing via `attempt_completion` in the standard XML message format, addressed to the first operational agent.

**Execution Pipeline:**
1. **Read Briefing:** Read the project briefing from the `<message_body>` block in the `new_task` instructions.
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

**Inputs:** Receives the task briefing via `new_task` instructions in the standard XML message format (`<message_metadata>` + `<message_body>`).

**Outputs:** Returns an execution report via `attempt_completion` in the standard XML message format, addressed `to: apd-tester` upon completion, or `to: user` if a blocker is encountered.

**Execution Pipeline:**
1. Read the task briefing from the `new_task` instructions.
2. Implement the required feature or bug fix in `src/`.
3. Return a report via `attempt_completion` in the standard XML message format.

> **Note:** This agent is part of the built-in `simple_code_project` example. Real projects will have agents defined by the Headhunter with custom slugs and instructions.

---

### `apd-tester` — QA Engineer *(example team)*

| Property | Value |
|---|---|
| **Slug** | `apd-tester` |
| **Category** | Project / Development |
| **Domain** | `tests/` (test files) |

**Role:** Validates the implementation by creating and running tests. Determines whether the feature passes or fails and routes accordingly.

**Inputs:** Receives the execution report via `new_task` instructions in the standard XML message format (`<message_metadata>` + `<message_body>`).

**Outputs:** Returns a test report via `attempt_completion` in the standard XML message format, addressed `to: user` (tests passed) or `to: apd-coder` (bug found).

**Execution Pipeline:**
1. Read the execution report from the `new_task` instructions.
2. Create or update test files in `tests/`.
3. Run the test suite and validate results.
4. Return a report via `attempt_completion` in the standard XML message format addressed to the appropriate recipient.

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

### Lessons-Driven Execution
At the start of every task, agents read `agent_framework/memory/lessons_learned.md` alongside `agent_framework/memory/decisions.md`. When an error is encountered and resolved — whether technical (code, dependencies, commands) or behavioral (protocol, message format) — the agent appends an entry to `lessons_learned.md` before concluding the task. This prevents the same mistakes from recurring across sessions.

### Full Autonomy
Agents **never ask the user for confirmation**. The only way an agent communicates with the user is by setting `to: user` in the `<message_metadata>` of their `attempt_completion` result — the Orchestrator will then pause and notify the human. This is enforced by [`global_rules.md`](../skeleton/agent_framework/registry/shared/agents/rules/global_rules.md).

### The Handoff Protocol
Every operational agent must conclude its task by calling `attempt_completion` with `result` set to the full outgoing message in the standard XML format:

```
<message_metadata>
from: {your_slug}
to: {recipient_slug}
subject: {brief description}
</message_metadata>

<message_body>
{your message content here}
</message_body>
```

The Orchestrator reads this result, writes it verbatim to `agent_framework/inbox/draft/message.md`, runs `cycle/main.py` (which archives the current `unread/` contents, promotes the draft to `unread/`, and returns the next recipient slug), and invokes the next agent via `new_task` with the XML message as instructions.

### No Direct Mode Switching
Agents **cannot** invoke other agents directly or switch Roo modes. Handoff is achieved solely via `attempt_completion` with the standard XML message format. The Orchestrator mediates all routing.
