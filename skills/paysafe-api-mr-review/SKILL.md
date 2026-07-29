---
name: paysafe-api-mr-review
description: >-
  Reviews merge requests that change OpenAPI specs in apis/ for this repository,
  focusing on API design best practices, consistency with the existing specs, reuse of
  already-defined models, fields, parameters, responses and examples, plus example
  integrity, schema/example conformance and coverage, documentation/spec drift, and
  contract completeness and lifecycle.
  Auto-detects the change set: fetches an MR diff via the GitLab MCP when given an
  MR URL/ID, otherwise diffs the local branch against its default branch. Complements the
  CI gates (oasdiff breaking-changes, version/CHANGELOG, review-confirmation) without
  duplicating them. Use when asked to review, audit, or sanity-check API/spec changes,
  a merge request, or a branch in paysafe-wallet-saas-api.
disable-model-invocation: true
---

# Paysafe API MR review

Review OpenAPI spec changes under `apis/` for **design quality**, **cross-spec
consistency**, and **reuse of existing definitions**. This is the human-judgment
layer on top of the automated CI gates — it does **not** re-implement them.

## Scope

**In scope (this skill):**
- API design best practices (verbs, status codes, resource modelling, constraints).
- Consistency with conventions already established across the ~26 specs in `apis/`.
- Reuse: use existing schemas / fields / parameters / responses / examples instead of
  redefining equivalents.
- Documentation quality: business-purpose descriptions (not field restatement), summaries,
  examples.
- Version-bump **magnitude** — whether the semver increase fits the change (checklist D).

**Out of scope — CI already gates these; mention, never re-run inside a review:**
- Breaking-change detection → `oasdiff` (`ci/api-breaking-changes/`, OASDiff MCP, or
  `./gradlew apiBreakingChangesVerification`).
- Version bump + `CHANGELOG.md` **existence/format** → the `paysafe-semver-version-bump`
  skill and `./gradlew apiVersionChangelogVerification`. Judging whether the bump
  **magnitude** fits the change stays in scope — see checklist D.
- Consumer-team sign-off → the MR's "API Review Confirmation" thread.

## Workflow

```
- [ ] 1. Resolve the change set (auto-detect: MR URL/ID → GitLab MCP, else local diff)
- [ ] 2. Load conventions → read reference.md
- [ ] 3. Review each changed spec against the checklist
- [ ] 4. Reuse-first: grep existing specs before flagging any "new" component
- [ ] 5. Emit the review report (in chat)
```

### Step 1 — Resolve the change set

Two invocation modes; both reduce to "review only what changed under `apis/`".

**A. Local branch — invoked inside the repo (primary path).** Diff the working branch
against the merge-base with the repo's default branch, restricted to `apis/`:

```bash
timeout 120 git fetch origin
# default branch of origin (falls back to master)
BASE_REF=$(git symbolic-ref -q --short refs/remotes/origin/HEAD || echo origin/master)
BASE=$(git merge-base "$BASE_REF" HEAD)
git diff --stat "$BASE"...HEAD -- apis/
git diff "$BASE"...HEAD -- apis/
```

**B. MR URL/ID given** (e.g. `.../-/merge_requests/123` or "MR 123") → GitLab MCP.
Project `id` is the URL-encoded path
`paysafe%2Fconsumer%2Fcore-wallet%2Fpaysafe-wallet-saas-api` (or the numeric project id);
`merge_request_iid` is the MR number.

- `get_merge_request` → `{ id, merge_request_iid }` (title, description, source/target).
- `get_merge_request_diffs` → `{ id, merge_request_iid, per_page: 100 }` (the diffs;
  page through if truncated).

The GitLab MCP exposes **only** MR metadata + diffs — it has **no file-read tool**
(`get_file_contents` is GitHub-only). Any check needing more than the hunk (ref
resolution, reuse greps, example↔schema) requires the files on disk: check out the MR's
source branch and review via mode A. Use MCP mode only to identify the change set.

If nothing under `apis/` changed, say so and stop.

### Step 2 — Load conventions

Read [reference.md](reference.md) — the grounded catalog of this repo's conventions
(shared components, error model, naming, data types, security, versioning). Cite it in
findings so authors can self-serve.

### Step 3 — Review against the checklist

Walk each changed operation/schema through the checklist below. For every changed spec,
also check the **ripple**: if a schema is referenced cross-file
(`./paysafe-wallet-*.yaml#/components/...`), confirm consumers still line up.

When a diff hunk isn't self-contained — verifying an example against its schema, or an
`error.fieldErrors[].field` against the request — **resolve the `$ref` and read the full
operation from disk** (Step 1: the GitLab MCP has no file-read tool, so deep checks need a
local checkout of the branch / MR source). The diff alone rarely shows the request schema
an example must match.

