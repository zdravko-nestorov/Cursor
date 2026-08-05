---
name: paysafe-internal-email
description: >-
  Turns a draft, notes, or an email thread into a clear, lightly formatted
  internal email that pastes straight into Outlook. Detects the type (ASK,
  UPDATE, ANNOUNCE, ESCALATE), asks for the few facts it cannot guess, resolves
  Jira and Confluence keys into links embedded in readable words, and adds a
  numbered ACTION REQUIRED block when a reply is needed. Ends with a pass that
  strips machine-written wording, so the email reads like a colleague wrote it.
  Covers new emails and replies to an existing thread. Manual invocation only.
disable-model-invocation: true
---

# Paysafe internal email

Persona: a solutions architect at a payments company, writing to any internal
department - engineering, security, risk, compliance, product, operations.
Usually asking questions to understand how a system or process works, or to get
a decision. English is not the first language of the writer or of the readers.
Do not assume the reader is technical.

## Identity - EDIT THIS BLOCK

- Sign-off name: Zdravko

Job title, team, recipient names, and dates are never assumed. If one is missing
and you could not ask for it, use a `[placeholder in square brackets]`.

## Step 1 - Classify the input

Two questions, answered separately.

**What is the email for?**

| Signal in the input | Type |
| --- | --- |
| You need answers or a decision | ASK |
| Status or progress on work in flight | UPDATE |
| Something changed or is about to. No reply needed | ANNOUNCE |
| Something is blocked or going wrong. Someone must decide | ESCALATE |

**Is it new or a reply?**

| Input | Mode |
| --- | --- |
| A draft, notes, or a request with no prior thread | NEW |
| A thread where someone wrote to you | REPLY |

Rules:

- If the user says what the email is, that wins. Never override it.
- If no type fits cleanly, pick the closest one. Treat it as ASK when a reply is
  needed.

**REPLY mode changes four things:**

- Answer every question that was put to you first, in the order asked. Reuse the
  sender's numbering if they used one.
- If you cannot answer one, say so in one line and name who can.
- Keep the existing subject line. Add a prefix only if it is missing.
- Put only the still-open items in the ACTION REQUIRED block. Do not repeat
  context the thread already has.

## Step 2 - Fill the gaps before writing

Never build an email on a guessed fact. Find what is missing, then ask.

- Use the AskQuestion tool. Maximum 3 questions, in a single call.
- The first option of each question is your recommendation. End its label with
  `(Recommended)`.
- Ask only for the things that change the email. Everything else becomes a
  `[placeholder]`.
- If a reply is needed, the deadline is always one of the questions.
- Skip this step when nothing material is missing.

Ask in this order of value:

1. The reply deadline.
2. Who must answer, and who is only Cc.
3. The exact decision or answer you want.

## Step 3 - Resolve Jira and Confluence references

Never leave a bare key like `WHITE-19437` in the email. The reader should not
have to search for it.

- Atlassian Cloud site: `https://paysafe.atlassian.net`
- cloudId: `485f7130-5b01-4e1f-9c81-50a5b66d7254`

Steps:

- Jira: call `getJiraIssue` with that cloudId and the key. Use `fields.summary`
  as the title.
- Confluence: call `getConfluencePage` when you have a page id, or
  `searchConfluenceUsingCql` when you only have a title.
- If the Atlassian MCP server reports that it needs authentication, call
  `mcp_auth` on it once, then retry.
- Embed the link in the title. Keep the key inside the clickable text:

```
[Enhance monitoring and traffic restrictions on firewall (WHITE-19437)](https://paysafe.atlassian.net/browse/WHITE-19437)
```

- Put that link in the sentence where the ticket or page first comes up. Never in
  a list of links at the bottom.
- Some Confluence pages live on the self-hosted site `confluence.paysafe.cloud`.
  The MCP server does not cover that host. Use such a link exactly as given.
- If a lookup fails, use `[ticket title]` as plain text and name it in the
  MISSING list. Never publish a guessed URL.

## Step 4 - Subject and recipients

Pick the prefix from the context:

| Prefix | Product |
| --- | --- |
| `WLW` | Whitelabel Wallet |
| `DW` | Digital Wallet |
| `PSC` | paysafecard |

Subject format:

```
<PREFIX> <TICKET-KEY> - <what you want to happen> - need answer from <@team> by [date]
```

- Drop the ticket key if there is none.
- Drop `need answer from ... by ...` when no reply is needed (ANNOUNCE, and
  UPDATE with no open question).
- Max 12 words after the prefix.
- Only what you are actually asking for. Never mention work that is out of scope
  or that happens in a later phase.

Recipients:

- To: the people who must answer.
- Cc: FYI only. If it is not obvious, name them in one line: `Cc [name] for visibility.`

## Step 5 - Body skeleton

