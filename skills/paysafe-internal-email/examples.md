# Examples

The emails below sit inside fenced blocks so you can see the raw markdown. The
real output is printed rendered in the chat, with no fence. See Step 10.

## Example 1 - NEW ASK

**Input (raw notes from the user):**

```
need to ask security + risk about the new merchant payout webhook for whitelabel
wallet. right now one shared HMAC key for all merchants. we want per-merchant
keys. also unclear who rotates them. risk side: can we reuse the existing
velocity limit check or do they want a new one. platform team builds the key
store, my team wires the webhook. want answers this week. confluence page exists
but i don't have the link handy.
```

**Output:**

```
Type: ASK. Security and risk must decide before build starts.

- To: Security team; Risk team
- Subject: WLW - agree per-merchant webhook keys - need answer from @security by [date]

Hi Security and Risk teams,

We want to change how the merchant payout webhook is signed. Today all merchants
share one HMAC key (a secret used to prove a message is genuine). We want one key
per merchant instead, so one leaked key cannot affect everyone.

**Scope**

- In: signing keys for the merchant payout webhook
- Out: any other webhook, and the payout logic itself

**How it works today**

- One shared HMAC key signs every merchant payout webhook
- The key is stored in [key store name]
- Nobody owns rotating it

**Proposed flow**

- Each merchant gets its own HMAC key
- The key store issues and stores the key
- The webhook service picks the key by merchant ID

**Split of work**

- Platform team: build the key store changes
- My team: wire the webhook service to the new key store

**Nuance**

- Existing merchants keep working during the change. We plan to accept both the old and the new key for [number] days.
- The full design sits on the [Confluence page title] page.

**ACTION REQUIRED**

Please copy the questions into your reply and delete the answer that does not apply.

**@security - 2 questions**

1. Today one shared HMAC key signs all merchant payout webhooks. Do you agree we move to one key per merchant?

   YES / NO -

2. Who owns rotating the per-merchant keys once they exist?

   ANSWER:

**@risk - 1 question**

3. The payout flow already runs a velocity check (a limit on how much can move in a time window). Can we reuse it as is for this change?

   YES (please share link or example) / NO -

How to reply: reply all, keep the numbers, answer only your team's questions.

Deadline: [date]. We need an explicit answer from this team before we can proceed.

Have a nice day ahead.

Thanks, Zdravko

MISSING: deadline date, key store name, dual-key window in days, Confluence link
```

Note: the silence line was replaced because security and risk sign-off is
required. Lazy consensus does not apply here. The Confluence link was not
available, so the title stays plain text and the link is named in MISSING. The
closing line is there because this is a new thread.

---

## Example 2 - REPLY

**Input (thread):**

```
From: Maria (Risk), today 11:20
> 1. Which merchants are in the first batch?
> 2. Does this change the payout timing?
> 3. We will need a new limit rule. Who builds it?

(she is replying to my mail from today 09:05)

my answers: first batch is the 3 pilot merchants, names are in the confluence
page. timing does not change. i don't know who builds the limit rule - probably
risk engineering, need to confirm. still waiting on security for the key
rotation owner.
```

**Output:**

```
Type: ASK, REPLY mode. Answers given, two items still open.

- To: Maria
- Cc: Security team
- Subject: RE: WLW - agree per-merchant webhook keys

Hi Maria,

Answers below.

1. The first batch is the 3 pilot merchants. Their names are on the [Confluence page title] page.
2. No. Payout timing does not change.
3. I do not know. I think Risk Engineering owns it, but please confirm.

One item is still open with Security.

**ACTION REQUIRED**

Please copy the questions into your reply and delete the answer that does not apply.

**@risk - 1 question**

1. Does Risk Engineering own building the new limit rule for per-merchant webhook keys?

   YES / NO -

**@security - 1 question**

2. Who owns rotating the per-merchant webhook keys?

   ANSWER:

How to reply: reply all, keep the numbers, answer only your team's questions.

Deadline: [date]. We need an explicit answer from this team before we can proceed.

Thanks, Zdravko

MISSING: deadline date, Confluence link
```

Note: the subject is unchanged in REPLY mode. The context from the thread is not
repeated. Only the still-open items appear in ACTION REQUIRED, renumbered from 1.
There is no friendly closing line, because Zdravko already wrote in this thread
at 09:05 the same day.

---

## Example 3 - ANNOUNCE, no ACTION REQUIRED

Shows three things: a resolved Jira key linked inside a sentence, an email with
no questions, and no Links section at the bottom.

**Input (raw notes from the user):**

```
tell the mobile and web SDK teams about WHITE-19437. we are going to alert on
requests that arrive without the mandatory headers, then later block them. so
they must keep sending User-Agent, Paysafe-Wallet-Version and
Paysafe-Wallet-Platform on every call. alerting only at first, no blocking yet.
just fyi, nothing to decide.
```

**Output:**

```
Type: ANNOUNCE. Informational only, no decision needed from the readers.

- To: Mobile SDK team; Web SDK team
- Subject: WLW WHITE-19437 - firewall will alert on missing SDK headers

Hi Mobile and Web SDK teams,

We are adding firewall monitoring for the Wallet SDKs, tracked under [Enhance monitoring and traffic restrictions on firewall (WHITE-19437)](https://paysafe.atlassian.net/browse/WHITE-19437). The firewall (the filter in front of our services) will start alerting when a request arrives without the mandatory headers.

Alerting only for now. No request will be blocked in this step.

**What changes**

- The firewall raises an alert on requests missing the mandatory headers
- Blocking rules may follow in a later phase, announced separately

**What you must keep doing**

- Send User-Agent on every call
- Send Paysafe-Wallet-Version on every call
- Send Paysafe-Wallet-Platform on every call

**Nuance**

- Nothing to change in your code if you already send all three headers. This email is only so an alert on your service does not surprise you.

Have a great day ahead.

Thanks, Zdravko
```

Note: no ACTION REQUIRED block, no deadline, and no `need answer from` in the
subject. Nothing was asked of the reader, so nothing was invented. The ticket is
linked inside the first sentence instead of sitting in a list at the bottom. The
closing line is a different one from Example 1 on purpose.