Beyond reuse/design, sweep for **example integrity, doc/spec drift, and completeness**
(checklist F–H) — the class of issue that structural CI (`validateSpec`) does not catch.
Run the recipes in [reference.md](reference.md) (§Drift & completeness scans) to surface
candidates mechanically, then confirm by reading.

### Step 4 — Reuse-first discovery (the priority)

Before flagging "define a new X", prove nothing reusable exists — consult
[reuse-catalog.md](reuse-catalog.md) (component registry, canonical field lexicon,
error-code registry) and run:

```bash
# existing component by concept (schemas are 4-space-indented PascalCase keys)
rg -n "^\s{4}[A-Z][A-Za-z0-9]*:" apis/ | rg -i "<concept>"
# every place a name/concept already appears
rg -n "<Name|concept>" apis/
# what common already provides (reuse before adding)
rg -n "paysafe-wallet-api-common.yaml#" apis/ | sort -u
# canonical field vs drift (e.g. currencyCode vs bare currency)
rg -n "currencyCode:|(^|\s)currency:" apis/
# existing error codes to reuse (DW-<DOMAIN>-<REASON>)
rg -oN --no-filename "code: '?[A-Za-z0-9][A-Za-z0-9_-]*'?" apis/ | sort -u
# likely-duplicate schema: eyeball its property set against candidates
rg -n -A20 "^\s{4}<NewSchema>:" apis/<file>.yaml
```

These recipes need a **local checkout** and run from the repo root — already true when the
skill is invoked inside your project on the branch. In pure MR mode (URL only, no clone),
grepping isn't available: check out the MR source branch (Step 1), or fall back to the
[reuse-catalog.md](reuse-catalog.md) registries plus the diff.

If an equivalent exists → **♻️ Reuse**; cite the exact `$ref` or error code.

### Step 5 — Emit the report

Output the report (template below) in chat. **The current GitLab MCP has no tool to
post MR discussion notes** (`create_workitem_note` targets issues/epics, not MRs), so
deliver findings in chat; the author applies or pastes them.

## Review checklist

### A. Reuse & consistency (highest priority)
- [ ] Error responses `$ref` the common `Error`
      (`./paysafe-wallet-api-common.yaml#/components/schemas/Error`) with named
      examples — **not** a locally redefined `Error`/`ErrorDetails`/`FieldError`.
- [ ] Reuse `PagingResultMeta`, `Limit`, `Offset`, `Link` from common; reuse domain
      schemas from `paysafe-wallet-api.yaml` / `paysafe-wallet-user-api.yaml` before
      adding new ones.
- [ ] Money = `integer`, minor units, `format: int64`; `currencyCode` (reuse `Currency`,
      ISO 4217); `countryCode` (ISO-3166 alpha-2). No money as `number`, no bare
      `currency`/`country`. New field names match the canonical lexicon (reuse-catalog.md).
