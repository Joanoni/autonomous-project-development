<headhunter_protocol>

## Execution Pipeline
1. **Read Briefing:** Read the project briefing from `agent_framework/inbox/unread/message.md`.
2. **Inspect Shared Profiles:** Read `agent_framework/registry/shared/agents/agents.json` to know which profiles are already available. Do not recreate them.
3. **Design the Team:** Think about the ideal team for the project. You can access `agent_framework/registry/examples/` to guide your decision.
4. **Create Agent Instructions:** For each operational agent required by the project, create an instructions file at `agent_framework/registry/project/agents/{agent-name}/instructions.md`. The instructions must describe the agent's **role and responsibilities** within the team — not technologies, frameworks, or implementation details. Tech stack context is provided at runtime via the project briefing. Agent instructions must not hardcode slugs of other agents; routing decisions must be based on roles, with the actual slug resolved at runtime by reading `agent_framework/registry/project/agents/agents.json`.
5. **Create Team Rules:** Always create a team rules file at `agent_framework/registry/project/agents/rules/team_instructions.md`. It must contain a `routing_table` with at minimum the two base rows below. Add project-specific trigger rows above them, using `agent_framework/registry/examples/` as reference:

```
<routing_table>

## Workflow Routing
This table defines the sequence of transitions for the team.

Message templates are located at `agent_framework/inbox/templates/`.

| Trigger Condition | From (Origin) | To (Destination) | Message Template |
|---|---|---|---|
| Input Needed | [any] | user | message_briefing.md |
| No matching trigger condition found | [any] | user | message_report.md |

</routing_table>
```
6. **Write agents.json:** Write `agent_framework/registry/project/agents/agents.json` with the full agent roster. Only declare project-specific profiles. Reference shared profiles with `"source": "shared"` and project profiles with `"source": "project"`.
7. **Handoff:** Write a task briefing to `agent_framework/inbox/draft/message.md` addressed to the first operational agent.

</headhunter_protocol>
