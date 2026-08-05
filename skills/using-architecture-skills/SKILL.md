---
name: using-architecture-skills
description: >-
  Routes architecture and design work to book-derived architecture skills
  (Ousterhout, Clean Architecture, DDD Distilled, DDIA, PoEAA). Use when
  starting architecture work, choosing module boundaries, domain modeling,
  data-system design, enterprise layering, or when unsure which architecture
  skill to apply. Complements Addy agent-skills (delivery) - does not replace them.
---

# Using Architecture Skills

## How this relates to Addy

| Layer | Skills | Job |
|---|---|---|
| **Delivery / process** | `using-agent-skills` and the skills it routes to | What to build, how to ship |
| **Architecture / design** | This pack | How to structure modules, domains, data, boundaries |

Use **both**: Addy for the workflow; architecture skills for design pressure inside that workflow.

Load **one primary** architecture skill per task (optionally one secondary). Do not stack all five.

## Routing

```
Architecture / design task
    │
    ├── Module depth, APIs, decomposition, cognitive load?
    │     → philosophy-of-software-design
    │
    ├── Protect business rules from frameworks/DB/UI; ports & adapters?
    │     → clean-architecture
    │
    ├── Subdomains, bounded contexts, ubiquitous language, context maps?
    │     → domain-driven-design-distilled
    │
    ├── Consistency, replication, partitioning, events, schema evolution?
    │     → designing-data-intensive-applications
    │
    ├── Enterprise pattern choice (Transaction Script vs Domain Model,
    │   Repository, Unit of Work, DTO, layering catalogs)?
    │     → patterns-of-enterprise-application-architecture
    │
    └── Unsure? Pick primary by the decision that most changes the design,
          then optionally add a complementary secondary (see matrix).
```

## Compatibility (do not co-load as equal primaries)

From the ciembor compatibility matrix:

| Pair | Status | Guidance |
|---|---|---|
| Clean Architecture + PoEAA | Overlap | Prefer **Clean Architecture** for dependency direction; use **PoEAA** only when choosing a specific enterprise pattern catalog |
| DDD Distilled + PoEAA | Overlap | Prefer **DDD Distilled** for modeling; PoEAA only for application-pattern catalog |
| Full DDD / IDDD + PoEAA | Conflict | Not installed; stay on Distilled |
| APoSD + Clean Architecture + DDD Distilled + DDIA | Complementary | Safe stack; still pick **one primary** per task |

## With Addy skills (typical combos)

| You are doing… | Addy skill | Architecture skill |
|---|---|---|
| Spec / PRD for a new capability | `spec-driven-development` | `domain-driven-design-distilled` and/or `clean-architecture` |
| API / module boundaries | `api-and-interface-design` | `philosophy-of-software-design` |
| Data platform / events / consistency | `api-and-interface-design` or `observability-and-instrumentation` | `designing-data-intensive-applications` |
| Review before merge (structure) | `code-review-and-quality` | `philosophy-of-software-design` or `clean-architecture` |
| Simplify / deepen modules | `code-simplification` | `philosophy-of-software-design` |
| ADRs / architecture docs | `documentation-and-adrs` | whichever book matches the decision |

## Invocation

- These skills are **model-invocable**: the agent should auto-select them from the task description.
- You can also name them explicitly: e.g. “use clean-architecture” or “apply DDD Distilled”.
- `reference.md` inside each skill is the **full** book pack - read only for deep audits, not every turn.

## Operating rules

1. State which architecture skill is primary before non-trivial design work.
2. If Addy and an architecture skill disagree on process vs structure: Addy wins on *workflow*; architecture skill wins on *structure*.
3. Prefer `mini` body already in each `SKILL.md`; escalate to that skill’s `reference.md` only when stuck.
