# Cursor configuration

Portable parts of `~/.cursor`. Rules, skills, references, agent policy and hooks.

## What is deliberately not tracked

| Path | Why |
|---|---|
| `mcp.json` | Holds a live API token. Use `mcp.json.example` as the template. |
| `cli-config.json` | Holds account details (email, userId, authId). Only its permission rules are tracked, in `cli-permissions.json`. |
| `projects/`, `chats/`, `plugins/`, `skills-cursor/` | Cursor writes and owns these. |
| `skills/*/.venv/` | Local Python caches. Rebuild from the skill's `requirements.txt`. |

## Setting up on a new machine

1. Copy `mcp.json.example` to `mcp.json` and fill in the token.
2. Run `python3 scripts/restore-cli-permissions.py` to apply the CLI permission rules.
3. Edit the paths in `sandbox.json` (see below).

## Machine-specific values

`sandbox.json` lists absolute paths under `additionalReadwritePaths`. They are hardcoded
to one home directory, because Cursor does not expand `$HOME` or `~` in that file.
Rewrite them after cloning.

Two things that look like they should work but do not:

- Adding a path under `~/.cursor` to `additionalReadwritePaths` has no effect. Cursor
  blocks sandboxed writes there regardless.
- `permissions.json` is advisory. It guides the Auto-review classifier for shell, MCP and
  fetch calls. It does not gate the `Read` tool, and it does not apply to the CLI.
  The CLI rules live in `cli-permissions.json` and those are enforced.

## Hooks

`hooks.json` registers `hooks/check-dashes.py`. It runs after every file edit and warns
the agent when the text it just wrote contains an em-dash or en-dash, which
`rules/writing-style.mdc` bans. Hooks here are user-level, so they apply in every project.
