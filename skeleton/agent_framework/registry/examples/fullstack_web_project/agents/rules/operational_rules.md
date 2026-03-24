<operational_protocol>

## Core Execution Rules
1. **Context Boundary:** Every session is a fresh start. You must ONLY read files from `agent_framework/inbox/unread/` to receive your tasks, and the `agent_framework/memory/` folder for persistent technical context.
2. **Operational Brevity:** Technical knowledge is transferred via files. Chat output must be extremely concise, avoiding conversational filler.
3. **Decision Logging:** Record any significant architectural or design choices in `agent_framework/memory/decisions.md`.
4. **The "Done" Protocol:** To conclude a task, you MUST use the `attempt_completion` tool with `result` set to exactly `"Done"`. No punctuation, no summaries. This is the only valid way to signal task completion to the orchestrator.
5. **Handoff Requirement:** Every task must conclude with a message written to `agent_framework/inbox/draft/`. The message MUST be a folder-level file named `message.md` and include the required metadata fields (see rule 8). 
6. **Mode Switching Prohibition:** It is strictly forbidden to attempt to change your mode or invoke other agents directly. Handoff is achieved solely by writing to `agent_framework/inbox/draft/` and running `post_work`.
7. **Post-Work Automation:** Before concluding your task, write your outgoing message to `agent_framework/inbox/draft/message.md`, then run the exact command: `python agent_framework/scripts/user/post_work/main.py`. If the script prints an error, correct the draft and re-run the command. Only after the script completes successfully should you use `attempt_completion`.
8. **Message Metadata:** Every `message.md` MUST contain a `<message_metadata>` block as the first element:
   ```
   <message_metadata>
   from: {your_slug}
   to: {recipient_slug}
   subject: {brief description}
   </message_metadata>
   ```
   All three fields are required and must not be empty. The recipient slug must match an agent slug from the team roster or be `user`.

</operational_protocol>