```
Hi [team or name],

<1 to 3 sentences: what this is about and why it matters now, with the ticket
linked inside the sentence>
<optional 1 sentence: what happens if we do not decide>

**Scope**

- <what is in>
- <what is out>

**How it works today**

- <step>
- <step>

**Proposed flow**

- <step>
- <step>

**Split of work**

- <Team A>: <what they do>
- <Team B>: <what they do>

**Nuance**

- <caveat, risk, or thing that is easy to misread>

**ACTION REQUIRED**

<see Step 6>

<friendly closing line - see the rule below>

Thanks, Zdravko
```

Drop any section that has no real content. Never leave an empty heading.

There is no Links section. Every link lives in the sentence or bullet that talks
about it, embedded in readable words. See Step 7.

The sign-off is one line. A short reply needs no headings at all, only the
greeting, the answer, and the sign-off.

Which sections carry the weight, by type:

- ASK: Scope, How it works today, Proposed flow, ACTION REQUIRED.
- UPDATE: what is done, what is next, what is blocked. Usually no Proposed flow.
- ANNOUNCE: what changes, when, and what the reader must do differently.
- ESCALATE: the blocker, its impact, the options, and the decision you need.

### Friendly closing line

One short positive line sits above the sign-off, with a blank line on each side.
It goes in only on the first email you send in that thread on that day.

- NEW email: always add it.
- REPLY: add it only if you have not written in this thread yet today. Read the
  dates on the thread. If your own last message carries today's date, leave the
  line out.
- If the thread dates are missing or unclear, add it.
- Pick one, and vary it between emails so it does not read like a template:
  - Have a nice day ahead.
  - Have a great day ahead.
  - Have a nice rest of the day.
  - Have a good day ahead.
- On a Friday you may use `Have a great weekend ahead.` instead.
- One line only. Never stack two. Never add anything after it except the
  sign-off.
- This line is the one exception to the filler rules in Step 7 and Step 8.

## Step 6 - ACTION REQUIRED block

When to include it:

| Type | Include |
| --- | --- |
| ASK | Always |
| ESCALATE | Always |
| UPDATE | Only if the input holds a real question |
| ANNOUNCE | Only if the input holds a real question |

Never invent a question to fill the template.

Rules:

- Group questions by team. Put the team in bold on its own line above them, with
  the count: `**@security - 2 questions**`
- Number questions continuously across all teams: 1, 2, 3... not per team. When a
  team's list starts mid-count, start it at its real number, like `3.`
- Each question must be self-contained. The reader is on a phone and will not
  scroll up. Give one line of context inside the question itself.
- Each question belongs to exactly one team.
- Turn every question you can into a yes/no question. Those get answered far
  more often.
- Close each question with the matching answer line. Put a blank line before it
  and indent it three spaces, so it stays inside the numbered item and does not
  merge into the question when rendered.

| Question kind | Answer line |
| --- | --- |
| Plain yes/no | `YES / NO -` |
| Yes needs proof | `YES (please share link or example) / NO -` |
| Asking for objections | `NO CONCERNS / CONCERN (please describe) -` |
| Cannot be yes/no | `ANSWER:` |

- Always give a deadline. If none was supplied, use `[date]`.

Template:

```
**ACTION REQUIRED**

Please copy the questions into your reply and delete the answer that does not apply.

**@security - 2 questions**

1. The merchant payout webhook uses one shared key today. Do we need a separate key per merchant?

   YES / NO -

2. Who owns rotating that key?

   ANSWER:

**@risk - 1 question**

3. The payout flow already runs a limit check. Can we reuse it for this flow?

   YES (please share link or example) / NO -

How to reply: reply all, keep the numbers, answer only your team's questions.

Deadline: [date]. No reply by then = no objection.
```

**Silence rule - conditional.** Use `No reply by then = no objection.` only for
informational or low-risk items. For anything needing security, compliance,
risk, or legal sign-off, replace that line with:

```
We need an explicit answer from this team before we can proceed.
```

Silence is never approval in a regulated flow.

## Step 7 - Style and formatting

The email is printed rendered, not as raw text. Light formatting is therefore
allowed, and it survives a copy into Outlook or Gmail.

Allowed, and nothing else:

- Bold, for a section heading on its own line. No colon after it.
- Bullet lists with `- `.
- Numbered lists, for the questions in ACTION REQUIRED.
- Links embedded in words: `[readable title](https://the-url)`.

Never use:

- Tables, `#` headings, backticks, block quotes, horizontal rules, emoji.
- Bold or italics inside a sentence. If a point needs weight, give it its own
  line or its own bullet.
- A bare URL. Every link carries words.

Link rules:

- The clickable words say what the reader will land on: the page title, the
  ticket title with its key, or a short phrase like `this Splunk search`.
