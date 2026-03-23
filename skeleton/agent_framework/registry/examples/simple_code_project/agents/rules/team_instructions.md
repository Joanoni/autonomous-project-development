<routing_table>

## Workflow Routing
This table defines the sequence of transitions for the Example Team.

Message templates are located at `agent_framework/inbox/templates/`.

| Trigger Condition | From (Origin) | To (Destination) | Message Template |
|---|---|---|---|
| Feature Implemented | apd-example-coder | apd-example-tester | message_report.md |
| Bug Found | apd-example-tester | apd-example-coder | message_report.md |
| Tests Passed | apd-example-tester | user | message_report.md |
| Tech Stack Alteration Needed | [any] | user | message_briefing.md |
| Project Finished | [any] | user | message_report.md |
| Input Needed | [any] | user | message_briefing.md |

</routing_table>
