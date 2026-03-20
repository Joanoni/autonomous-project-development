# APD Teams

## What is a Team?

A **team** is a named configuration that defines:
1. **Which agents** are active for a project (the roster).
2. **How work flows** between those agents (the routing table).

Teams live in `agent_framework/registry/teams/`. Each team is a subdirectory containing at minimum an `agents.json` file. Teams with multi-agent workflows also include a `workflow.md`.

```
agent_framework/registry/teams/
├── init/
│   └── agents.json
└── example/
    ├── agents.json
    └── workflow.md
```

The **Headhunter** selects the appropriate team based on the project briefing, then runs the provisioner pipeline to build the runtime environment for that team.

---

## Built-in Teams

### `init` — Initial Team Setup

**Purpose:** Minimal bootstrap team used during the very first provisioning of a project. Contains only the infrastructure needed to select and provision a full team.

**Agents:**

| Slug | Role |
|---|---|
| `apd-orchestrator` | Pipeline manager |
| `apd-headhunter` | Boot architect — selects and provisions the real team |

**When to use:** This is the default team set in `scout/input.json` when `new_project.py` runs. It is not intended for ongoing development — the Headhunter's job is to replace it with a more capable team.

**No `workflow.md`:** The `init` team has no routing table because the Headhunter's only job is to provision the environment and hand off to the next team.

---

### `example` — Example Development Team

**Purpose:** A ready-to-use reference team that demonstrates a full development cycle with a coder and a tester. Intended as a starting point for projects that follow a standard implement → test → review loop.

**Agents:**

| Slug | Role |
|---|---|
| `apd-orchestrator` | Pipeline manager |
| `apd-example-coder` | Senior Software Engineer — implements features and fixes bugs in `src/` |
| `apd-example-tester` | QA Engineer — creates and runs tests in `tests/` |

**When to use:** Select this team (or use it as a template) for projects that need a basic implementation + testing workflow. The Headhunter can select it when the project briefing describes a standard software development task.

**Workflow:** Defined in `registry/teams/example/workflow.md`. The routing table is:

| Trigger Condition | From | To |
|---|---|---|
| Project Initialized | `apd-headhunter` | `apd-example-coder` |
| Feature Implemented | `apd-example-coder` | `apd-example-tester` |
| Bug Found | `apd-example-tester` | `apd-example-coder` |
| Tests Passed | `apd-example-tester` | `user` |
| Any escalation | `[any]` | `user` |

---

## How the Headhunter Selects a Team

When the Headhunter receives a project briefing, it:

1. Reads all available team directories under `agent_framework/registry/teams/`.
2. Evaluates the project requirements against each team's capabilities (agent roster and workflow).
3. Selects the team that best fits the scope and complexity of the project.
4. Sets `chosen_team` in `scout/input.json` and runs the provisioner pipeline.

The provisioner then **wipes and rebuilds** the entire runtime environment for the chosen team — replacing `.roomodes`, `.roo/rules-*/`, `inbox/`, and `memory/` with fresh, slot-filled artifacts.

---

## Creating a New Team

To add a custom team to APD, create a new subdirectory under `agent_framework/registry/teams/` with the following structure:

### Required: `agents.json`

Defines the team name and the list of agents, with each agent's slug and registry path.

```json
{
  "team_name": "My Custom Team",
  "agents": [
    {
      "slug": "apd-orchestrator",
      "path": "fixed/apd-orchestrator"
    },
    {
      "slug": "apd-example-coder",
      "path": "operational/development/apd-example-coder"
    },
    {
      "slug": "agent-a",
      "path": "operational/group-a/agent-a"
    }
  ]
}
```

**Rules:**
- The `apd-orchestrator` must always be included (it is the pipeline manager).
- The `path` value must match the agent's directory path relative to `agent_framework/registry/agents/`.
- Slugs must be unique within the team.

### Optional: `workflow.md`

Defines the routing table for the team. This file is injected into every operational agent's rules directory, so all agents are aware of the full workflow.

```markdown
<routing_table>

## Workflow Routing

| Trigger Condition | From (Origin) | To (Destination) | Message Template |
|---|---|---|---|
| Task Complete | agent-a | user | message_report.md |
| Input Needed | [any] | user | message_briefing.md |

</routing_table>
```

**Rules:**
- Use the `<routing_table>` XML tag as the root element (consistent with APD's XML formatting conventions).
- Always include a row for routing to `user` — agents must know when to escalate to the human.
- Reference only message templates that exist in `agent_framework/registry/internal_templates/`.

### Team Directory Structure

```
agent_framework/registry/teams/my-team/
├── agents.json      ← required
└── workflow.md      ← required for multi-agent teams
```

Once the directory exists, the Headhunter can select it by name during provisioning.
