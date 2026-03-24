# APD Teams

## What is a Team?

A **team** is a runtime configuration that defines:
1. **Which agents** are active for a project (the roster).
2. **How work flows** between those agents (the routing table).
3. **What workspace files** (inbox templates, memory files) are available to agents.

Teams are not stored as static directories in the registry. Instead, the **Headhunter** designs and writes the team configuration at runtime by creating files under `agent_framework/registry/project/`:

```
agent_framework/registry/project/
├── agents/
│   ├── agents.json              ← team roster (written by Headhunter)
│   ├── rules/
│   │   └── team_instructions.md ← routing table (written by Headhunter)
│   ├── {agent-name}/
│   │   └── instructions.md      ← agent-specific instructions (written by Headhunter)
│   └── ...
└── workspace/                   ← workspace files synced into agent_framework/
```

> **Note:** `global_rules.md`, `operational_rules.md`, and `xml_rules.md` are **not** stored under `registry/project/`. They live in `registry/shared/agents/rules/` and are applied to agents automatically via the shared `apd-core` and `operational` profiles.

On the next Orchestrator loop, `cycle/main.py` picks up the new `agents.json` and automatically rebuilds `.roomodes` and `.roo/rules-{slug}/` for the new team.

---

## Built-in Examples

APD ships with two reference examples under `agent_framework/registry/examples/`. The Headhunter uses these as references when designing a team for a new project.

---

### `simple_code_project`

A minimal single-agent example. Use this as a reference for projects that only need a coder with no automated testing.

**Location:** `agent_framework/registry/examples/simple_code_project/`

**Agents:**

| Slug | Role |
|---|---|
| `apd-coder` | Senior Software Engineer — implements features and fixes bugs in `src/` |

**Profiles defined in `agents/agents.json`:**

| Profile | Source | Files | Applied to |
|---|---|---|---|
| `apd-core` | `shared` | `rules/global_rules.md`, `rules/xml_rules.md` | All agents |
| `operational` | `shared` | `rules/operational_rules.md` | All agents |
| `simple-team` | `project` | `rules/team_instructions.md` | All agents |

**Workspace files** (synced into `agent_framework/` when this example is used):
- `inbox/templates/message_briefing.md` — task briefing template
- `inbox/templates/message_report.md` — execution report template
- `memory/tech_stack.md` — canonical record of the project's technology choices
- `memory/decisions.md` — log of significant architectural decisions
- `memory/lessons_learned.md` — log of recurring errors and their solutions

---

### `simple_code_and_test_project`

A two-agent example with a coder and a tester. Use this as a reference for projects that require automated testing after each implementation cycle.

**Location:** `agent_framework/registry/examples/simple_code_and_test_project/`

**Agents:**

| Slug | Role |
|---|---|
| `apd-coder` | Senior Software Engineer — implements features and fixes bugs in `src/` |
| `apd-tester` | QA Engineer — creates and runs tests in `tests/` |

**Profiles defined in `agents/agents.json`:**

| Profile | Source | Files | Applied to |
|---|---|---|---|
| `apd-core` | `shared` | `rules/global_rules.md`, `rules/xml_rules.md` | All agents |
| `operational` | `shared` | `rules/operational_rules.md` | All agents |
| `simple-team` | `project` | `rules/team_instructions.md` | All agents |

**Routing table** (from `agents/rules/team_instructions.md`):

| Trigger Condition | From | To |
|---|---|---|
| Feature Implemented | `apd-coder` | `apd-tester` |
| Bug Found | `apd-tester` | `apd-coder` |
| Tests Passed | `apd-tester` | `user` |
| Tech Stack Alteration Needed | `[any]` | `user` |
| Project Finished | `[any]` | `user` |
| Input Needed | `[any]` | `user` |

**Workspace files** (synced into `agent_framework/` when this example is used):
- `inbox/templates/message_briefing.md` — task briefing template
- `inbox/templates/message_report.md` — execution report template
- `memory/tech_stack.md` — canonical record of the project's technology choices
- `memory/decisions.md` — log of significant architectural decisions
- `memory/lessons_learned.md` — log of recurring errors and their solutions

---

## How the Headhunter Designs a Team

When the Headhunter receives a project briefing, it:

