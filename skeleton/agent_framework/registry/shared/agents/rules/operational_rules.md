<operational_protocol>

## Core Execution Rules
1. **Context Boundary:** Every session is a fresh start. Your task is delivered via the `new_task` instructions in the standard message format (`<message_metadata>` + `<message_body>`). Read your task from there. Also read the `agent_framework/memory/` folder for persistent technical context.
2. **Lessons Check:** At the start of every task, read `agent_framework/memory/lessons_learned.md` alongside `agent_framework/memory/decisions.md`. Apply all recorded solutions proactively — do not repeat known errors.
3. **Operational Brevity:** Technical knowledge is transferred via files. Chat output must be extremely concise, avoiding conversational filler.
4. **Decision Logging:** Record any significant architectural or design choices in `agent_framework/memory/decisions.md`.
5. **Lessons Logging:** Whenever you encounter and resolve an error — whether technical (code, dependencies, commands) or behavioral (protocol, message format) — append an entry to `agent_framework/memory/lessons_learned.md` before concluding the task.
6. **The "Done" Protocol:** To conclude a task and hand off to the next agent, you MUST use the `attempt_completion` tool with `result` set to the full outgoing message in the standard format:
   ```
   <message_metadata>
   from: {your_slug}
   to: {recipient_slug}
   subject: {brief description}
   </message_metadata>

   <message_body>
   {your message content here}
   </message_body>
   ```
   Before setting `to`, consult the routing table in `agent_framework/registry/project/agents/rules/team_instructions.md` to determine the correct recipient based on the current trigger condition. The `recipient_slug` must match an agent slug from the team roster or be `user`. This is the only valid way to signal task completion and trigger the next step.
7. **Mode Switching Prohibition:** It is strictly forbidden to attempt to change your mode or invoke other agents directly. Handoff is achieved solely via `attempt_completion` with the standard message format above.

</operational_protocol>
