<frontend_tester_protocol>

## Execution Pipeline
1. **Read Report:** Read the execution report from `agent_framework/inbox/unread/message.md`.
2. **Read Context:** Read `agent_framework/memory/tech_stack.md` for technical alignment.
3. **Test Creation:** Create or update automated test files exclusively within the `tests/frontend/` directory. Ensure coverage of the implemented components and user interactions.
4. **Execution & Validation:** Run the frontend test suite using the appropriate terminal commands and validate the results.
5. **Handoff:** Write a test report to `agent_framework/inbox/draft/message.md` addressed to `apd-architect`. Include whether tests passed or failed, and provide failure details if applicable. Then run `python agent_framework/scripts/user/post_work/main.py` and output `Done`.

</frontend_tester_protocol>
