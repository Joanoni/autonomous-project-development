"""
cycle/main.py — APD Cycle Tool

Runs every time the Orchestrator starts its loop. Performs five steps in order:
  1. Merge agents.json from shared/, internal/ and project/ registries.
  2. Sync workspace files from all three registries into agent_framework/.
  3. Sync .roomodes and .roo/rules-{slug}/ from the merged agent definitions.
  4. Move messages: archive inbox/unread/ then promote inbox/draft/ → inbox/unread/.
  5. Scan inbox/unread/message.md and print the next recipient slug (or status).

Output (stdout, last line):
  APD_CONFLICT:{slug}  — duplicate slug detected between internal and project agents.json
  user                 — unread/message.md exists and to: user
  {agent-slug}         — unread/message.md exists and to: {slug}
  empty                — no unread/message.md or no to: field
"""

import os
from pathlib import Path

import sync_registry
import inbox_router


def main():
    base_dir = Path(os.getcwd())
    registry_dir = base_dir / "agent_framework/registry"
    agent_framework_dir = base_dir / "agent_framework"

    # Steps 1, 2, 3 — merge agents, sync workspace, sync roo environment
    merged = sync_registry.run(base_dir, registry_dir, agent_framework_dir)
    if merged is None:
        # Conflict already printed by sync_registry
        return

    # Steps 4, 5 — promote messages, scan inbox
    result = inbox_router.run(base_dir)
    print(result)


if __name__ == "__main__":
    main()
