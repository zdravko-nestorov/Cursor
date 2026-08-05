# Reuse catalog

Before adding a **schema, field, parameter, response, or error code**, find and reuse
what already exists. This is the #1 review priority. Pair the discovery recipes in
`SKILL.md` (Step 4) with the tables below. Frequencies are from `apis/` and indicate the
dominant (canonical) choice; "avoid" entries are real drift seen in the repo — don't
propagate them.

## Reusable components (reuse before defining)

### From `paysafe-wallet-api-common.yaml` (relative `$ref`)

| Component | `$ref` | Use for |
|-----------|--------|---------|
| `Error` | `./paysafe-wallet-api-common.yaml#/components/schemas/Error` | every error response body |
| `PagingResultMeta` | `.../schemas/PagingResultMeta` | `meta` block of a list response |
| `Link` | `.../schemas/Link` | navigation / redirect links |
| `Limit`, `Offset` | `.../parameters/Limit`, `.../parameters/Offset` | pagination query params |
| responses `404` / `500` / `503` | `.../responses/404` … | standard error responses |
| examples `NOT_FOUND`, `INTERNAL_SERVER_ERROR`, `SERVICE_UNAVAILABLE`, `REQUEST_BODY_NOT_PARSABLE` | `.../examples/<NAME>` | error example bodies |

### Domain schemas (reuse from the owning spec, cross-file `$ref`)

| Concept | Schema | Owner |
|---------|--------|-------|
| ISO 4217 currency | `Currency` | `paysafe-wallet-api.yaml` |
| ISO-3166 country | `CountryCode` | `paysafe-wallet-api.yaml` |
| date-time | `SaasTimestamp` | `paysafe-wallet-api.yaml` |
| external id | `ExternalId` | `paysafe-wallet-api.yaml` |
| Wallet / Account / Transaction / Address / CustomerPerson | (same) | `paysafe-wallet-api.yaml` |
| Profile / instrument / deposit models | (various) | `paysafe-wallet-user-api.yaml` |

`$ref` these cross-file instead of copying. Internal/v2 specs already compose user-api
fragments via `allOf` — follow that pattern.

## Canonical field lexicon

| Concept | Canonical field | Type / format | Reuse | Avoid (drift) |
|---------|-----------------|---------------|-------|---------------|
| money amount | `amount` | `integer`, `format: int64`, **minor units** | — | `type: number` (~12×), decimal strings |
| currency | `currencyCode` (582×) | string ISO 4217 | `$ref Currency` | bare `currency` (225×) except a nested `FxAmount.currency` object |
| country | `countryCode` (90×) | string ISO-3166 alpha-2 | `$ref CountryCode` | bare `country` (41×) |
| entity id | `<entity>Id` | string (often `maxLength` 20/40) | — | ad-hoc names, snake_case |
| — examples | `customerId`, `accountId`, `walletId`, `instrumentId`, `cardId`, `externalId`, `merchantId` | | | |
| uuid | keep `<entity>Id`; add `format: uuid` **only** when strictly a UUID (28× total) | string `uuid` | — | blanket `format: uuid` on all ids |
| timestamp | see note | string, `format: date-time` (UTC `Z`) | `SaasTimestamp` | inventing a 5th name |

**Timestamp note:** naming is genuinely inconsistent in the repo — `timestamp` (66×),
`createdDate` (36×), `createdAt` (36×), `updatedTime` (25×). There is **no** single
winner. The invariant is `format: date-time`. Match the name already used in the same
spec/domain; do not add a new variant.

## Error-code registry

**Canonical published source of truth (MUST verify against this for new/changed codes):**

https://docs.paysafe.com/docs/embedded-wallets/error-handling

This table is a **high-frequency shortcut only** — incomplete vs the live docs. Always
fetch the docs page when the MR touches error examples/codes (see reference.md
§Published error codes).

**Canonical style for NEW codes:** `DW-<DOMAIN>-<REASON>` — UPPER case, hyphen-separated.
Reuse a **published** code when one already means the same thing (♻️). A wrong-style name
is a 🔴 blocker. A correctly named new code still needs a docs row (HTTP status + code +
message), but that is a **📋 After merge** task and does not block the merge.

Reusable high-frequency codes (confirm still listed on the docs page):

| Purpose | Code(s) |
|---------|---------|
| 500 / 503 | `DW-INTERNAL-SERVER-ERROR`, `DW-SERVICE-UNAVAILABLE` |
| 404 | `DW-ENTITY-NOT-FOUND`, `DW-NO-SUCH-CUSTOMER` |
| 403 | `DW-OPERATION-NOT-ALLOWED`, `DW-CUSTOMER-NOT-ALLOWED` |
| 400 | `DW-CUSTOMER-BAD-REQUEST` |
| validation | `DW-<X>-SHOULD-BE-VALID`, `DW-<X>-SHOULD-BE-NUMERIC`, `DW-INCORRECT-OFFSET-AND-LIMIT` |
| 429 | `DW-TOO-MANY-REQUESTS` |
| domain | `DW-INSUFFICIENT-FUNDS`, `DW-<X>-LIMIT-EXCEEDED` |

**Legacy — do not mint new ones** (reuse only if already published / already in the op):
numeric Paysafe codes `5269`, `5068`, `5279`, `5270`, `5275`, `1200`, `1000`, `5285`.

**Avoid / flag as drift for NEW codes:**
- Underscore `DW_...` (e.g. `DW_CUSTOMER_CURRENCY_NOT_SUPPORTED`) duplicates the hyphen
  form `DW-CUSTOMER-CURRENCY-NOT-SUPPORTED`. Use hyphens.
- Bare `UPPER_SNAKE` (`TRANSFER_LIMIT_EXCEEDED`, `INSUFFICIENT_FUNDS`,
  `MOBILE_NUMBER_ALREADY_EXISTS`) — prefer the published `DW-` form when one exists.
- Example placeholders are not codes: `VOUCHER-ABC123`, `VPS`, `MYAGENT3`, raw hashes.
- Do not invent a twin of a code already on the Error Handling page.

**Do not conflate:** `Transaction Failure Status Reason` codes on the same docs page are
for `statusReason` / async failure — not HTTP `error.code` unless the operation truly
returns that value as `error.code`.

## Duplication heuristic (when is it a duplicate → ♻️ Reuse)

Treat a new schema/field/param/code as a probable duplicate if **any** hold:
- Same or synonymous **name** as an existing component (search the name and its stems).
- Same **property set** (±1 field) as an existing schema, even under a different name.
- Encodes a **lexicon concept** under a new name/type (e.g. a new `currency` string
  instead of `currencyCode` + `Currency`).
- New **error code** semantically equal to an **existing published** one (Error Handling
  docs) or to one already used in `apis/`.
- New **parameter** matching an existing `components/parameters` (`Limit`, `Offset`,
  `Signature`, …).

When probable, the finding names the exact existing `$ref` / **published** code to use
instead.
