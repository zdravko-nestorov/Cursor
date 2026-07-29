---
name: paysafe-semver-version-bump
description: >-
  Bumps the Paysafe Wallet SaaS API release version in gradle.properties using
  semver rules and prepends a Release Notes block to CHANGELOG.md with Jira
  link. Use when bumping version, semver, CHANGELOG, Release Notes,
  gradle.properties, Jira, or WHITE-* tickets for this repository.
---

# Paysafe semver version bump

## Semver mapping

Read current `X.Y.Z` from repository root `gradle.properties` (`version = X.Y.Z`).

**Minor / major** means **compatibility impact** (backward-compatible vs breaking), not how large the change feels.

| Kind    | Scope (compatibility)        | Bump rule                 |
| ------- | ---------------------------- | ------------------------- |
| Bugfix  | Minor (backward-compatible)  | `Z + 1`                   |
| Bugfix  | Major (breaking)             | `X + 1`, `Y = 0`, `Z = 0` |
| Feature | Minor (backward-compatible)  | `Y + 1`, `Z = 0`          |
| Feature | Major (breaking)             | `X + 1`, `Y = 0`, `Z = 0` |

## Workflow

1. **Collect inputs** (use AskQuestion when available, otherwise ask in chat):
   - Jira backlog item: ticket key (e.g. `WHITE-12345`) or full browse URL.
   - Feature vs bugfix.
   - Minor (backward-compatible) vs major (breaking) change.
2. **Normalize Jira line**: If only a key was given, use `https://paysafe.atlassian.net/browse/<KEY>`. If a full URL was given, use it as-is (trim whitespace).
3. **Description**: Ask for a short, imperative one-line summary for the changelog (match tone of existing entries in repository root `CHANGELOG.md`).
4. **Compute next version**: Parse current `version` from `gradle.properties`, apply the table above.
5. **Edit `gradle.properties`**: Update only the `version = ...` line; keep spacing `version = X.Y.Z`.
6. **Edit `CHANGELOG.md`**: Insert a new block **immediately after** `# Release Notes` and the following blank line, **before** the first existing `### Version ...`.

Use this template (replace placeholders):

```markdown
### Version X.Y.Z
- <description from user>
- <Jira URL>
```

7. **Verification**: Re-read `gradle.properties` and `CHANGELOG.md`. The new `### Version` heading must match `version` in `gradle.properties`, and there must be no duplicate version block for that number.