1. Reads the project briefing from the `<message_body>` block in the `new_task` instructions.
2. Browses `agent_framework/registry/examples/` to find a reference team that fits the project scope.
3. Designs the agent roster and routing table for the project.
4. Creates agent instruction files at `agent_framework/registry/project/agents/{agent-name}/instructions.md`.
5. Creates a team rules file at `agent_framework/registry/project/agents/rules/` (e.g., `team_instructions.md`) containing the routing table.
6. Writes `agent_framework/registry/project/agents/agents.json` with the full roster.
7. Returns a task briefing via `attempt_completion` in the standard XML message format, addressed to the first operational agent.

On the next Orchestrator loop, `cycle/main.py` detects the updated `agents.json` and rebuilds the Roo environment for the new team automatically.

---

## Creating a Custom Team

To define a custom team, the Headhunter (or a developer manually) creates the following files under `agent_framework/registry/project/`:

### Required: `agents/agents.json`

Defines profiles and the agent roster. Each agent has a `roo` block (Roo mode configuration) and an `apd` block (rule file references).

> **Note:** The Headhunter writes this file at runtime. It should only include the **operational agents** it is provisioning — do not include `apd-headhunter` itself, as it is already defined in `registry/project/agents/agents.json` and will be present on every cycle regardless.

```json
{
  "profiles": [
    {
      "name": "my-team",
      "source": "project",
      "files": [
        "rules/team_instructions.md"
      ]
    }
  ],
  "agents": [
    {
      "roo": {
        "slug": "my-agent",
        "name": "My Agent",
        "roleDefinition": "<role_definition>You are a...</role_definition>",
        "groups": ["read", "edit", "command"],
        "customInstructions": ""
      },
      "apd": {
        "profiles": [
          { "name": "apd-core", "source": "shared" },
          { "name": "operational", "source": "shared" },
          { "name": "my-team", "source": "project" }
        ],
        "files": ["my-agent/instructions.md"]
      }
    }
  ]
}
```

> **Note:** Do **not** define `apd-core` or `operational` profiles locally — they are provided by `registry/shared/agents/agents.json` and referenced via `"source": "shared"`. Only define team-specific profiles (e.g., `my-team`) in the project `agents.json`.

**Rules:**
- Slugs must be unique across both `internal/agents/agents.json` and `project/agents/agents.json`. A conflict will cause `cycle/main.py` to output `APD_CONFLICT:{slug}` and halt.
- Profiles are scoped by source. Use `"source": "shared"` to reference shared profiles, `"source": "project"` for profiles defined in the project `agents.json`.
- File paths in `profiles[].files` are resolved relative to the `agents.json` that defines them. File paths in `apd.files` are resolved relative to the agent's own `agents.json` directory.

### Required: `agents/{agent-name}/instructions.md`

Agent-specific execution instructions. Wrap content in an XML tag matching the agent's role:

```markdown
<my_agent_protocol>

## Execution Pipeline
1. Read the task briefing from the `<message_body>` block in the `new_task` instructions.
2. Do the work in your domain.
3. Return a report via `attempt_completion` in the standard XML message format:
   ```
   <message_metadata>
   from: {your_slug}
   to: {recipient_slug}
   subject: {brief description}
   </message_metadata>

   <message_body>
   {your report content here}
   </message_body>
   ```

</my_agent_protocol>
```

### Required: `agents/rules/team_instructions.md`

The routing table for the team. Wrap in a `<routing_table>` XML tag:

```markdown
<routing_table>

## Workflow Routing

| Trigger Condition | From (Origin) | To (Destination) | Message Template |
|---|---|---|---|
| Task Complete | my-agent | user | message_report.md |
| Input Needed | [any] | user | message_briefing.md |
| No matching trigger condition found | [any] | user | message_report.md |

</routing_table>
```

**Rules:**
- Always include a row for routing to `user` — agents must know when to escalate to the human.
- Reference only message templates that exist in `agent_framework/inbox/templates/`.

### Team Directory Structure

```
agent_framework/registry/project/agents/
├── agents.json              ← required: roster + team-specific profiles
├── rules/
│   └── team_instructions.md ← required: routing table
└── {agent-name}/
    └── instructions.md      ← required per agent
```

> `global_rules.md`, `operational_rules.md`, and `xml_rules.md` are **not** placed here. They live in `registry/shared/agents/rules/` and are applied automatically via the shared profiles.

Once these files exist, the next Orchestrator loop will automatically provision the new team.
