<routing_table>

## Workflow Routing
This table defines the sequence of transitions for the Fullstack Web Project team.

Message templates are located at `agent_framework/inbox/templates/`.

| Trigger Condition | From (Origin) | To (Destination) | Message Template |
|---|---|---|---|
| Backend task assigned | apd-architect | apd-backend-dev | message_task.md |
| Frontend task assigned | apd-architect | apd-frontend-dev | message_task.md |
| E2E flow ready for user testing | apd-architect | apd-user-tester | message_task.md |
| Project complete | apd-architect | user | message_report.md |
| Input or decision needed | apd-architect | user | message_report.md |
| Backend implementation done | apd-backend-dev | apd-backend-tester | message_report.md |
| Frontend implementation done | apd-frontend-dev | apd-frontend-tester | message_report.md |
| Backend tests passed | apd-backend-tester | apd-architect | message_report.md |
| Backend bug found | apd-backend-tester | apd-architect | message_report.md |
| Frontend tests passed | apd-frontend-tester | apd-architect | message_report.md |
| Frontend bug found | apd-frontend-tester | apd-architect | message_report.md |
| User test guide ready | apd-user-tester | user | message_user_test_guide.md |

</routing_table>
