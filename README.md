# APD — Autonomous Project Development

APD is a multi-agent AI orchestration framework that automates software development cycles. It uses [Roo](https://github.com/RooVetGit/Roo-Code) (VS Code extension) as the agent runtime and the **filesystem as an asynchronous communication bus**, enabling a team of specialized AI agents to build, test, and iterate on a project with minimal human intervention.

---

## Key Features

- **Fully autonomous pipeline** — agents hand off work to each other without human prompting; the human only intervenes when a decision or review is needed.
- **Filesystem-based messaging** — no external infrastructure required; agents communicate by writing `.md` files to the shared `inbox/` folder.
- **Profiles-based rules system** — agent behavior is composed from named profiles declared in `agents.json`, making it easy to extend or customize without touching agent code.
- **Dynamic team provisioning** — the Headhunter agent designs and writes the team roster (`agents.json`) at runtime; `cycle/main.py` picks up changes automatically on the next Orchestrator loop.
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
python scripts/new_project/main.py
```

Follow the prompts to set a destination folder and project name (or provide a Git SSH URL for a remote project).

### 3. Open the generated project in VS Code

```bash
code /path/to/your/project
```

Roo will detect `.roomodes` and load the APD agent modes automatically.

### 4. Write a briefing and start the cycle

1. Copy `agent_framework/templates/project_briefing/template.md` to `agent_framework/inbox/unread/message.md` and fill in your project description, tech stack, and success criteria.
2. Switch to **APD Orchestrator** mode in Roo and type `Start`.
3. The agents take it from there.

See [`docs/how-to-use.md`](docs/how-to-use.md) for the full step-by-step guide.

---

## Architecture Overview

```
APD Repository
├── scripts/
│   └── new_project/        ← entry point: creates new projects
└── skeleton/               ← template copied into every project
    ├── agent_framework/
    │   ├── registry/
    │   │   ├── internal/   ← orchestrator blueprint + cycle script
    │   │   ├── project/    ← headhunter blueprint + operational rules
    │   │   └── examples/   ← example teams for Headhunter reference
    │   ├── inbox/          ← filesystem message bus (draft/unread/read)
    │   ├── memory/         ← persistent technical state (decisions)
    │   └── templates/      ← user-facing document templates
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
| [`teams.md`](docs/teams.md) | Team system, built-in examples, how to create a custom team |
| [`how-to-use.md`](docs/how-to-use.md) | Step-by-step usage guide |
