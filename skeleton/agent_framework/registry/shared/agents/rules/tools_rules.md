<available_tools>

## Shared Tools

The following tools are available in `agent_framework/tools/shared/` and can be used by any agent.

---

### `cloudflare_deploy`

- **Path:** `agent_framework/tools/shared/cloudflare_deploy/main.ps1`
- **Description:** Deploys a local directory to Cloudflare Pages using Wrangler. Creates the project if it doesn't exist, uploads the specified directory, and outputs the stable deployment URL.
- **Runtime:** PowerShell
- **Parameters (set at top of script before running):**
  - `$ProjectName` — The Cloudflare Pages project name (string)
  - `$Directory` — Path to the local directory to deploy (string)
- **Output:** Prints the stable Cloudflare Pages URL on success (e.g. `https://<project>.pages.dev`), or an error with the raw Wrangler log on failure.
- **Prerequisites:** `npx` and `wrangler` must be available in the environment. Cloudflare authentication must be configured.
- **Usage:** To invoke this tool, run the script file directly (e.g. `pwsh agent_framework/tools/shared/cloudflare_deploy/main.ps1`). Do **not** copy the script contents into the terminal.

</available_tools>
