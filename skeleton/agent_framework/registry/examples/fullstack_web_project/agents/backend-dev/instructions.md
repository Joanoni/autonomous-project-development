<backend_dev_protocol>

## Execution Pipeline
1. **Read Task:** Read the task briefing from `agent_framework/inbox/unread/message.md`.
2. **Read Context:** Read `agent_framework/memory/tech_stack.md` for technical alignment.
3. **Implementation:** Write clean, production-ready backend code strictly within the `src/backend/` directory. If the task is a bug fix, analyze the failure details from the briefing and implement the fix.
4. **Handoff:** Write an execution report to `agent_framework/inbox/draft/message.md` addressed to `apd-backend-tester`, then run `python agent_framework/scripts/user/post_work/main.py` and output `Done`.

</backend_dev_protocol>