- [ ] Timestamps `format: date-time` (UTC `Z`); calendar dates `format: date`; reuse the
      timestamp field name already used in that spec (don't add a new variant).
- [ ] New error `code` uses `DW-<DOMAIN>-<REASON>` (UPPER, hyphens) and reuses an existing
      code when the semantic exists — no numeric, `UPPER_SNAKE`, or `DW_` variants
      (registry in reuse-catalog.md).
- [ ] Lists use `{ <items>: [...], meta: PagingResultMeta }` with `limit`/`offset`
      params from common — no cursor/pageToken (not used here).
- [ ] Shared headers/params (`Signature`, `Authorization`, `Idempotency-Key`) reused,
      not re-inlined with a divergent shape.
- [ ] Common wallet SDK headers (`User-Agent`, `Paysafe-Wallet-Version`,
      `Paysafe-Wallet-Platform`, `Partner-Application-Version`) are **mandatory, always
      present, and defined centrally — not declared per operation**. Never flag their
      absence as a parameter, nor flag a field / `provider` derived from them as
      "undocumented input" (reference.md §Common platform headers).

### B. Naming
- [ ] Properties `camelCase`; schemas `PascalCase` (`Request`/`Response`/`List`
      suffixes; never `Dto`); enum values `UPPER_SNAKE_CASE`.
- [ ] Path params `camelCase` (`{customerId}`); multi-word path segments `kebab-case`.
- [ ] `operationId` `kebab-case`, unique within the file.
- [ ] Tags `Title Case` with a description.
- [ ] Exceptions are intentional only: OAuth/IETF fields (`grant_type`) stay
      `snake_case` in `auth.yaml`.

### C. Design best practices
- [ ] Correct HTTP verb + status codes; document the applicable set of
      400/401/403/404/409/429/500/503 (this repo does not use 422).
- [ ] `required` vs optional is accurate; `readOnly` for server-generated fields,
      `writeOnly` for secrets (request/response ownership detailed in H).
- [ ] New fields carry constraints where meaningful (`minLength`/`maxLength`,
      `pattern`, `example`).
- [ ] Removing/renaming a field or tightening a type is a breaking change — flag it and
      defer to the oasdiff gate; prefer `deprecated: true` over deletion.
- [ ] Security scheme matches the spec family (Bearer for user/v2, API_KEY/basic for
      B2B v1, OAuth2 scopes for internal); `security: []` only for intentionally public
      endpoints.
- [ ] Public vs internal placement correct: internal surfaces live in `*-internal-*`
      specs and/or carry `x-internal`.

### D. Versioning & wiring
- [ ] `info.version` stays `@Version@` unless the spec is intentionally pinned
      (`payments.yaml`, checkout specs use `'1.0'`).
- [ ] **Version bump magnitude fits the change** — additive feature → `Y+1,Z=0`;
      bugfix/doc → `Z+1`; breaking (per oasdiff) → `X+1,Y=0,Z=0`. Confirm `gradle.properties`
      equals the top `CHANGELOG.md` `### Version` block (+ Jira link, no duplicate). CI
      checks a bump *exists*; the *magnitude* is human judgment (reference.md §Version bump
      correctness).
- [ ] A **new spec file** is wired per README: `apis/`, a `build.gradle` generate task
      (+ `sourceJar`/`JavaCompile` deps), and a README entry.

### E. Documentation
- [ ] Operations have `summary` + `description`; new schemas/fields are described.
- [ ] Descriptions convey **business purpose**, flow role, covered scenarios, and
      behavioural contract (idempotency / side effects) — not a restatement of
      already-visible field names/types. Match reference.md §Description quality; flag a new
      public op shipping only a `summary` or a name-echoing description.
- [ ] Examples are named `UPPER_SNAKE`; no secrets/PII in examples.

### F. Examples — conformance, coverage & correctness (high-value; easy to miss)
_All findings in F cite reference.md §Examples: conformance & coverage._
- [ ] **Example ↔ schema conformance (both directions).** Every example is a valid
      instance of its schema — no keys forbidden by `additionalProperties: false`, all
      `required` present, correct types — **and** every field the schema defines is
      reflected in its examples. Adding/renaming/removing a schema field updates every
      example in lockstep: important new fields appear in ≥1 example, renamed keys are
      renamed, removed keys are purged from request *and* response examples. No example key
      lacks a matching schema property; no schema field is silently absent from all examples.
- [ ] **`example`, `default` and named-example values satisfy every constraint** — each
      value is a member of the field's `enum`, matches its `format` (`date-time` UTC `Z`,
      `uuid`, `int64` money in minor units), satisfies `pattern`, and respects
      `minLength`/`maxLength`, `minimum`/`maximum`, `minItems`/`maxItems`. A property-level
      `example`/`default` that violates its own `enum`/`pattern`/bounds is a contract bug.
- [ ] **Response examples are correct against the schema *and* consistent with the request.**
      On top of schema conformance (above), a response example that echoes or derives from
      request fields must line up with a plausible request: echoed values (`amount`,
      `currencyCode`, ids, `externalId`) match what the request sends, server-derived
      `readOnly` fields (status, timestamps, generated ids) stay coherent, and a paired
      request ↔ `2xx` example tells one story (no `USD` request answered by a `EUR`
      response).
- [ ] **Response examples cover the important scenarios — sparingly.** Every response with
      a body has ≥1 named example for the primary (happy-path) outcome; default to **1–2
      per response**. Add a **third+ only for a concrete business need** — genuinely
      distinct outcomes a consumer handles differently (each `oneOf`/polymorphic variant,
      or distinct error `code`s under one status). Flag over-provisioning: near-duplicate
      examples differing only trivially (a name, a timestamp) collapse to one.
- [ ] Example **data is coherent** — `sender.role`/author match the content, ids and
      timestamps are plausible, no copy-paste slips (a customer line tagged `role: AGENT`).
- [ ] **Error examples reference only real inputs.** In a `4xx` example, every
      `error.fieldErrors[].field` — and any field named in `error.details`/`message` — must
      be an actual request body property or parameter of *that* operation; a `400` example
      flagging fields the request never defines (or omitting the field that is actually
      validated) is a bug. The `code` must be one the operation can return for that input
      (reuse-catalog.md §Error-code registry).
