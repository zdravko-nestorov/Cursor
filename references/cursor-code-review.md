# Automated Review: Bugbot & Security Agents

## The one idea
Let an agent review your pull/merge request **before a human does**. It catches bugs, security issues, and regressions, comments inline, and can even push fixes - turning review from a bottleneck into a fast feedback loop.

## Bugbot - AI code review
- **What:** Cursor's code-review agent. Reviews PRs/MRs, comments on likely bugs and security issues, and can be configured as a **mandatory pre-merge check**.
- **Where:** GitHub, GitLab (incl. self-hosted), Bitbucket.
- **In-editor / CLI triggers:** `/review` and `/review-bugbot` (Cursor 3.7+ and at `cursor.com/agents`) keep local reviews in sync with Bugbot on your connected provider.
- **Bugbot Autofix:** spawns a **cloud agent** in its own VM to fix the issues it found, then pushes fixes (to the PR branch or a new branch) and comments the results. Uses cloud-agent credits at your plan rate. "Fix All" handles multiple findings at once.
- **Config:** uses your default model; can connect to MCP servers for extra context during review.

## Security review
- **What:** a review pass focused on vulnerabilities - untrusted input handling, authn/authz, injection, secret handling, unsafe data flows.
- **How you'll use it here:** the `security-and-hardening` skill and the **security-review** subagent (explicitly invoked) review local changes; Bugbot flags security issues on the PR itself.

## Why it matters
- Catches classes of bugs humans skim past (edge cases, error paths, injection).
- Shifts review left - issues found at PR time, not in production.
- Autofix gives reviewers a jumpstart instead of a to-do list.

## How to fit it into the workflow
```
Open PR/MR ─▶ Bugbot reviews automatically (or run /review-bugbot)
           ─▶ triage comments; let Autofix propose fixes
           ─▶ run a security pass on sensitive changes
           ─▶ human review ─▶ merge
```
Treat agent findings as **signal, not gospel** - verify before applying, especially security-sensitive fixes.

## When to lean on it
- Every non-trivial PR (make Bugbot a required check for shared repos).
- Anything touching auth, payments, user input, or data handling → add a security pass.

## Authoritative / current
- Bugbot: https://cursor.com/docs/bugbot
- Bugbot Autofix: https://cursor.com/blog/bugbot-autofix
