---
name: paysafe-api-mr-review
description: >-
  Reviews merge requests that change OpenAPI specs under apis/ in
  paysafe-wallet-saas-api. Covers API design, cross-spec consistency, reuse of existing
  definitions, example integrity, documentation and spec drift, contract completeness,
  and published error-code transparency. Complements the CI gates without duplicating
  them. Use when asked to review, audit or sanity-check API or spec changes, a merge
  request, or a branch in paysafe-wallet-saas-api.
disable-model-invocation: true
---

# Paysafe API MR review

Review OpenAPI spec changes under `apis/` for **design quality**, **cross-spec
consistency**, and **reuse of existing definitions**. This is the human-judgment layer on
top of the CI gates; it does not re-implement them.

Detail lives in separate files so this one stays cheap to load. Open them on demand.

| File | Open it when |
|------|--------------|
| [checklist.md](checklist.md) | Reviewing a spec. Full A-H rules, reuse recipes, error-code decision tree. |
| [reporting.md](reporting.md) | Writing the report. Writing rules, template, severity guide. |
| [reference.md](reference.md) | A finding needs a citation, or a convention is unclear. |
| [reuse-catalog.md](reuse-catalog.md) | Checking whether a component already exists. |

**Out of scope, CI owns these:** breaking-change detection (`oasdiff`), version bump and
`CHANGELOG.md` *format*, consumer sign-off. Mention them, never re-run them. Judging
whether the bump *magnitude* fits the change stays in scope.

## Step 0 - pick a depth and announce it

Say the depth in one line before you start, and repeat it in the report header. The user
overrides by typing `quick`, `standard` or `deep` after the MR number.

| Depth | Cost | What it does |
|-------|------|--------------|
| `quick` | ~20s | MCP diff only, no clone. Design, naming, status codes from the hunks. |
| `standard` | ~40s | **Default.** Worktree, reuse greps, example validator. No build. |
| `deep` | ~90s | Standard plus code generation, to inspect the generated Java. |

Auto-pick from the diff returned in Call 1:

- **deep** if it touches `oneOf`, `allOf`, `discriminator`, `x-one-of-interface`, an enum
  shared by variants, adds or deletes a file under `apis/`, or edits `build.gradle`.
- **quick** if it touches only `description:`, `summary:` or comments.
- **standard** otherwise.

Escalate mid-review if something surprises you, and say why in the report.

## Never rebuild what CI already proved

The MR pipeline ran on the same commit. Read job status with `get_pipeline_jobs`, which
costs 2 seconds against 35 for a local compile.

| Job | Hard gate | What green means |
|-----|-----------|------------------|
| `build` | yes | Code generation and `compileJava` pass. Do not re-run them. |
| `api-version-changelog-verification` | yes | A bump and a CHANGELOG entry exist. |
| `sonarqube-check` | yes | Static analysis passed. |
| `api-breaking-changes` | **no**, `allow_failure` | **Nothing.** Green here does not mean compatible. |

Run gradle only to **inspect generated output** (interface shape, `getType()` return type,
controller signature), or to test a fix **you** propose. Never to re-check the author's
compile.

## Environment

| Thing | Use this |
|-------|----------|
| Scratch root | `/tmp/paysafe-mr-review/` |
| MR worktree | `/tmp/paysafe-mr-review/mr-<N>` |
| Gradle clone | `/tmp/paysafe-mr-review/build` (reused between reviews) |
| Validator python | `/Users/zdravko.nestorov/.cursor/skills/paysafe-api-mr-review/.venv/bin/python` |

1. **Keep every scratch artifact under `/tmp/paysafe-mr-review`.** Never write to a
   sibling of the workspace such as `../mr-<N>`.
2. **`rm -rf src/generated` is the only delete a review needs.** Run it from inside the
   scratch build clone. Drop a worktree with `git worktree remove`, never with `rm`.
3. **Use the validator's own interpreter.** System `python3` is externally managed and has
   no `pyyaml` or `jsonschema`. If the virtual environment is gone, rebuild it once with
   `python3 -m venv <path>` then `<path>/bin/pip install pyyaml jsonschema`.
4. **Read files with the `Read` tool**, including generated Java under `/tmp`. It gives
   line numbers, and it never truncates the way `head` does.
5. **Never read credentials.** A review never needs a token, because the MCP server is
   already authenticated. `env`, `printenv`, `~/.ssh`, `~/.netrc` and `~/.cursor/mcp.json`
   are denied globally and will stop to ask the user.

## Workflow: five calls, not twenty

Latency comes from round trips, so batch aggressively. Project id is **1861**
(`paysafe/consumer/embedded-finance/paysafe-wallet-saas-api`); the `core-wallet` path is
stale. `<N>` is the MR number, `<T>` the target branch from `get_merge_request`.

**The GitLab MCP parameter is `id`, not `project_id`.** Every merge-request, pipeline and
job tool takes `{"id": "1861", "merge_request_iid": <N>}`, with `merge_request_iid` as an
**integer**. Passing `project_id` returns `404 Project Not Found`, which looks like a
missing project but is really a bad argument name. Only `search` and `get_workitem_notes`
use `project_id`.