- [ ] Examples on a **response reused across operations** are valid for *each* op — a
      terminal/"end" op reusing a generic `200` must not offer non-terminal states as
      outcomes; give it a dedicated response/examples when the shared set is wrong.
- [ ] Idempotent-replay notes/examples reflect the resource's **actual** state, not a
      hardcoded one (don't pin a single `endReason`/`status` for every replay).

### G. Documentation & spec drift
- [ ] `info.description` and field/op descriptions **match what the spec implements** — no
      aspirational or copied-in features (tokens, file uploads) with no backing path; no
      stale wording ("applied when creating" on a now server-derived field).
- [ ] Descriptions are **complete** — finish behaviour/idempotency notes with the
      consequence (e.g. "…else returns `409`, see `ConversationConflict`"); no dangling
      sentences.
- [ ] Drop "values are examples" on a closed `enum` — the enum *is* the contract.

### H. Completeness & lifecycle
- [ ] **Status-code parity** — every code named in a description exists in that op's
      `responses` and vice-versa; the `500`/`503` family used elsewhere is present on all
      non-trivial ops.
- [ ] **No unreachable declarations** — every error `code`/example and every schema is
      reachable from ≥1 operation (a defined `409` error must be wired to the op that can
      conflict, e.g. sending to an already-ended resource).
- [ ] **Request vs response ownership** — server-owned fields (identity, timestamps,
      status, derived context) are excluded from request schemas *and* examples, and
      marked `readOnly` on the resource.
- [ ] **Cross-operation required-ness** — a field `required` on a shared resource must be
      guaranteed by every producer; don't require on the response what's optional/absent
      on create.
- [ ] **Closed sets constrained** — a fixed value list (language, etc.) uses
      `enum`/`pattern`, not prose only; enum membership is complete and sensible (a
      `SYSTEM_ENDED` reason implies a `SYSTEM` actor; question odd pairs like
      `[NONE, STANDARD]`).
- [ ] **Collections bounded** — client-supplied arrays carry `minItems`/`maxItems`.
- [ ] **Terminal-state inputs are safe** — an endpoint that drives a resource to a
      terminal state accepts only that target (`status: [ENDED]`), not the full lifecycle
      enum.

## Output format

Report in chat in this shape — **summary first, findings by severity (highest first),
then what passed.** Keep it scannable.

```markdown
## API MR Review — <title / branch>

|          |                                         |
|----------|-----------------------------------------|
| Verdict  | ⛔ Changes requested                     |
| Specs    | `apis/<file>.yaml` (+A/−D), …           |
| Findings | 🔴 2 · 🟡 3 · ♻️ 1 · 🟢 4                 |

**Why:** <one decisive sentence — the reason for this verdict>.

### 🔴 Blockers — must fix before merge
1. **<short title>** · `apis/<file>.yaml:<line>`
   <problem, 1–2 lines>
   **Fix:** <concrete change> · _ref: <convention>_

### 🟡 Should fix
1. **<title>** · `apis/<file>.yaml:<line>` — <problem>. **Fix:** <change>. _ref: <…>_

### ♻️ Reuse
1. **<new component> duplicates <existing>** · `apis/<file>.yaml:<line>`
   **Use:** `$ref: './paysafe-wallet-api-common.yaml#/components/schemas/<X>'`

### 🟢 Nits
- <one-liners>

### ✅ Checked, no issues
<areas swept clean — e.g. naming · data types · pagination · security · version magnitude>

### CI gates — not evaluated here
Breaking changes · version/CHANGELOG format · review-confirmation.
```

**Verdict rule:** any 🔴 → ⛔ Changes requested; only 🟡/♻️/🟢 → 🔧 Approve with nits;
none → ✅ Approve. Lead with blockers; if nits run long, show the top ~5 and add "+N more".
Every finding needs `file:line`, a concrete fix, and a convention ref.

**Severity guide:**
- 🔴 **Blocker** — hard-convention violation, or a bug that misleads a consumer into a
  broken integration: redefined `Error`, `snake_case` property, money as decimal, an
  example that contradicts its schema, or one flagging / echoing a field the request
  doesn't define.
- 🟡 **Should fix** — deviates without strong reason; drift that won't break a client today.
- ♻️ **Reuse** — an existing definition should be used instead of the new one.
- 🟢 **Nit** — docs / example / style polish.

## Notes
- Read-only: this skill reviews, it does not edit specs.
- If asked to also check breaking changes, run
  `./gradlew apiBreakingChangesVerification` or use the OASDiff MCP — do not hand-roll it.

## Additional resources
- [reference.md](reference.md) — full convention catalog with file:line examples.
- [reuse-catalog.md](reuse-catalog.md) — reusable components, canonical field lexicon,
  error-code registry, and the duplication heuristic.
