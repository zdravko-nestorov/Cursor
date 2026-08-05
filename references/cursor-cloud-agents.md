# Cloud Agents (Background Agents)

## The one idea
A cloud agent is a Cursor agent that runs on a **remote machine (its own VM)** instead of blocking your editor. You hand it a task; it works independently in the background, can run for a long time, open a pull request, and even **control its own computer to demo** what it built.

## Why it matters
- **Parallelism:** kick off several agents on independent tasks; keep coding locally while they run.
- **Long-horizon work:** tasks that would tie up your machine for a long time run remotely.
- **Handoff-ready output:** results come back as a **PR/MR** you can review, plus optional demos - not just a diff in your chat.
- **Automation:** cloud agents are the engine behind event-driven workflows (e.g. Bugbot Autofix spawns a cloud agent when a PR is opened).

## When to use
- Large refactors, migrations, or codemods across many files.
- "Go implement this ticket and open a PR" style delegation.
- Batch/repetitive changes.
- Anything you want to run unattended (use a **cheaper/Standard model tier** - no human is watching, so throughput doesn't matter).

## When NOT to use
- Tight interactive loops where you're iterating second-by-second - stay local in Agent mode.
- Tiny changes - the setup overhead isn't worth it.

## How it works (mental model)
```
You describe a task ─▶ Cursor provisions a VM ─▶ agent clones the repo,
  works, runs commands/tests ─▶ pushes a branch + opens a PR
  ─▶ (optionally) demos the result ─▶ you review & merge
```
Start cloud agents from the Cursor dashboard / agents surface (`cursor.com/agents`) or the integration you've connected.

## Git provider support (important for teams)
- **GitHub** (incl. GitHub Enterprise Server): full support for Cloud Agents + Bugbot.
- **GitLab** (incl. **self-hosted**): supported. **Background/cloud agents for GitLab are available**, in addition to Bugbot.
- **Bitbucket** (incl. Data Center): supported.

### GitLab self-hosted setup (high level)
Requires a **Teams or Enterprise** plan and a **paid GitLab plan** (Premium/Ultimate - project access tokens don't exist on GitLab Free). An admin registers a GitLab application:
- Redirect URI: `https://cursor.com/gitlab-connected`
- Trusted: `true`, Confidential: `true`
- Scopes: `api` and `write_repository`

Then, in the Cursor dashboard → Integrations → Advanced → GitLab Self-Hosted, enter the instance hostname + Application ID + Secret, register, link your account (select your self-hosted host, not the gitlab.com default), and Sync Repos. Enterprises can **lock a GitLab group/namespace** to the org via Protected Git Scopes (requires GitLab Owner).

> Networking: self-hosted GitLab needs secure **inbound** access from Cursor and **outbound** access for webhook notifications. On a Pro (non-team) plan, only gitlab.com is supported.

## Authoritative / current
- Cloud agents: https://cursor.com/docs/cloud-agent
- Self-hosted pool: https://cursor.com/docs/cloud-agent/self-hosted-pool
- GitLab integration: https://cursor.com/docs/integrations/gitlab