**Call 1 - three things in parallel.** `get_merge_request`, `get_merge_request_diffs`
(`per_page: 100`), and this shell:

```bash
git fetch origin "refs/merge-requests/<N>/head:refs/mr/<N>"
```

Fetch into a **named local ref**, not bare `FETCH_HEAD`. Any later `git fetch` overwrites
`FETCH_HEAD`, and the worktree you build from it then points at the wrong commit.

Now pick the depth and announce it. Stop here if nothing under `apis/` changed.

**Call 2 - one shell that does all of the cheap work.** Skip entirely for `quick`.

```bash
mkdir -p /tmp/paysafe-mr-review && git worktree add --detach /tmp/paysafe-mr-review/mr-<N> refs/mr/<N> && cd /tmp/paysafe-mr-review/mr-<N> && git diff --stat origin/<T>...HEAD -- apis/ && git diff origin/<T>...HEAD -- apis/ && for f in $(git diff --name-only origin/<T>...HEAD -- apis/); do echo "== $f"; /Users/zdravko.nestorov/.cursor/skills/paysafe-api-mr-review/.venv/bin/python /Users/zdravko.nestorov/.cursor/skills/paysafe-api-mr-review/scripts/validate-examples.py "$f"; done
```

The validator checks every example against its schema, follows cross-file `$ref`s and
understands discriminators. **Only compare against the base when the head run reports
failures**; large legacy specs carry pre-existing ones, so a clean head needs no baseline.
When you do need it, add a second worktree at `/tmp/paysafe-mr-review/base` on
`origin/<T>`, run the validator there, and `diff` the two outputs.

**Call 3 - reuse greps and targeted reads, in parallel.** Put every `rg` from
[checklist.md](checklist.md) §Reuse-first into one shell call, and issue the `Read` calls
for the changed spec regions alongside it. A diff hunk is rarely self-contained: resolve
`$ref`s and read the whole operation before judging an example or a `fieldErrors[].field`.

**Call 4 - build. Only at `deep` depth.**

```bash
cd /tmp/paysafe-mr-review/build && git checkout -q <sha> && rm -rf src/generated && ./gradlew generateSaasChatbot --console=plain --offline
```

Create the clone once with
`git clone --shared --no-checkout <repo> /tmp/paysafe-mr-review/build`. It shares the
workspace object store, so Call 1's fetch already put the commit there. Do not fetch in
the clone; its `origin` is a local path.

`rm -rf src/generated` is **mandatory**. The generator never deletes files, so classes from
the previous SHA survive and collide, producing a fake error such as
`TextMessage.java: error: interface expected here` that reads exactly like a real defect.
Reused and warm, codegen takes about 2 seconds. Add `compileJava` (35s) only to test your
own fix.

**If `git checkout` refuses**, saying local changes to a spec would be overwritten while
`git status --short` prints nothing, the clone's index is just stale after
`--no-checkout`. Run `git status` once to refresh it, then checkout again. Do not reach
for `git stash`, `git reset` or `rm`.

**To compare generated code between base and head, reuse the one clone.** Check out the
other SHA, delete `src/generated`, generate again, and read the file. Never copy the clone;
it carries a full Gradle build directory and the copy buys you nothing. Two traps when you
inspect the output: methods are indented four spaces, so an `rg` pattern anchored with
`^  public` silently matches nothing and an interface looks empty, which is why you should
`Read` the file instead; and a `oneOf` parent generates an interface exposing **only** the
discriminator getter, whatever you put on the parent schema.

**Call 5 - the report**, in chat. The GitLab MCP cannot post MR notes, so the author
copies it. Clean up with `git worktree remove /tmp/paysafe-mr-review/mr-<N>` and leave the
gradle clone in place.

### Checking whether review comments are resolved

Run this when the user asks, for example "check if comments are properly resolved". It
answers two different questions, and you must report both: is the thread **resolved**, and
is the comment **fixed in the spec**. A thread can be fixed but still open, which still
blocks the merge.

1. `get_merge_request` already tells you the blocking state. Read
   `blocking_discussions_resolved`, `detailed_merge_status` (look for
   `discussions_not_resolved`) and `user_notes_count`.
2. Read the comment bodies with `search`, scope `notes`, `project_id: "1861"`,
   `per_page: 100`. Filter the result for `noteable_type == "MergeRequest"` and
   `noteable_iid == <N>`. Each note carries `resolvable`, `resolved`, `author` and `body`.
3. `search` needs a keyword, so run two or three in one parallel batch using nouns from
   the diff, such as the schema name, the field name and `Acknowledge` for the breaking
   changes bot. Merge the results by note id.
4. For every comment, check the head of the branch to see whether the requested change
   landed. Report each one as fixed or not fixed, separately from resolved or not.

**Known limit, always state it.** There is no "list merge request discussions" tool, so
step 2 finds only notes whose text matches a keyword. If the count you recover is lower
than `user_notes_count`, say so in the report and name the number you could not see.
A reply inside a thread has `resolvable: false`; only the thread head can be resolved.

