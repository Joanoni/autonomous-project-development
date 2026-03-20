# APD Agents

## Overview

APD agents are specialized AI modes powered by the Roo VS Code extension. Each agent has a fixed role, a defined domain (the files it may touch), and communicates exclusively through the filesystem inbox. Agents are provisioned dynamically by the assembler based on the chosen team.

There are two agent categories:

| Category | Description |
|---|---|
| **Fixed** | Always present regardless of team. Manages the pipeline itself. |
| **Operational** | Provisioned per team. Performs actual project work. |

---

## Agent Reference

### `apd-orchestrator` — Orchestrator

| Property | Value |
|---|---|
| **Slug** | `apd-orchestrator` |
| **Category** | Fixed |
| **Roo Group** | `command` |
| **Domain** | No file writes — read-only pipeline manager |

**Role:** The infrastructure manager. Its sole purpose is to monitor the message queue and delegate execution to the correct agent or pause for human intervention.

**Inputs:** None — the Orchestrator does not have an inbox and does not read from one. No `inbox/apd-orchestrator/` folder is created during provisioning. It is triggered by the human typing `Start`.

**Outputs:** Invokes sub-agents via Roo's `new_task` tool with the command `Start`.

**Execution Loop:**
1. Run `python agent_framework/scripts/utils/scan_inbox/main.py`.
2. If output is `user` → pause and notify the human.
3. If output is `empty` → report "Queue Empty" and stop.
4. If output is an agent slug → invoke that agent via `new_task`.
5. When the sub-task returns `Done` → repeat from step 1.

**Constraints:**
- Does not read files, execute logic scripts, or write code.
- Relies entirely on `scan_inbox` output for routing decisions.

---

### `apd-headhunter` — Boot Architect

| Property | Value |
|---|---|
| **Slug** | `apd-headhunter` |
| **Category** | Operational / Initialization |
| **Domain** | `agent_framework/` (scripts, registry inputs) |

**Role:** The initialization specialist. Transforms a project briefing into a fully provisioned execution environment by selecting the appropriate team and running the provisioner pipeline.

**Inputs:** Reads from `agent_framework/inbox/unread/` — expects a project briefing in `message.md`.

**Outputs:** Writes a task briefing to `agent_framework/inbox/draft/message.md` and runs `post_work`.

**Execution Pipeline:**
1. **Team Selection:** Scan `agent_framework/registry/teams/` and choose the team that best fits the project requirements.
2. **Phase 1 — Scouting:** Set `chosen_team` in `agent_framework/scripts/provisioner/scout/input.json`, then run `python agent_framework/scripts/provisioner/scout/main.py`.
3. **Phase 2 — Assembly & Slot Filling:** Fill all `{{placeholders}}` in `agent_framework/scripts/provisioner/assembler/input.json`, then run `python agent_framework/scripts/provisioner/assembler/main.py`.
4. Run `post_work` and output `Done`.

---

### `apd-example-coder` — Senior Software Engineer

| Property | Value |
|---|---|
| **Slug** | `apd-example-coder` |
| **Category** | Operational / Development |
| **Domain** | `src/` (application source code) |

**Role:** Implements features and fixes bugs based on the task briefing and the project's tech stack. Writes production-ready code strictly within the `src/` directory.

**Inputs:** Reads from `agent_framework/inbox/unread/` — expects a task briefing in `message.md` with objective, success criteria, and constraints.

**Outputs:** Writes an execution report to `agent_framework/inbox/draft/message.md` (addressed `to: apd-example-tester`) upon completion, or escalates (`to: user`) if a blocker is encountered.

**Execution Pipeline:**
1. Read the task briefing from `unread/`.
2. Implement the required feature or bug fix in `src/`.
3. Write a report to the next agent's `unread/` folder.
4. Run `post_work` and output `Done`.

---

### `apd-example-tester` — QA Engineer

| Property | Value |
|---|---|
| **Slug** | `apd-example-tester` |
| **Category** | Operational / Development |
| **Domain** | `tests/` (test files) |

**Role:** Validates the implementation by creating and running tests. Determines whether the feature passes or fails and routes accordingly.

**Inputs:** Reads from `agent_framework/inbox/unread/` — expects an execution report in `message.md` from the coder.

**Outputs:** Writes a test report to `agent_framework/inbox/draft/message.md` addressed `to: user` (tests passed) or `to: apd-example-coder` (bug found).

**Execution Pipeline:**
1. Read the execution report from `unread/`.
2. Create or update test files in `tests/`.
3. Run the test suite and validate results.
4. Write a report to the appropriate recipient based on the outcome.
5. Run `post_work` and output `Done`.

---

## Rules Inheritance Chain

Every agent's effective ruleset is assembled by the provisioner from the following hierarchy. Rules are applied from most general to most specific:

The hierarchy below shows the built-in agents. The framework is fully customizable — you can add new operational agents under any domain group, and they will automatically inherit the rules from their parent folders.

```
agents/common/                              ← global_rules.md, xml_rules.md (ALL agents)
├── agents/fixed/common/                    ← fixed-agent shared rules
│   └── agents/fixed/adp-orchestrator/      ← orchestrator-specific instructions
└── agents/operational/common/              ← operational_rules.md (all operational agents)
    ├── agents/operational/{domain}/common/ ← domain-shared rules (e.g., dev_rules.md)
    │   ├── agents/operational/{domain}/agent-a/ ← agent-a-specific instructions
    │   └── agents/operational/{domain}/agent-b/ ← agent-b-specific instructions
    └── agents/operational/initialization/common/
        └── agents/operational/initialization/adp-headhunter/ ← headhunter-specific instructions
```

Additionally, the team's `workflow.md` is injected into every **operational** agent's rules directory, giving each agent full awareness of the routing table. The `apd-orchestrator` is a fixed agent and does **not** receive the `workflow.md` — it has no inbox and does not participate in the routing table.

---

## Key Behavioral Rules

### Full Autonomy
Agents **never ask the user for confirmation**. The only way an agent communicates with the user is by writing a message to `inbox/draft/message.md` with `to: user` — the Orchestrator will then pause and notify the human. This is enforced by [`global_rules.md`](../../skeleton/agent_framework/registry/agents/common/global_rules.md).

### The "Done" Protocol
The **absolute last message** of any operational agent in any task or sub-task must be strictly and only the word `Done` — no punctuation, no summary, no additional text. This signals the Orchestrator that the sub-task has completed and the loop should continue.

### Post-Work Mandatory
Before outputting `Done`, every operational agent **must**:
1. Write the outgoing message to `agent_framework/inbox/draft/message.md` with valid `from`, `to`, and `subject` front-matter fields.
2. Run `python agent_framework/scripts/utils/post_work/main.py`.
3. If the script prints an error, correct `draft/message.md` and re-run the command.

This validates the draft, archives the current `unread/` contents into `read/`, and promotes the draft to `unread/` for the next agent.

### No Direct Mode Switching
Agents **cannot** invoke other agents directly or switch Roo modes. Handoff is achieved solely by writing a message to `agent_framework/inbox/draft/` and running `post_work`. The Orchestrator detects the new `unread/message.md` on its next scan and performs the invocation.

