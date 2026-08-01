# API convention catalog

Established conventions across `apis/*.yaml` (~26 OpenAPI specs), with `file:line`
evidence. Use these when reviewing changes so findings cite a concrete precedent.
When two patterns coexist, the **dominant** one wins for new work; the exception is
noted so you don't flag it as a regression.

## Shared components (`paysafe-wallet-api-common.yaml`)

A components-only spec (`paths: {}`, `servers: []`) holding cross-cutting primitives.
Reuse these first.

| Kind | Component | Cite |
|------|-----------|------|
| Schema | `Error`, `ErrorDetails`, `FieldError` | `apis/paysafe-wallet-api-common.yaml:45-83` |
| Schema | `PagingResultMeta` | `apis/paysafe-wallet-api-common.yaml:84-114` |
| Schema | `Link` | `apis/paysafe-wallet-api-common.yaml:16-44` |
| Parameter | `Limit`, `Offset` | `apis/paysafe-wallet-api-common.yaml:115-136` |
| Example | `REQUEST_BODY_NOT_PARSABLE`, `NOT_FOUND`, `INTERNAL_SERVER_ERROR`, `SERVICE_UNAVAILABLE` | `apis/paysafe-wallet-api-common.yaml:137-163` |
| Response | `'404'`, `'500'`, `'503'` | `apis/paysafe-wallet-api-common.yaml:164-191` |

**Reference style — relative path by filename:**

```
$ref: ./paysafe-wallet-api-common.yaml#/components/schemas/Error
$ref: ./paysafe-wallet-api-common.yaml#/components/parameters/Limit
$ref: ./paysafe-wallet-api-common.yaml#/components/responses/500
```

Both quoted and unquoted `$ref` appear (`apis/paysafe-wallet-api.yaml:111` unquoted vs
`apis/paysafe-wallet-api-v2.yaml:82` quoted) — cosmetic; don't block on it.

**Reference hierarchy** (reuse from the layer above before defining new):

```
paysafe-wallet-api-common.yaml   (primitives)
  → paysafe-wallet-api.yaml       (B2B/admin domain: Wallet, Customer, Transaction, Currency…)
  → paysafe-wallet-user-api.yaml  (user/profile domain: deposits, instruments…)
  → internal-api-v2 / merchant-api / user-loyalty / checkout … (compose the above)
```

`paysafe-wallet-api.yaml` re-exports common pagination so downstream specs can ref
either (`apis/paysafe-wallet-api.yaml:5252`, `:9288-9291`). Internal specs compose
user-api fragments via `allOf` (`apis/paysafe-wallet-internal-api-v2.yaml:3083-3094`).

## Error handling

Canonical shape is a wrapper with nested `error`
(`apis/paysafe-wallet-api-common.yaml:45-83`):

```yaml
Error:            # { error: ErrorDetails }
ErrorDetails:     # code:string, message:string, details:string[], fieldErrors:FieldError[]
FieldError:       # field:string, error:string
```

- Responses `$ref` the common `Error` schema + a **named** example, e.g. create-wallet
  400 (`apis/paysafe-wallet-api.yaml:106-129`). Best reuse refs the whole response:
  `$ref: ./paysafe-wallet-api-common.yaml#/components/responses/500`
  (`apis/paysafe-wallet-merchant-api.yaml:170-173`).
- Error `code` families in use: numeric legacy (`'5023'`, `'5269'`), `DW-` domain
  (`DW-CUSTOMER-BAD-REQUEST`, `DW-INTERNAL-SERVER-ERROR`), and a few `UPPER_SNAKE`
  (`MOBILE_NUMBER_ALREADY_EXISTS`).