**Never hunt for an API token to work around this.** Do not run `env`, do not read
`~/.cursor/mcp.json`, `~/.netrc` or a `glab` config, and do not try to install `glab`.
Those commands are denied on purpose and will stop the review to ask the user. The MCP
server is already authenticated; if a tool is missing, report the gap instead.

### Local branch instead of an MR

Same flow without the MCP calls or the worktree: `git fetch origin`, then
`git diff --stat origin/HEAD...HEAD -- apis/` and `git diff origin/HEAD...HEAD -- apis/`
in the workspace, then Call 3 onward.

### Quick depth caveat

Without a clone you cannot do reuse discovery or check conformance against unchanged
schemas. Say so in the report and offer to re-run at standard depth.

## Checklist triggers

One line each. Open [checklist.md](checklist.md) for the rule, the severity and the
citation whenever a line fires.

**A. Reuse and consistency (highest priority)** - common `Error` + named examples, not a
local copy; `PagingResultMeta`/`Limit`/`Offset`/`Link` from common; money as `int64` minor
units with `currencyCode`; timestamps `date-time` UTC; error codes reused and named
`DW-<DOMAIN>-<REASON>`; lists as `{items, meta}` with limit/offset; shared headers not
re-inlined.

**B. Naming** - properties `camelCase`, schemas `PascalCase` without `Dto`, enums
`UPPER_SNAKE_CASE`, `operationId` `kebab-case` and unique per file, tags `Title Case`.

**C. Design** - right verb and status codes (no `422` here); accurate `required`,
`readOnly`, `writeOnly`; constraints on new fields; removal or tightening is breaking;
polymorphism follows the canonical shape; security scheme matches the spec family;
internal surfaces in `*-internal-*` or `x-internal`.

**D. Versioning and wiring** - `info.version` stays `@Version@`; bump magnitude fits, and
in this repo a breaking change is a **patch**, never a major; `gradle.properties` equals
the top CHANGELOG block with a Jira link; a new spec file is wired in `build.gradle` and
the README.

**E. Documentation** - `summary` plus `description` on operations; descriptions give
business purpose, not a restatement; identifiers and enum literals in backticks; examples
named `UPPER_SNAKE`, no secrets.

**F. Examples** - conformance both ways, so no forbidden key, no missing `required`, and
no schema field absent from every example; every `example` and `default` satisfies its own
`enum`, `format`, `pattern` and bounds; response examples agree with a plausible request;
one or two examples per response, more only for genuinely distinct outcomes; error
examples name only real request fields; a shared response fits every operation that uses
it.

**G. Drift** - descriptions match what the spec implements; no dangling behaviour notes;
prose value lists match the `enum`.

**H. Completeness** - status codes named in prose exist in `responses`; no unreachable
schema or error code; server-owned fields kept out of requests; required-ness holds across
producers; closed sets use `enum`; client arrays bounded; terminal-state endpoints accept
only the terminal value.

## Never raise these (verified, they are correct)

Each of these has been checked against the generator or the repo history. Raising them
produces a false finding.

- **`oneOf` + `discriminator` + a shared enum on every variant.** This is the required
  shape. A per-variant inline enum breaks the build. Never propose single-value enums in
  place of the shared enum, and never propose dropping the discriminator.
- **A variant narrowing with `allOf: [$ref SharedEnum]` + sibling `enum: [ONE_VALUE]` +
  `default`.** Equivalent to the `not: {enum: [...]}` form and it compiles. Verified on
  MR 1214.
- **A `oneOf` parent without `x-one-of-interface`, `type: object` or `required: [type]`.**
  The generator still emits the correct interface. Verified on MR 1214.
- **A missing common platform header** (`User-Agent`, `Paysafe-Wallet-Version`,
  `Paysafe-Wallet-Platform`, `Partner-Application-Version`). They are global and mandatory
  by design, never declared per operation.
- **A breaking change shipped as a patch bump.** That is this repo's practice: 266
  releases, zero major bumps.
- **A green `api-breaking-changes` job as proof of compatibility.** It is `allow_failure`.

## Report

Skeleton and rules live in [reporting.md](reporting.md). Two things to remember here:
few findings each explained in three or four plain sentences, and the verdict rule, which
is any 🔴 means ⛔ Changes requested, only 🟡/♻️/🟢 means 🔧 Approve with nits, and none
means ✅ Approve. 📋 never changes the verdict.

## Notes

- Read-only: this skill reviews, it does not edit specs.
- Commands run without asking the user. `~/.cursor/permissions.json` holds only `autoRun`
  guidance, so everything a review does is allowed and just a short deny list stops for
  approval: privilege escalation, git commands that publish or rewrite history, deletes
  outside `/tmp`, and credential reads. If a review command ever stops, it hit that list,
  so change the command rather than asking for the deny list to be widened.
- If asked to check breaking changes explicitly, run
  `./gradlew apiBreakingChangesVerification` or use the OASDiff MCP. Do not hand-roll it.
- Published error-code source of truth:
  https://docs.paysafe.com/docs/embedded-wallets/error-handling
