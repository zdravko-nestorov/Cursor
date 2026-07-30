---
name: cursor-playbook
description: >-
  Guides how to approach a task in Cursor effectively: picking the right mode
  (Ask / Plan / Agent / Debug) and model tier (fast default vs high-reasoning vs
  design-leaning) before executing, and when to reach for cloud agents,
  automated review (Bugbot / security), MCP + indexing, or the profiling loop.
  Use at the start of a coding task, when the user is unsure which model or mode
  to use, when a task is large/ambiguous/architectural, or when the user asks how
  to work efficiently in Cursor. Treat models as a tool belt; do not default to
  the highest-reasoning model for everything.
---

# Cursor Playbook

The short version of "how to proceed" in Cursor. Two ideas drive everything:

1. **Mode before execution.** Understand and design in a read-only mode first, then execute. This is the single biggest lever for output quality and wasted-token reduction.
2. **Models are a tool belt.** Match the model to the task. The highest-reasoning model is not the best default — it is slower and more expensive, and overkill for most edits.

This skill is the hub. Each topic has a plain-language deep dive in the references library; read the relevant one when you need the "why" and "how."

---

## Start-of-task routine

Run this quickly at the start of any non-trivial task. Recommend a mode/model to the user and offer to switch (`SwitchMode` for Plan/Agent); the user chooses the model in the picker.

```
1. Classify the task:
   - Question / understand code?          → Ask mode
   - Big, ambiguous, multi-file, or       → Plan mode (high-reasoning model)
     architectural?
   - Clear and scoped?                     → Agent mode (fast default model)
   - Tricky bug needing runtime evidence?  → Debug mode
2. Pick the model tier for that mode (see table below).
3. Execute. For long/parallel/independent work, consider a cloud agent.
4. Before merge: run automated review (Bugbot / security) on the PR.
```

When in doubt about the model, **Auto** is a safe choice — it routes by prompt complexity.

---

## Decision table: task → mode → model tier

| Task | Mode | Model tier (examples — check the picker) |
|------|------|------------------------------------------|
| "How does X work?", explore architecture, read-only Q&A | **Ask** | Fast default (Composer 2.5) or Auto |
| Small edits, refactors, tests, tight write→run→fix loop | **Agent** | Fast default (Composer 2.5) |
| Complex feature, many files, unclear scope, design/architecture | **Plan** first | High-reasoning (GPT-5.x, Opus, Sonnet-thinking) → then switch to fast to execute |
| Subtle/hard bug, needs runtime evidence | **Debug** | High-reasoning |
| Frontend / UI / design-heavy work | Agent (or Plan) | Design-leaning (Gemini) — worth testing; see `frontend-ui-engineering` |
| Not sure | any | **Auto** (routes by complexity) |

Rationale for the "Plan with a big model, execute with a fast one" split: the hard part is usually deciding **what** to change. Spend reasoning budget on the plan, then hand a precise plan to a fast model for the mechanical **how**.

---

## Model tiers (the tool belt)

- **Fast default** — everyday agentic coding: file edits, terminal, multi-file changes, iteration. Fast and cheap. *Currently: Composer 2.5 (Fast variant is the in-IDE default; Standard is same intelligence, cheaper, for background/CI).*
- **High-reasoning / frontier** — complex planning, architecture, gnarly debugging, subtle correctness. Slower, pricier; use deliberately. *Currently: GPT-5.x, Opus, Sonnet "thinking" tiers.*
- **Design-leaning** — frontend/UX/visual work. *Currently: Gemini — test it for your workflow.*
- **Auto** — routes by prompt complexity when you don't want to choose.

Model names churn constantly. Pick by **tier**, not by memorizing versions; confirm what's live in the model picker. Full detail: `references/cursor-models.md`.

---

## When to reach for the bigger tools

- **Cloud agents** — long-running, parallel, or "kick it off and walk away" work; can open PRs and even demo results. Also how self-hosted / GitLab automation runs. See `references/cursor-cloud-agents.md`.
- **Automated review (Bugbot + security)** — catch bugs and vulnerabilities on PRs/MRs before merge; Bugbot can auto-fix via cloud agents. Can be a mandatory pre-merge check. See `references/cursor-code-review.md`.
- **Working at scale** (skills, MCP, plugins, repo indexing, semantic search, browser context) — how to give the agent the right context on large projects. See `references/cursor-working-at-scale.md`.
- **Profiling** — Cursor has no built-in profiler; use your stack's profiler, then attach the trace/flamegraph and let Agent run a measure → change → measure loop. See `references/cursor-profiling.md`.

---

## Deep dives (references library)

Read the one that matches the moment:

- `references/cursor-models.md` — models as a tool belt; which model when, and why.
- `references/cursor-modes.md` — Ask / Plan / Agent / Debug, and the Ask→Plan→Agent flow.
- `references/cursor-cloud-agents.md` — cloud agents, PRs, demos, GitLab + self-hosted.
- `references/cursor-code-review.md` — Bugbot and security review agents.
- `references/cursor-working-at-scale.md` — skills, MCP, plugins, indexing, semantic search, browser context.
- `references/cursor-profiling.md` — the performance measure→change→measure loop.
- `references/cursor-resources.md` — official links, workshops, and open questions for the Cursor team.

## Relationship to the engineering skills

This playbook is about **operating Cursor** (which mode/model/tool). The `.cursor/skills/*` engineering skills are about **doing the work** (spec, plan, implement, test, review). They compose: e.g. Plan mode + `planning-and-task-breakdown`, or the frontend tier + `frontend-ui-engineering`.
