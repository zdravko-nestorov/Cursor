# Report format and writing rules

Read this before writing the report. `SKILL.md` keeps only the template skeleton and the
verdict rule; everything that governs *how* a finding is written lives here.

Report in chat. Aim for **few findings, each one well explained**. Cut the number of
findings, never the explanation. A reader who has not opened the file must still
understand what is wrong and why it matters.

## Writing rules (follow these strictly)

- **Plain English.** One idea per sentence. Aim for 15 words or fewer. Use the everyday
  word: `use` not `utilize`, `start` not `commence`, `so` not `hence`. Many readers are
  not native English speakers.
- **Write full sentences, not notes.** Say `The schema does not allow this field.` Do not
  say `field not allowed -> invalid`. Short is not the same as telegraph style. Never use
  arrow chains, fragments, or invented shorthand.
- **Always explain why it matters.** Every finding states what goes wrong for the client
  if nobody fixes it. "It breaks the contract" is not enough. Say what the client sees.
- **Explain a technical term the first time you use it**, in about six words. Format:
  `discriminator (the field that says which variant this is)`.
- **Three to four short sentences per finding.** What is wrong. Why it matters. What to
  change. Add your evidence if you tested it.
- **Cap the number, not the depth.** Show the top 5 nits, then `+N more`. Merge similar
  findings into one. Drop findings the author cannot act on.
- **No em-dashes.** Use a hyphen, a comma, or a new sentence.

## Code snippets in the report

A short snippet is allowed, but only when words alone are slower to follow. Use one when:

- the fix is a **shape**, not a value (a nested `allOf` / `not` block, a new parent schema);
- you are pointing at an **existing pattern** the author should copy;
- the difference between wrong and right is **hard to describe in a sentence**.

Keep it to about 10 lines, show only the lines that change, and keep normal indentation:

````markdown
**Fix:** pin the value inside each variant.

```yaml
        type:
          allOf:
            - $ref: '#/components/schemas/MessageEntryType'
          default: MESSAGE
          not:
            enum: [PARTICIPANT_CHANGED]
```
````

Do **not** add a snippet when the fix is one word, a rename, a deleted line, or a value
change. Write those in prose. Never paste a whole schema or a whole example.

## Template

```markdown
## API MR Review - <title>

|          |                                   |
|----------|-----------------------------------|
| Verdict  | ⛔ Changes requested               |
| Depth    | standard (auto) - no build needed |
| Specs    | `apis/<file>.yaml` (+A/-D)        |
| Findings | 🔴 1 · 🟡 3 · ♻️ 1 · 🟢 2 · 📋 1    |

**Why:** <one short sentence naming the single biggest problem>.

### 🔴 Must fix before merge
1. **<short title>** · `apis/<file>.yaml:<line>`
   <What is wrong.> <Why it matters for the client.>
   **Fix:** <What to change.> <Your evidence, if you tested it.>

### 🟡 Should fix
1. **<short title>** · `apis/<file>.yaml:<line>`
   <What is wrong.> <Why it matters.>
   **Fix:** <What to change.>

### ♻️ Reuse
1. **<short title>** · `apis/<file>.yaml:<line>`
   <What the MR defines, and what already exists that does the same job.>
   **Use:** `$ref: '<path>'`

### 🟢 Nits
- `:<line>` <one sentence saying what to change and why it helps.>

### 📋 After merge - do not forget
- [ ] <task>. Owner: <who>.

### ✅ Clean
<comma-separated areas>. Not checked here (CI gates): breaking changes, version and
CHANGELOG format, review confirmation.
```

Skip any section that is empty. Never pad the report to fill the template.

## Good and bad findings

❌ **Too short.** The author cannot act on this, and nobody learns anything.

> `:487` - top-level `type` forbidden. **Fix:** delete 6 lines.

✅ **Right depth.** Same finding, but it says what, why, and how.

> **Examples send a field the schema does not allow** · `:487,508,518,528,547,557`
> The `Message` schema sets `additionalProperties: false` and no longer defines a
> top-level `type` field. Six examples still send `type: MESSAGE`. A client that copies
> these examples will send a request the server rejects.
> **Fix:** delete the six top-level `type:` lines. The `type` inside `payload` stays,
> because that one is still part of the schema. I tested this: all 72 examples become
> valid and the build still passes.

The good version is five lines instead of one. That is the right trade. If the report
feels long, remove weak findings, not the explanations.

**Verdict rule:** any 🔴 → ⛔ Changes requested; only 🟡/♻️/🟢 → 🔧 Approve with nits;
none → ✅ Approve. **📋 never changes the verdict.**

## Severity guide

| Mark | Meaning | Blocks merge? |
|------|---------|---------------|
| 🔴 | A bug in the spec that would break a client integration. Redefined `Error`, `snake_case` property, money as decimal, an example that contradicts its schema, an example naming a field the request does not have. | Yes |
| 🟡 | Deviates from convention. Will not break a client today. | No |
| ♻️ | Something reusable already exists. Includes a new error code that copies a published one. | No |
| 🟢 | Docs, example, or style polish. Missing backticks, weak wording. | No |
| 📋 | Work that must happen **outside this spec**, mainly publishing new error codes on the docs site. The spec itself is correct. | No |

## 📋 After merge - keep it small

This section keeps documentation work visible without flooding the review. Rules:

- **Group related tasks into one checkbox.** Five new error codes are one line, not five.
- **Say who owns it and why it is needed**, in one short sentence. Skip the background.
- **Only real follow-ups.** Anything the author can fix inside the spec belongs in
  🔴/🟡/♻️ instead.

Typical entry:

```markdown
### 📋 After merge - do not forget
- [ ] Publish 2 new error codes on the Error Handling docs page:
      `DW-LIVE-CHAT-CONVERSATION-ALREADY-EXISTS` (409) and
      `DW-LIVE-CHAT-CONVERSATION-NOT-ACTIVE` (409). Clients integrate against that page,
      so a code that is missing there is invisible to them. Owner: MR author.
```

## Reporting the depth you used

State the depth in the header table and, when it was reduced, say what that cost:

- **quick** - "Reuse discovery and conformance against unchanged schemas were not possible
  without a clone. Re-run at standard depth for a complete review."
- **standard** - no caveat needed; say `no build needed` if CI's `build` job was green.
- **deep** - name what the build proved, for example "codegen and compile verified, both
  variants keep the shared enum".