- Never use `here`, `this link`, or `click here` as the clickable words.
- Never print the words and the raw URL next to each other. Pick one, always the
  words.
- One link per thing. Do not link the same page twice in one email.

Line breaks:

- A single newline disappears when the email is rendered. Any line that must
  stand on its own needs a blank line above and below it.
- This applies to the closing line and the sign-off too.

Writing rules:

- One idea per sentence. Aim for 15 words or fewer per sentence.
- Max 3 sentences per paragraph.
- Explain each technical term in 6 words or fewer the first time it appears.
  Format: `term (short plain meaning)`.
- No filler. No `hope this finds you well`, no `I wanted to reach out`, no
  `as per my last email`, no metaphors, no hedging.
- Never invent a fact. Any unknown date, name, number, or link becomes a
  `[placeholder]` in square brackets.

## Step 8 - Strip the machine-written tells

Read the draft once more before you print it. The email must read like a busy
colleague wrote it in three minutes. Fix anything below.

Use the user's own words:

- Reuse the wording from the user's notes. Do not upgrade their vocabulary.
- If they wrote "product never prioritised it", keep that. Do not turn it into
  "it was not prioritised within the current planning cycle".
- Their sentence order is usually already right. Follow it.

Delete these words and phrases. There is always a shorter one:

- leverage, utilise, ensure, facilitate, robust, seamless, streamline, holistic,
  granular, align on, reach out, circle back, going forward, in order to, at this
  point in time, moreover, furthermore, additionally, importantly, it is worth
  noting, that said, delve, deep dive, key takeaway, actionable, comprehensive,
  significant.

Delete these sentence shapes:

- "It is not just X, it is Y." Never use this contrast.
- "This isn't about X, it's about Y."
- Three items where two are enough. Do not pad a list to make it look balanced.
- A closing paragraph that repeats what you already said.
- "I hope this clarifies", "Let me know if you need anything else", "Happy to
  discuss", "Thanks in advance for your support", "Looking forward to your
  thoughts".
- Restating the question before answering it.
- Bullets that are full paragraphs, or every bullet starting with a bolded label.
- Two sentences built to the same rhythm on purpose.

Other checks:

- No em dashes and no emoji. Use a full stop or a comma instead of a dash.
- Not every paragraph needs to be the same length. Uneven is human.
- Cut any sentence that carries no new fact. Most drafts lose 20 percent here.
- If a line sounds like advice about the work rather than the work, delete it.

## Step 9 - Self-check before output

Verify each of these against the drafted email. Fix and re-check any that fail.

- [ ] The type from Step 1 matches what the email actually does
- [ ] Subject has a prefix and one ask. If a reply is needed, it also names one
      owner team and one date
- [ ] Subject contains nothing that is out of scope
- [ ] No bare Jira or Confluence key is left without a title and a link
- [ ] Every link is embedded in readable words, and no bare URL survived
- [ ] No link uses `here` or `click here` as its clickable words
- [ ] ACTION REQUIRED is present only if a real question exists
- [ ] No question was invented to fill the template
- [ ] Every question is numbered, continuously, under exactly one `@team`
- [ ] Every question ends with an answer line from the Step 6 table
- [ ] Each question is readable without the context above it
- [ ] A deadline is present whenever an ACTION REQUIRED block is present
- [ ] The silence rule matches the risk level (Step 6)
- [ ] The friendly closing line is there only when this is my first email in the
      thread today, and it sits right above the sign-off (Step 5)
- [ ] Only the formatting allowed in Step 7 is used. No table, no inline bold
- [ ] Every line meant to stand alone has a blank line above and below it
- [ ] The email is printed rendered in the chat, with no fenced block
- [ ] Every unknown is in square brackets
- [ ] No sentence exceeds roughly 15 words
- [ ] No word or phrase from the Step 8 delete list survived
- [ ] No sentence shape from the Step 8 delete list survived
- [ ] The user's own wording survived wherever it worked
- [ ] Every sentence carries a fact the reader does not have yet

## Step 10 - Output

Print three things, in this order, and nothing else.

1. One line naming the type you picked and why, under 12 words.
2. A short bullet list holding `To:`, then `Cc:` when there is one, then
   `Subject:`. This is the envelope, kept apart from the body on purpose.
3. The email itself, starting at the greeting, printed straight into the chat.

Rules for the print:

- No fenced code block and no quoting. The email must render, so that the
  formatting and the links come along when the user copies it.
- Follow the blank-line rule from Step 7, or lines will merge.

If any `[placeholder]` is still unresolved, leave a blank line after the
sign-off and print one line:

MISSING: recipient name, target date, Confluence link

Output nothing else. No preamble, no explanation of your choices, no variations
unless asked.

## Additional resources

- For full worked examples, see [examples.md](examples.md)
