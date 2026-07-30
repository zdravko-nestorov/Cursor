# Cursor Resources & Open Questions

Official links (cleaned from the Cursor team's session), plus learning paths and questions to send back.

## Core docs
- **Docs home:** https://cursor.com/docs
- **Composer 2.5 (default coding model):** https://cursor.com/docs/models/cursor-composer-2-5
- **All models:** https://cursor.com/docs/models
- **Plan mode:** https://cursor.com/docs/agent/plan-mode
- **Agent mode:** https://cursor.com/help/ai-features/agent
- **Cloud agents:** https://cursor.com/docs/cloud-agent
- **Self-hosted agent pool:** https://cursor.com/docs/cloud-agent/self-hosted-pool
- **Agent skills:** https://cursor.com/docs/skills
- **GitLab integration:** https://cursor.com/docs/integrations/gitlab
- **Bugbot (code review):** https://cursor.com/docs/bugbot

## Learning & background
- **Cursor Bench (model/coding benchmark):** https://cursor.com/cursorbench
- **Developer habits / insights:** https://cursor.com/insights
- **Cursor Harness (how the agent loop keeps improving):** https://cursor.com/blog/continually-improving-agent-harness
- **Workshops (101, 201, ...):** https://cursor.com/workshops

## Suggested learning path (for dummies → confident)
1. **Modes** — do Ask → Plan → Agent on one real task. (`references/cursor-modes.md`)
2. **Models** — try the same task with the fast default vs a high-reasoning model; feel the difference. (`references/cursor-models.md`)
3. **Working at scale** — add a small rules file + enable indexing on a real repo. (`references/cursor-working-at-scale.md`)
4. **Review** — turn on Bugbot for one repo; open a PR and read its comments. (`references/cursor-code-review.md`)
5. **Cloud agents** — delegate one self-contained ticket and let it open a PR. (`references/cursor-cloud-agents.md`)
6. **Profiling** — profile one slow path and run the measure→change→measure loop. (`references/cursor-profiling.md`)
7. Do a **Workshop** (101 then 201) to reinforce.

## Key takeaways (one screen)
- Treat models as a **tool belt**; don't default to max reasoning.
- **Ask/Plan before Agent** reduces wasted tokens and misfires.
- **Composer 2.5** = strong, fast, cheap default for coding.
- **High-reasoning** (GPT-5.x / Opus) = planning, architecture, hard debugging.
- **Gemini** = test for frontend/design.
- **Auto** routes by complexity.
- **Cloud agents** = long/parallel work, PRs, demos.
- **Bugbot + security** = automate PR review; Autofix via cloud agents.
- **Skills, MCP, plugins, indexing, semantic search, browser context** = context for large projects.
- **Profiling** = use your stack's profiler; Agent drives the fix loop.

## Open questions for the Cursor team
Add your own; these are starters worth asking:
1. **Model routing:** how does Auto decide, and can we see/log which model handled a request (for cost attribution)?
2. **Cost controls:** best way to enforce the cheaper Composer tier for background/CI agents org-wide? Per-seat budgets/alerts?
3. **Self-hosted GitLab:** can Cursor use a **single stable service account** across all projects instead of creating a new bot user per action/project?
4. **Bugbot on GitLab self-hosted:** recommended setup to avoid duplicate webhooks/bot users; making it a hard required check.
5. **Skills vs rules at org scale:** guidance for sharing/versioning team skills and rules across many repos.
6. **Enterprise data:** confirmation of data handling / privacy mode for cloud agents on private repos.
7. **Profiling:** any first-class plans for perf/trace ingestion, or is the "attach trace → Agent" loop the intended path?

> Note: links in the original email were Outlook safelink-wrapped and duplicated. The URLs above are the clean canonical ones.
