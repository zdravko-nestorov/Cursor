# Working at Scale: Context, Skills, MCP, Indexing

## The one idea
On a big codebase, the agent's output quality is mostly a function of **context** - giving it the right information at the right time. These features are the levers for that. (Deep companion: the `context-engineering` skill.)

## The levers

### 1. Repo indexing + semantic search
- **What:** Cursor indexes your codebase into embeddings so it can **search by meaning**, not just exact text ("where do we validate a payout?" finds the code even if it says `disbursement`).
- **Why:** the agent finds the *relevant* files on a large project without you naming them.
- **How:** keep indexing enabled; let it finish after cloning a big repo. Still anchor important tasks with explicit `@file` / `@folder` references.

### 2. Rules (persistent context)
- **What:** `.cursor/rules/*.mdc` (and `AGENTS.md`) inject standing context into **every** conversation - tech stack, commands, conventions, boundaries.
- **Why:** highest-leverage context. "If it isn't written down, it doesn't exist" for the agent.
- **Keep them small:** always-applied rules cost tokens on every request. Point to detail; don't inline everything.

### 3. Skills (on-demand know-how)
- **What:** `.cursor/skills/<name>/SKILL.md` - reusable workflows/knowledge the agent loads **when relevant** (like this playbook). Progressive disclosure: a lean SKILL.md links to heavier reference files read only when needed.
- **Why:** encode a process once, reuse everywhere, without paying for it on every prompt.
- **When:** repeatable workflows, team standards, domain knowledge the model wouldn't otherwise have.

### 4. MCP (Model Context Protocol)
- **What:** connectors that give the agent live, structured access to external systems - Jira/Confluence, GitHub/GitLab, Slack, databases, docs, browser tools, etc.
- **Why:** the agent can pull real data (an actual ticket, a live schema, a PR) instead of guessing.
- **How:** discover available tools first, then call them. Prefer an MCP tool over scraping or manual copy-paste when one exists for the system in question.

### 5. Plugins / editor extensions
- **What:** Cursor is VS Code-based, so the VS Code extension marketplace applies (linters, debuggers, profilers, language servers, framework tooling).
- **Why:** bring your existing stack's tooling; the agent then works *on top of* their output.

### 6. Browser context
- **What:** feed the agent live browser/runtime state - DOM, console errors, network, screenshots (e.g. via a Chrome DevTools MCP; see `browser-testing-with-devtools`).
- **Why:** verify UI against real runtime data instead of assuming; close the loop on frontend bugs.

## Choosing the right lever
```
Need standing project facts everywhere?      → Rules (small, always-on)
Need a repeatable workflow/know-how?         → Skill (on-demand)
Need live data from an external system?      → MCP
Need to find code by meaning on a big repo?  → Indexing + semantic search
Need stack tooling (profiler, linter, LSP)?  → VS Code extension/plugin
Need real UI/runtime state?                  → Browser context / DevTools MCP
```

## Context hygiene (don't flood it)
- More context ≠ better. Too much dilutes attention. Aim for focused, task-relevant context.
- Start fresh chats when switching tasks (modes have their own context anyway).
- Load the relevant spec section, not the whole spec.

## Authoritative / current
- Skills: https://cursor.com/docs/skills
- Docs home: https://cursor.com/docs
