<routing_table>

## Workflow Routing
This table defines the sequence of transitions for the team.

Message templates are located at `agent_framework/inbox/templates/`.

| Trigger Condition | From (Origin) | To (Destination) | Message Template |
|---|---|---|---|
| Feature Implemented | apd-coder | apd-tester | message_report.md |
| Bug Found | apd-tester | apd-coder | message_report.md |
| Tests Passed | apd-tester | user | message_report.md |
| Tech Stack Alteration Needed | [any] | user | message_briefing.md |
| Project Finished | [any] | user | message_report.md |
| Input Needed | [any] | user | message_briefing.md |
| No matching trigger condition found | [any] | user | message_report.md |

</routing_table>
