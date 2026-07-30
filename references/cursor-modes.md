# Modes: Ask / Plan / Agent / Debug

## The one idea
A **mode** is the agent's job description for a task. Picking the right one before you start is the cheapest way to get better results and waste fewer tokens. The winning habit is **understand → design → execute**, not "type request, hope."

Switch modes with **Shift+Tab** (rotates modes) or the mode-picker dropdown. Each mode uses its **own fresh context window**, so start a new chat when you change tasks.

## The four modes

### Ask — read-only research
- **What:** Searches and explains your codebase. Answers questions. **Makes no changes.**
- **Why:** Build a correct mental model before touching anything. It's the mode most people underuse.
- **Use for:** "How does auth work here?", "Where is X handled?", exploring an unfamiliar area, sanity-checking an approach.
- **Gotcha:** Don't try to squeeze implementation out of Ask — it produces vague suggestions with no edits. Switch to Agent when you want code.

### Plan — design before code
- **What:** Researches the codebase, **asks clarifying questions**, and produces a reviewable, editable implementation plan (steps + affected files). It edits code only **after you approve** the plan ("Build").
- **Why:** The hard part of most work is deciding *what* to change. A plan lets you catch a wrong approach in seconds instead of unwinding a bad multi-file change. It also makes the agent "farm context aggressively up front," which keeps it on track during execution.
- **How:**
  1. Shift+Tab to Plan (Cursor also suggests it when you type complexity keywords).
  2. Describe the goal with whatever context you have — paste the ticket, link files, mention constraints. A verbose/messy prompt is fine; Plan's job is to turn it into a clear plan.
  3. Answer its clarifying questions.
  4. Review the plan — **prune extra steps** (e.g. remove "build and verify" steps you'll do manually), reorder, add missing pieces. You can edit it conversationally.
  5. Build. Consider switching to a faster model to execute.
- **Use for:** complex features, many-file/many-system changes, unclear scope, architectural decisions.
- **Note:** Plans save to your home directory by default; "Save to workspace" to keep/share them with the repo.

### Agent — execution
- **What:** Full-capability mode. Reads files, makes multi-file edits, runs terminal commands, fixes errors, iterates until done.
- **Why:** This is where work gets done.
- **Use for:** implementing a plan, scoped changes, refactors, tests, bug fixes.
- **Guardrails (Agent can over-modify):** run Plan first for anything non-trivial, anchor it to existing patterns with `@file` references, and run tests immediately after each apply.

### Debug — runtime forensics
- **What:** Analyzes stack traces, logs, and state flow to find root causes; can instrument and use runtime evidence to propose targeted, minimal fixes.
- **Use for:** tricky bugs that are hard to reproduce or understand. Pairs with the `debugging-and-error-recovery` skill.

## Quick reference

| Mode | Best for | Edits files? |
|------|----------|--------------|
| **Ask** | Understanding code, exploring architecture | No (read-only) |
| **Plan** | Complex features where you review the approach first | Yes, after you approve |
| **Agent** | Building, refactoring, fixing | Yes |
| **Debug** | Tricky bugs needing runtime evidence | Yes |

## The flow that works
```
Ask   → understand the current architecture and constraints
Plan  → produce a precise, reviewable plan (high-reasoning model)
Agent → execute the plan (fast model), test after each step
Debug → drop in when something breaks and needs evidence
```
For a quick one-line fix or a simple question, skip straight to Ask or Agent — the ceremony only pays off as tasks get bigger (roughly: >2 files → do Ask/Plan first).

## Restart-from-plan trick
If Agent builds the wrong thing, don't fight it with follow-up prompts. **Revert, refine the plan, re-run.** Fixing the plan is usually faster and cleaner than steering a bad in-progress run.

## Good to know
- **Rules apply in every mode** (project, user, team rules are always in context).
- Because each mode has its own context, **new task = new chat** for best results.

## Authoritative / current
- Plan mode: https://cursor.com/docs/agent/plan-mode
- Agent: https://cursor.com/help/ai-features/agent
