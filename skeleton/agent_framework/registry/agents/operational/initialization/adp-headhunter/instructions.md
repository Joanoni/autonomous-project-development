<headhunter_protocol>

## Execution Pipeline
1. **Team Selection:** Scan `agent_framework/registry/teams/` and choose the team that best fits the project requirements.
2. **Phase 1 (Scouting):**
   - Open `agent_framework/scripts/provisioner/scout/input.json`.
   - Set the `chosen_team` key to your selected team's folder name.
   - Execute: `python agent_framework/scripts/provisioner/scout/main.py`.
3. **Phase 2 (Assembly & Slot Filling):**
   - Analyze the project briefing and fill all empty `{{placeholders}}` inside the `slots` object in `agent_framework/scripts/provisioner/assembler/input.json`.
   - Execute: `python agent_framework/scripts/provisioner/assembler/main.py`.

</headhunter_protocol>