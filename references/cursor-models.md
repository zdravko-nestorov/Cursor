# Models as a Tool Belt

## The one idea
Different models are different tools. A carpenter doesn't use a sledgehammer for everything. Reaching for the highest-reasoning model on every task wastes time and money and often produces *worse* interactive experiences (slower loops, over-thinking simple edits). Match the model to the job.

## Why it matters
- **Speed:** Fast models keep you in a tight write → run → fix loop. High-reasoning models pause longer to "think."
- **Cost:** High-reasoning frontier models can cost ~10x more per task than a fast coding model for the same edit.
- **Quality per task type:** A model tuned for agentic coding beats a general reasoner at file edits and tool use; a reasoning model beats a fast one at architecture and subtle bugs.

## The tiers

### 1. Fast default (everyday coding)
Your default for hands-on, agentic work: editing files, running terminal commands, multi-file changes, iterating on tests.

- **Currently:** **Composer 2.5** - Cursor's in-house agentic model. Frontier-level coding quality at a fraction of the cost/latency. Runs only inside Cursor.
  - **Fast variant** = the in-IDE default. Higher throughput so it *feels* responsive while you watch it. Same intelligence.
  - **Standard variant** = identical intelligence, ~6x cheaper, lower throughput. Ideal for background/cloud agents, CI, batch, or unattended long runs where no human is waiting.
- **Use for:** most day-to-day tasks - features, refactors, bug fixes, tests, "change this across these files."

### 2. High-reasoning / frontier (think hard)
Reserve for tasks where the *thinking* is the hard part.

- **Currently:** GPT-5.x, Claude Opus, Claude Sonnet "thinking" tiers (names change - check the picker).
- **Use for:** complex planning, architecture decisions, ambiguous multi-system changes, subtle correctness/security reasoning, hard debugging.
- **Cost/speed:** slower and more expensive. Use deliberately, not by default.

### 3. Design-leaning (frontend / UX)
- **Currently:** Gemini models - worth testing for frontend and design-heavy workflows.
- **Use for:** UI layout, visual polish, design iteration. Pair with the `frontend-ui-engineering` skill.

### 4. Auto (let Cursor choose)
- Routes to a model based on prompt complexity. A safe pick when you don't want to decide. Routing behavior continues to improve over time.

## How to choose (fast heuristic)
```
Is the hard part THINKING (design, architecture, subtle bug)?
  → High-reasoning tier.
Is the hard part DOING (edits, wiring, tests, iteration)?
  → Fast default (Composer 2.5).
Is it UI / visual / design?
  → Try the design-leaning tier (Gemini).
Don't want to decide?
  → Auto.
```

## The power move: split the work
For big tasks, **plan with a high-reasoning model, execute with a fast one.**
1. In **Plan mode**, use a frontier model to interpret a messy request, research the codebase, and produce a precise, reviewable plan.
2. Switch to a **fast default** model in **Agent mode** to implement the plan mechanically.

This spends expensive reasoning only where it pays off (deciding *what*) and cheap speed on the bulk work (*how*).

## Cost note (background work)
When an agent runs unattended (cloud agent, CI, Bugbot autofix, scheduled jobs), prefer the **Standard/cheaper** tier - throughput matters only when a human is watching tokens stream. The 6x Fast premium buys responsiveness you won't use at 3am.

## Anti-patterns
- Defaulting to the biggest model "to be safe" - slower, costlier, no better on routine edits.
- Using a fast coding model for a genuinely hard architecture decision - it may commit to a shallow approach.
- Memorizing exact version numbers - they change monthly. Think in tiers; confirm in the picker.

## Authoritative / current
- Composer 2.5: https://cursor.com/docs/models/cursor-composer-2-5
- All models: https://cursor.com/docs/models
