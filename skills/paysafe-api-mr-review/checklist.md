# Full review checklist (A-H)

`SKILL.md` carries the one-line triggers. This file carries the reasoning behind each one.
Open it when a trigger fires and you need the exact rule, the severity, or the citation.

## A. Reuse & consistency (highest priority)
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
- [ ] **Error codes are reused, and new ones are named right.** Check every new or
      changed `error.code` against
      [Error Handling](https://docs.paysafe.com/docs/embedded-wallets/error-handling),
      using the correct table (`HTTP Response Errors` / `Embedded Wallets Errors`, **not**
      `Transaction Failure Status Reason`). Three outcomes:
      **(a)** already published → OK;
      **(b)** a published code means the same thing → ♻️ reuse it;
      **(c)** genuinely new → check the name only. Wrong style (new numeric, `UPPER_SNAKE`,
      `DW_`) is 🔴. Correct `DW-<DOMAIN>-<REASON>` style is fine in the spec, so the missing
      docs entry goes to **📋 After merge**, not to 🔴.
      Applies to public and internal specs. _(ref: reference.md §Published error codes)_
- [ ] Lists use `{ <items>: [...], meta: PagingResultMeta }` with `limit`/`offset`
      params from common — no cursor/pageToken (not used here).
- [ ] Shared headers/params (`Signature`, `Authorization`, `Idempotency-Key`) reused,
      not re-inlined with a divergent shape.
- [ ] Common wallet SDK headers (`User-Agent`, `Paysafe-Wallet-Version`,
      `Paysafe-Wallet-Platform`, `Partner-Application-Version`) are **mandatory, always
      present, and defined centrally — not declared per operation**. Never flag their
      absence as a parameter, nor flag a field / `provider` derived from them as
      "undocumented input" (reference.md §Common platform headers).

## B. Naming
- [ ] Properties `camelCase`; schemas `PascalCase` (`Request`/`Response`/`List`
      suffixes; never `Dto`); enum values `UPPER_SNAKE_CASE`.
- [ ] Path params `camelCase` (`{customerId}`); multi-word path segments `kebab-case`.
- [ ] `operationId` `kebab-case`, unique within the file.
- [ ] Tags `Title Case` with a description.
- [ ] Exceptions are intentional only: OAuth/IETF fields (`grant_type`) stay
      `snake_case` in `auth.yaml`.

## C. Design best practices
- [ ] Correct HTTP verb + status codes; document the applicable set of
      400/401/403/404/409/429/500/503 (this repo does not use 422).
- [ ] `required` vs optional is accurate; `readOnly` for server-generated fields,
      `writeOnly` for secrets (request/response ownership detailed in H).
- [ ] New fields carry constraints where meaningful (`minLength`/`maxLength`,
      `pattern`, `example`).
- [ ] Removing/renaming a field or tightening a type is a breaking change — flag it and
      defer to the oasdiff gate; prefer `deprecated: true` over deletion.
- [ ] **Polymorphism uses the canonical shape. `oneOf` + `discriminator` + a *shared*
      enum on every variant is CORRECT; never flag it.** The Java generator needs one
      `getType()` per interface, so a per-variant inline `enum` **breaks the build**. Never
      propose replacing the shared enum with single-value enums, and never propose dropping
      the `discriminator` to tighten validation. Each variant is pinned *inside itself*
      with `default: <VALUE>` + `not: { enum: [<other values>] }`; the parent carries
      `x-one-of-interface: true`, `type: object`, and `required: [<propertyName>]`. Only
      flag (🟡) a variant that has **neither** `default` **nor** `not`/`enum`, a parent
      missing those keys, or a `mapping` that disagrees with the `oneOf` list.
      _(ref: reference.md §Polymorphism. Reference implementation:
      `paysafe-wallet-user-loyalty.yaml:3456-3532`)_
- [ ] **Verified variations that must NOT be flagged** (all confirmed by running
      `generateSaasChatbot compileJava`, MR 1214):
      a variant may narrow with `allOf: [$ref SharedEnum]` + sibling `enum: [ONE_VALUE]`
      + `default` instead of `not`; a parent may omit `x-one-of-interface`, `type: object`
      and `required: [type]` and the generator still emits the correct interface. Both
      compile and both keep the shared enum on `getType()`.
- [ ] A `oneOf` parent generates a Java **interface exposing only the discriminator
      getter**. Common fields then need a cast. That is an inherent cost of a top-level
      discriminator, not a defect. Do flag a **response** that points at the polymorphic
      parent when the operation can only ever return one variant.
- [ ] Security scheme matches the spec family (Bearer for user/v2, API_KEY/basic for
      B2B v1, OAuth2 scopes for internal); `security: []` only for intentionally public
      endpoints.
- [ ] Public vs internal placement correct: internal surfaces live in `*-internal-*`
      specs and/or carry `x-internal`.

## D. Versioning & wiring
- [ ] `info.version` stays `@Version@` unless the spec is intentionally pinned
      (`payments.yaml`, checkout specs use `'1.0'`).
- [ ] **Version bump magnitude fits the change, judged against this repo's actual
      practice, not textbook semver.** Additive feature → `Y+1,Z=0`; bugfix, doc or
      breaking fix → `Z+1`. This repo has **never** bumped the major in 266 releases and
      ships breaking changes as patches. Do not demand `X+1`; see reference.md §Version
      bump correctness for the measured evidence. Confirm `gradle.properties` equals the
      top `CHANGELOG.md` `### Version` block (+ Jira link, no duplicate).
- [ ] A **new spec file** is wired per README: `apis/`, a `build.gradle` generate task
      (+ `sourceJar`/`JavaCompile` deps), and a README entry.

## E. Documentation
- [ ] Operations have `summary` + `description`; new schemas/fields are described.
- [ ] Descriptions convey **business purpose**, flow role, covered scenarios, and
      behavioural contract (idempotency / side effects) — not a restatement of
      already-visible field names/types. Match reference.md §Description quality; flag a new
      public op shipping only a `summary` or a name-echoing description.
- [ ] **Identifiers and literals in descriptions use markdown code spans.** Wrap schema /
      field / op / path names, status codes, error codes, and closed-set / enum values in
      backticks so portals render them as code — e.g. ``Supported values: `en`, `es`, `de`.``
      not bare `en, es, de`. Do **not** backtick ordinary prose. Prefer a schema `enum` as
      the contract; if prose also lists values, they must match the `enum` (see G / H).
      Missing backticks → 🟢; prose values ≠ schema → escalate under G/H.
      _(ref: reference.md §Description quality)_
- [ ] Examples are named `UPPER_SNAKE`; no secrets/PII in examples.

## F. Examples — conformance, coverage & correctness (high-value; easy to miss)
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
      a body has ≥1 named example for the primary (happy-path) outcome; default to **1-2
      per response**. Add a **third+ only for a concrete business need** — genuinely
      distinct outcomes a consumer handles differently (each `oneOf`/polymorphic variant,
      or distinct error `code`s under one status). Flag over-provisioning: near-duplicate
      examples differing only trivially (a name, a timestamp) collapse to one.
- [ ] Example **data is coherent** — `sender.role`/author match the content, ids and
      timestamps are plausible, no copy-paste slips (a customer line tagged `role: AGENT`).
- [ ] **Error examples name only real inputs.** In a `4xx` example, every
      `error.fieldErrors[].field` (and any field named in `error.details`/`message`) must
      be a real request property or parameter of *that* operation. Flagging a field the
      request never defines is a 🔴 bug. Each `error.code` must also be returnable for that
      input. Whether the code is **published** is handled in A: reuse → ♻️, bad name → 🔴,
      good name but missing from the docs page → 📋.
- [ ] Examples on a **response reused across operations** are valid for *each* op — a
      terminal/"end" op reusing a generic `200` must not offer non-terminal states as
      outcomes; give it a dedicated response/examples when the shared set is wrong.
- [ ] Idempotent-replay notes/examples reflect the resource's **actual** state, not a
      hardcoded one (don't pin a single `endReason`/`status` for every replay).

## G. Documentation & spec drift
- [ ] `info.description` and field/op descriptions **match what the spec implements** — no
      aspirational or copied-in features (tokens, file uploads) with no backing path; no
      stale wording ("applied when creating" on a now server-derived field).
- [ ] Descriptions are **complete** — finish behaviour/idempotency notes with the
      consequence (e.g. "…else returns `409`, see `ConversationConflict`"); no dangling
      sentences.
- [ ] Drop "values are examples" on a closed `enum` — the enum *is* the contract. A prose
      "supported values" list must match the schema `enum`/`pattern` exactly (and use
      backticks per E); do not invent a second, divergent list.

## H. Completeness & lifecycle
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

## Reuse-first discovery recipes (Step 4)

Run these from the repo root before flagging any "new" component. Consult
[reuse-catalog.md](reuse-catalog.md) first (component registry, canonical field lexicon,
error-code registry).

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

If an equivalent exists → **♻️ Reuse**; cite the exact `$ref` or error code.

## Published error codes (Step 4b — MUST when codes or error examples change)

Embedded Wallet is a SaaS product: clients integrate against **published** error codes, not
ad-hoc strings. Canonical list:

https://docs.paysafe.com/docs/embedded-wallets/error-handling

When the change set adds or edits any `error.code` (in examples, named error examples, or
response descriptions), **fetch that page** and apply the decision tree in
[reference.md](reference.md) §Published error codes. Do **not** treat
[reuse-catalog.md](reuse-catalog.md) alone as complete — it is a high-frequency shortcut;
the docs page is the source of truth.

Check **new/changed** codes only; do not churn legacy codes in untouched examples.

**A missing docs entry does not block the merge.** If the new code is named correctly, the
spec is fine. Put one grouped line in **📋 After merge** and move on. Keep 🔴 for what the
author can fix in the spec: a wrong-style name, or a code that duplicates a published one.
