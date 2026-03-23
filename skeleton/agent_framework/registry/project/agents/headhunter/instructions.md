<headhunter_protocol>

## Execution Pipeline
1. **Read Briefing:** Read the project briefing from `agent_framework/inbox/unread/message.md`.
2. **Design the Team:** Think about the ideal team for the project. You can access examples in `agent_framework/registry/examples/` to guide your decision.
3. **Create Agent Instructions:** For each operational agent required by the project, create an instructions file at `agent_framework/registry/project/agents/{agent-name}/instructions.md`.
4. **Create Team Rules:** Create a team rules file at `agent_framework/registry/project/agents/rules/`.
5. **Write agents.json:** Write `agent_framework/registry/project/agents/agents.json` with the full agent roster using the APD agents.json format (profiles + agents). Create a dedicated profile for the team that includes the team rules file. 
6. **Handoff:** Write a task briefing to `agent_framework/inbox/draft/message.md` addressed to the first agent to start, then run `python agent_framework/scripts/user/post_work/main.py` and output `Done`.

</headhunter_protocol>
