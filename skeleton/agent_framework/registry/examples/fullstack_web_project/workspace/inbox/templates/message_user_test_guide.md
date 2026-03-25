## Action Required
A new end-to-end flow is ready for manual testing. Please follow the test guide at `docs/user-testing/guide.md`.

## How to Respond
After completing the tests, write your findings to `agent_framework/inbox/draft/message.md` using this format:

```
<message_metadata>
from: user
to: apd-architect
subject: User Test Report
</message_metadata>

<user_test_report>

## Test Results
- **Overall Status:** {{passed | failed | partial}}
- **Flows Tested:** {{list of flows}}
- **Issues Found:** {{describe each issue or "None"}}
- **Steps to Reproduce:** {{for each issue}}

</user_test_report>
```

Then paste the message above in the **APD Orchestrator** chat to continue the cycle.
