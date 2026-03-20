# APD — Autonomous Project Development

APD is a multi-agent AI orchestration framework that automates software development cycles. It uses [Roo](https://github.com/RooVetGit/Roo-Code) (VS Code extension) as the agent runtime and the **filesystem as an asynchronous communication bus**, enabling a team of specialized AI agents to build, test, and iterate on a project with minimal human intervention.

---

## Key Features

- **Fully autonomous pipeline** — agents hand off work to each other without human prompting; the human only intervenes when a decision or review is needed.
- **Filesystem-based messaging** — no external infrastructure required; agents communicate by writing `.md` files to each other's `inbox/` folders.
- **Hierarchical rules system** — agent behavior is composed from layered rule files (global → operational → domain → agent-specific), making it easy to extend or customize.
- **Team-based provisioning** — the environment (Roo modes, rules, inboxes) is dynamically built from a team definition, so the agent roster and workflow can be swapped without touching agent code.
- **Full audit trail** — every message ever sent between agents is preserved in `read/` folders.
- **Self-contained projects** — each generated project carries its own agent infrastructure; no dependency on the APD repository at runtime.

---

## Quick Start

### 1. Clone this repository

```bash
git clone https://github.com/Joanoni/autonomous-project-development.git
cd autonomous-project-development
```

### 2. Create a new project

```bash
python new_project.py
```

Follow the prompts to set a destination folder and project name (or provide a Git SSH URL for a remote project).

### 3. Open the generated project in VS Code

```bash
code /path/to/your/project
```

Roo will detect `.roomodes` and load the APD agent modes automatically.

### 4. Write a briefing and start the cycle

1. Create `agent_framework/inbox/unread/message.md` with the front-matter `from: user`, `to: apd-headhunter`, `subject: Project Briefing` followed by your project description.
2. Switch to **APD Orchestrator** mode in Roo and type `Start`.
3. The agents take it from there.

See [`docs/how-to-use.md`](docs/how-to-use.md) for the full step-by-step guide.

---

## Architecture Overview

```
APD Repository
├── new_project.py          ← entry point: creates new projects
└── skeleton/               ← template copied into every project
    ├── agent_framework/
    │   ├── registry/       ← agent blueprints, team definitions, internal templates
    │   ├── scripts/        ← provisioner (scout + assembler) + utilities
    │   ├── inbox/          ← filesystem message bus (global draft/unread/read)
    │   └── memory/         ← persistent technical state (tech_stack, decisions)
    └── src/                ← application code 
```

---

## Requirements

| Requirement | Version |
|---|---|
| Python | 3.10+ |
| VS Code | Any recent version |
| Roo Code extension | Latest (VS Code Marketplace) |
| Git | Required for remote projects only |
| LLM API key | Configured in Roo settings |

---

## Documentation

Full documentation is in [`docs/`](docs/):

| Document | Description |
|---|---|
| [`architecture.md`](docs/architecture.md) | System design, runtime environment, rules hierarchy |
| [`agents.md`](docs/agents.md) | All agents: roles, domains, inputs, outputs, behavioral rules |
| [`scripts.md`](docs/scripts.md) | All scripts: purpose, inputs, outputs, side effects |
| [`teams.md`](docs/teams.md) | Team system, built-in teams, how to create a custom team |
| [`how-to-use.md`](docs/how-to-use.md) | Step-by-step usage guide |