- Status codes documented: **400, 401, 403, 404, 409, 429, 500, 503** (`412` only in
  instrument-verification; **422 is never used** — don't introduce it).

**Watch:** `auth.yaml`, `setup-api.yaml`, `webhooks.yaml`, `merchant-api.yaml`,
`payments.yaml` locally redefine `Error` instead of reusing common. `payments.yaml` uses
a **flat, lowercase `error`** schema (`apis/paysafe-wallet-payments.yaml:2764-2792`) —
legacy; new specs must reuse the common wrapper.

## Published error codes (MUST — SaaS transparency)

Clients integrate Embedded Wallet against **published** error codes. Source of truth:

https://docs.paysafe.com/docs/embedded-wallets/error-handling

[reuse-catalog.md](reuse-catalog.md) §Error-code registry is only a **high-frequency
shortcut** — never treat it as complete. When a change set adds or edits `error.code`
values (examples, named error examples, or response prose), **fetch the docs page** and
run this decision tree:

```
For each new/changed error.code in the MR:
  1. Exact match on the docs page (correct table)?
       → OK (published). Prefer reusing it over inventing a twin.
  2. No exact match, but a published code has the same semantic?
       → ♻️ Reuse that published code. Do not mint a near-duplicate.
  3. Genuinely new outcome clients must handle?
       → 🔴 until BOTH:
          a) naming is DW-<DOMAIN>-<REASON> (UPPER, hyphens; no new numeric /
             UPPER_SNAKE / DW_ underscore forms), AND
          b) Error Handling docs are updated (same change set or linked docs MR)
             with HTTP status + Error Code + Message/Description.
```

**Table discipline (do not conflate):**
| Docs section | Use for |
|--------------|---------|
| *HTTP Response Errors* / *Common Errors* / *Embedded Wallets Errors* (+ domain subsections) | `error.code` in OpenAPI error response examples |
| *Transaction Failure Status Reason* | `statusReason` / async failure fields — **not** HTTP `error.code` unless the op truly returns that field as `error.code` |

**Scope:** any code that ships in a **shipped OpenAPI example** (public or `*-internal-*` /
`x-internal`) — clients (and partners) still read the example.

**Gate only new/changed usage.** Do not force-rewrite every legacy code in untouched
examples. **Published ≠ style-perfect:** docs still list numeric legacy and some
`UPPER_SNAKE` / rare `DW_` forms — reusing those published codes in examples is OK; **new**
codes must be `DW-…` hyphens and must be added to the docs page.

**Flag it when:**
- 🔴 unpublished `error.code` in a changed example with no docs update.
- 🔴 new code that duplicates a published semantic (should reuse).
- 🔴 new code with wrong style (`DW_…`, bare `UPPER_SNAKE`, new numeric) even if a docs
  PR is promised.
- 🟡/`♻️` example uses a status-reason code as HTTP `error.code` (or the reverse) without
  the field actually being that.

## Naming

| Element | Convention | Cite |
|---------|-----------|------|
| Properties | `camelCase` | `apis/paysafe-wallet-api.yaml:4446-4478` |
| Schemas | `PascalCase`; `Request`/`Response`/`List` suffixes; no `Dto` | `apis/paysafe-wallet-api.yaml:4653-4663` |
| Enum values | `UPPER_SNAKE_CASE` | `apis/paysafe-wallet-api.yaml:4668-4694` |
| `operationId` | `kebab-case`, unique within file | `apis/paysafe-wallet-user-api.yaml:159-188` |
| Path params | `camelCase` `{customerId}` | `apis/paysafe-wallet-api.yaml` paths |
| Path segments | plural resources; `kebab-case` multiword | `/restriction-confirmations` |
| Tags | `Title Case` + description | `apis/paysafe-wallet-api.yaml:9335-9376` |

Paginated list wrapper:

```yaml
TransactionList:
  properties:
    transactions: { type: array, items: { $ref: '#/components/schemas/Transaction' } }
    meta: { $ref: '#/components/schemas/PagingResultMeta' }
```

**Exceptions (intentional):** OAuth/IETF fields use `snake_case`
(`grant_type`, `redirect_uri`) and lowercase enum values (`client_credentials`) in
`auth.yaml:1584-1603`. Checkout specs use `camelCase` operationIds
(`apis/paysafe-wallet-b2b-checkout.yaml:21`). `operationId` is not globally unique across
v1/v2 files (`create-wallet` in both `api.yaml:33` and `api-v2.yaml:32`) — unique **within
a file** is the bar.

## Data types & formats

- **Money:** `type: integer`, minor units, `format: int64`
  (`apis/paysafe-wallet-api.yaml:4574-4578`, balances `:4469-4477`). Property `amount`.
  _Watch:_ `merchant-api.yaml:1815-1822` uses `type: number` — non-standard, flag for new
  work.
- **Currency:** reuse `Currency` — ISO 4217, 3-char string
  (`apis/paysafe-wallet-api.yaml:5199-5205`); property `currencyCode`.
- **Country:** `CountryCode` ISO-3166 alpha-2, 2-char
  (`apis/paysafe-wallet-api.yaml:5916-5922`).
- **Timestamps:** `format: date-time`, UTC `Z` example; often `SaasTimestamp`
  (`apis/paysafe-wallet-api.yaml:5220-5225`). Calendar dates use `format: date`.
- **IDs:** internal IDs are `string` (often `maxLength: 20`); external IDs `string`
  `maxLength: 40` (`ExternalId` `apis/paysafe-wallet-api.yaml:6018-6024`). `format: uuid`
  only where strictly a UUID (loyalty idempotency, widget sessions) — not blanket.
- **Constraints:** `pattern`, `minLength`/`maxLength`, `example` widely applied;
  `readOnly`/`writeOnly` for server-gen/secret fields; `deprecated: true` to retire a
  field (e.g. `Transaction.fee` → `fees`); `nullable` is rare (loyalty / internal-user-
  management only).

## Reuse patterns

- **Pagination:** `limit`/`offset` only (`apis/paysafe-wallet-api-common.yaml:84-136`).
  No cursor/pageToken anywhere.
- **Shared parameters** defined in the owning spec and referenced cross-file: `Limit`,
  `Offset`, `Signature` (HMAC header, `apis/paysafe-wallet-api.yaml:9252-9258`),
  `Authorization`, `Content-Type`, `MerchantReferenceNumber`, `InstrumentType`.
- **Idempotency/concurrency** is ad hoc (no shared component): `Idempotency-Key` UUID
  header (`apis/paysafe-wallet-user-loyalty.yaml:906-911`), body ref ids
  (`onboardingReferenceId`), `If-Match`/ETag (instrument verification). Prefer reusing an
  existing pattern over inventing a new one.
- **Polymorphism:** two accepted patterns, both common (`oneOf` in 7 specs,
  `discriminator`+`mapping` in 10): (a) `oneOf`/`anyOf` variants, optionally with a
  `discriminator`; (b) a base schema with `discriminator` + `mapping` and subtypes via
  `allOf` (`apis/paysafe-wallet-api.yaml:4322-4326`). A `oneOf` whose variants have
  disjoint `required` fields is **valid and acceptable — do not flag it**. A
  `discriminator` is **optional**; propose adding one only as a 🟢 nit when it clearly
  improves codegen, never as a required change. The oasdiff gate injects an equivalent
  `oneOf` for discriminator-only schemas, so `oneOf` is the canonical shape for accurate
  diffing.
- **Request bodies:** usually inline schema `$ref`; `components/requestBodies` only in
  checkout specs.

## Common platform headers (mandatory — never flag as "missing")

The wallet SDK sends a fixed set of custom request headers on **every** call. They are
**mandatory and always present**, defined once centrally — **not** re-declared per
operation or per spec. Their absence from an operation's `parameters:` is **by design**.

| Header | Purpose | Example |
|--------|---------|---------|
| `User-Agent` | client + OS info, `<product>/<version> (<system>)` | `PaysafeWalletiOS/0.3.0 (iOS 16.4; Mobile)` |
| `Paysafe-Wallet-Version` | SDK version | `iOS-0.3.0` |
| `Paysafe-Wallet-Platform` | device platform + OS version | `iOS 16.4` |
| `Partner-Application-Version` | partner app version (update-policy enforcement) | `iOS-1.1.0` |

Source of truth: [CONFIG - Application Version Control → Headers](https://paysafe.atlassian.net/wiki/spaces/DWaaS/pages/136747266/CONFIG+-+Application+Version+Control#Headers).

**Reviewer rule — do NOT raise any of these:**
- "Mandatory header X is not declared as a parameter" — correct by design; they are global.
- "Response field `platform`/`appVersion` (or a derived `provider`) has no request input" —
  their source is these always-present headers (`Paysafe-Wallet-Platform` →
  `platform`/`provider`; `Partner-Application-Version` → app version). Treat as known context.

**Only** flag a header issue when a spec **re-declares** one of these as a local parameter
with a **divergent** name/shape, or invents a new custom header that duplicates one above.

## Security

| Spec family | Schemes | Default |
|-------------|---------|---------|
| B2B v1 (`api.yaml`) | `API_KEY` (http basic) | `API_KEY: []` |
| v2 (`api-v2.yaml`) | `Bearer`, `BearerProfileKycInfo` | `Bearer: []` |
| User (`user-api.yaml`) | `Bearer`, `BearerStandalone`, `SCA`, `BearerPCI` | all listed |
| Auth (`auth.yaml`) | `Basic`, `Bearer`, `BearerConfig`, `SCA`, `ATT` | all listed |
| Merchant | `BearerToken` | global |
| Internal (`internal-api.yaml`) | `InternalAuth` oauth2 clientCredentials + scopes | scoped (`apis/paysafe-wallet-internal-api.yaml:2219-2233`) |
| Webhooks | none (`{}`) | — |

Global `security` is the default; override an operation with `security: []` only when it
is genuinely public (`apis/paysafe-wallet-auth.yaml:343`). SCA is an `apiKey` header
`SCA-Authorization` (`apis/paysafe-wallet-user-api.yaml:18137-18141`).

## Versioning

- `info.version: '@Version@'` on ~22 specs (`apis/paysafe-wallet-api.yaml:6`); pinned
  `'1.0'` only in `api-common.yaml`, `payments.yaml`, both checkout specs.
- Version placement varies: in server URL (`/digitalwallets/v1`) for v1; in path
  (`/v2/...`) for `api-v2.yaml`; v2 server + unversioned paths for file-management /
  b2b-loyalty-v2. Match the spec's existing strategy.
- `-v2.yaml` / `-api-v2.yaml` file suffix denotes a newer surface.

## Version bump correctness (magnitude, not just presence)

CI (`apiVersionChangelogVerification`) only checks that a bump **and** a `CHANGELOG.md`
entry **exist**; it does not verify the bump **magnitude** is right for the change. That is
human judgment — cross-check against the `paysafe-semver-version-bump` skill ("minor/major"
means compatibility impact, not how big the change feels).

Read current `X.Y.Z` from `gradle.properties`; the MR's new value must follow:

| Change | Compatibility | Bump |
|--------|---------------|------|
| Feature — new op/schema/field, additive | backward-compatible | `Y+1`, `Z=0` |
| Bugfix / doc / example only | backward-compatible | `Z+1` |
| Breaking — remove/rename/tighten (feature or bugfix, per oasdiff) | breaking | `X+1`, `Y=0`, `Z=0` |

Reconcile with the oasdiff gate: a reported breaking change **must** be a major bump; a new
endpoint or optional field is a **minor**, never a patch. `CHANGELOG.md` must carry a top
block `### Version X.Y.Z` **equal to** `gradle.properties`, a one-line imperative summary,
and the Jira URL — with **no duplicate** block for that version.

**Flag it when:** magnitude ≠ change type (new endpoints shipped as `Z+1`; a breaking change
shipped as minor), `CHANGELOG` heading ≠ `gradle.properties` version, a duplicate version
block, or a missing Jira link.

## Public vs internal

- Internal surfaces live in `paysafe-wallet-internal-*` specs; titles marked
  `(Internal)`; `x-internal` marks hidden paths/ops/schemas within an otherwise public
  spec (`apis/paysafe-wallet-api.yaml:29-30` `x-internal: true` vs `:2353` `false`).
- Internal auth is OAuth2 client-credentials with scopes; public B2B v1 is basic API key.
- _Watch:_ `internal-user-management-api.yaml` and `merchant-api.yaml` carry "Internal"
  titles but use public `api.paysafe.com` servers — pre-existing, don't "fix" as a side
  effect.

## Documentation & vendor extensions

- Operations: imperative `summary` + markdown `description`; grouping `tags` required for
  Stoplight/portal.
- Examples: named `UPPER_SNAKE` at operation level (`Wallet_Created`, `INVALID_DATA`);
  reusable error examples in `common#/components/examples`.
- `x-*` in use: `x-stoplight` (Studio metadata), `x-internal` (hide from public docs),
  `x-examples`, `x-discriminator-value`, `x-enum-varnames`, `x-extra-annotation`
  (codegen, `auth.yaml`), `x-tags` (Stoplight tag on schemas). No `x-badges` — feature
  badges are HTML in markdown (`<FeatureInDevelopmentBadge />`).

## Description quality (business purpose over restatement)

Public-API descriptions must add what the schema cannot already show. A good description
states the **business purpose**, the operation's **role in the wider flow**, the
**scenarios it covers**, and any **behavioural contract** (idempotency, side effects,
ordering) — never a restatement of field names/types already visible in the spec.

**Exemplars to match:**
- Spec `info.description`: `## Introduction` + a business-purpose paragraph
  (`apis/paysafe-wallet-saas-chatbot.yaml:13-17`; `apis/paysafe-wallet-api.yaml:15-20`).
- Operation description naming purpose + flow role + scenario + behaviour:
  `create-live-chat-conversation` (`apis/paysafe-wallet-saas-chatbot.yaml:30-35`) — "handing
  the interaction over from the chatbot to a live support agent … the entry point for all
  subsequent live-chat operations … Include the `transcript` … **Idempotency:** …".
- Field description explaining format + consumer guidance, not just the type:
  `WalletVersionSupportVersion` (`apis/paysafe-wallet-internal-auth-api.yaml:305-315`).

**Markdown code spans (identifiers & literals):**
Descriptions are rendered as markdown in Stoplight/portal. Wrap tokens a consumer treats as
identifiers or contract literals in backticks so they render as code:

| Wrap | Examples |
|------|----------|
| Field / property names | `` `language` ``, `` `currencyCode` ``, `` `transcript` `` |
| Schema / model names | `` `Conversation` ``, `` `Error` `` |
| Ops / paths / status codes | `` `create-live-chat-conversation` ``, `` `409` `` |
| Enum / closed-set / error codes | `` `en` ``, `` `ENDED` ``, `` `DW-CUSTOMER-BAD-REQUEST` `` |

Do **not** backtick ordinary English words. Prefer a schema `enum`/`pattern` as the source
of truth for closed sets; if the description also lists values, every literal must match
that contract (and be backticked).

**Before / after:**
- ❌ `Supported values are: en, es, de, fr, it, pl, pt, ru, el, ro.`
- ✅ wrap each literal: Supported values are: `` `en` ``, `` `es` ``, `` `de` ``, …
  (better still: rely on `enum` and keep the description to purpose only)

**Flag it when:**
- 🟡 a **new public operation** ships with only a `summary` (or a `description` that just
  echoes the name — "Get the device.") and no purpose / flow / scenario context.
- 🟢 a new schema or non-obvious field restates its name instead of its meaning.
- 🟢 identifiers / enum literals / error codes appear bare in a description (should be
  `` `code` ``).
- 🟡/🔴 prose "supported values" disagree with the schema `enum`/`pattern` (drift — not a
  formatting nit).

Do **not** demand prose for self-evident fields (`amount`, `currencyCode`, `deviceId`) —
reserve the check for operations, schemas, and fields whose business meaning isn't obvious.

## Examples: conformance & coverage

Examples are contract, not decoration — `validateSpec` does not check them (see §Drift &
completeness scans). Two independent properties must hold: they must **agree with the
schema** (conformance) and there must be **enough of them, but no more** (coverage).

**Conformance — the example and the schema must match, both directions:**
- An example is a valid instance of its schema: no key forbidden by
  `additionalProperties: false`, every `required` field present, types correct.
- Every field the schema defines is reflected in its examples. When a schema field is
  added, renamed, or removed, ripple it through **every** example (request *and* response):
  important new fields appear in ≥1 example, renames are applied, removed keys are purged.
  A schema change with untouched examples is the most common drift here.
- Every example value — and every property-level `example`/`default` — satisfies the
  field's `enum` membership, `format` (`date-time` UTC `Z`, `uuid`, money `int64` minor
  units), `pattern`, and `minLength`/`maxLength`, `minimum`/`maximum`, `minItems`/`maxItems`.
  A schema `example`/`default` that violates its own constraints is itself a bug.
- Error-response examples reference only real inputs: `error.fieldErrors[].field` (and any
  field named in `error.details`/`message`) must be an actual request body property or
  parameter of *that* operation — a `400` example flagging fields the request never defines
  (or one whose `field` has no matching request constraint) is a bug. The `code` must be one
  the operation can return for that input (reuse-catalog.md §Error-code registry).
- Response examples that echo or derive from request fields must correlate with a plausible
  request: echoed values (`amount`, `currencyCode`, ids, `externalId`) match what the request
  would send, `readOnly`/server-derived fields stay coherent, and a paired request ↔ `2xx`
  example pair tells one consistent story.

**Coverage — enough examples to be useful, no more:**
- Every response returning a body carries at least one **named** (`UPPER_SNAKE`) example
  for the primary/happy-path outcome; reusable error examples come from
  `common#/components/examples` (`NOT_FOUND`, `INTERNAL_SERVER_ERROR`, …,
  `apis/paysafe-wallet-api-common.yaml:137-163`) rather than being re-invented.
- **Default to 1–2 examples per response.** One success example is the norm; add a second
  only when a distinct, common outcome genuinely helps the consumer.
- **Three or more only for a concrete business need** — outcomes a client must handle
  differently: each `oneOf`/polymorphic variant, or distinct error `code`s surfaced under
  the same status. "Might be nice" is not a need.
- **Flag over-provisioning.** Multiple examples differing only trivially (a name, an id, a
  timestamp) add noise, not signal — collapse to one. Prefer one precise example over
  three redundant ones.

## Inconsistency watchlist (know, don't auto-fix)

Pre-existing divergences — flag only if the MR under review *adds* to them:

1. Local `Error` duplication in auth/setup/webhooks/merchant/payments.
2. `payments.yaml` flat lowercase error shape + lowercase schema names.
3. `merchant-api` amount `type: number`.
4. `422` absent; screening spec documents only `200`.
5. `$ref` quoting mixed; OpenAPI `3.0.0` vs `3.0.3`.
6. operationId casing/duplication across v1/v2.
7. Internal-titled specs on public server URLs.

## Drift & completeness scans (checklist F–H)

Mechanical aids for the example-integrity, drift, and completeness checks. These are
heuristics — they surface **candidates**, not verdicts; confirm every hit by reading.

```bash
# status codes named in prose vs declared in `responses` (compare the two per op)
rg -n "\b(400|401|403|404|409|412|429|500|503)\b" apis/<file>.yaml
# aspirational / stale / non-authoritative description wording
rg -ni "values are examples|access token|file (attachment|upload)|applied when creating" apis/<file>.yaml
# dangling behaviour notes (a claim that never states its consequence)
rg -n "Idempoten|at most one|already (ended|exists)" apis/<file>.yaml
# every error code defined — then grep each to confirm a response actually surfaces it
rg -oN "code: '?[A-Za-z0-9][A-Za-z0-9_-]*'?" apis/<file>.yaml | sort -u
# closed sets described only in prose (should be enum/pattern)
rg -n "Supported values|one of|allowed values|must be one of" apis/<file>.yaml
# client-supplied arrays with no bounds (inspect for minItems/maxItems nearby)
rg -n -A3 "type: array" apis/<file>.yaml
# response examples: confirm each body has ≥1, and review any op carrying >2 (justified?)
rg -n "examples:" apis/<file>.yaml
# enum definitions — cross-check every example / `example` / `default` value is a member
rg -n -A8 "enum:" apis/<file>.yaml
# a schema field added/renamed — grep the name across examples to confirm parity
rg -n "<field>" apis/<file>.yaml
# fields cited in error examples — each `field:` must be a real request field of that op
rg -n -A4 "fieldErrors:" apis/<file>.yaml
# error codes in the changed file — then verify each new/changed one on Error Handling docs
rg -n "code: ['\"]?[A-Za-z0-9][A-Za-z0-9_-]*" apis/<file>.yaml
# fetch: https://docs.paysafe.com/docs/embedded-wallets/error-handling
```

**Example-vs-schema validation is not gated in CI** — `validateSpec` checks structure,
not example conformance or component reachability. For authoritative checks, run an
OpenAPI validator locally before human review, e.g. `spectral lint apis/<file>.yaml` or
`openapi-examples-validator`. A malformed example (extra key under
`additionalProperties: false`, missing `required`, wrong enum) is a real contract bug even
when the generator passes. Example **coverage** — how many, which scenarios — is human
judgment; see §Examples: conformance & coverage.
