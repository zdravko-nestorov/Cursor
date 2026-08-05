---
name: sync-global-rules
description: Push rule files from ~/.cursor/rules/ into Cursor Settings User Rules so they apply in every project. Use when a global rule file changed, when adding or removing a global rule, or when a rule does not seem to apply outside the .cursor workspace.
---

# Sync Global Rules

## Why this exists

Cursor has two separate rule systems:

| Where | Scope | Storage |
|-------|-------|---------|
| `.cursor/rules/*.mdc` | The open workspace only | Files |
| Settings User Rules | Every project on this machine | Cursor settings database |

Files in `~/.cursor/rules/` are **not** global. Cursor treats them as project
rules for the `~/.cursor` workspace. They do nothing when you open another repo.
Cursor staff have confirmed that global loading from `~/.cursor/rules` is not
supported.

Settings User Rules are the only reliable global layer, and they are not files.

This skill bridges the two. The files stay the source of truth in git. The
Settings copies are generated output.

Do not try to solve this with a `sessionStart` hook. Home-directory hooks are
global and `additional_context` is documented, but there are open bugs where the
injected context is dropped before the first message.

## What gets synced

| File in `~/.cursor/rules/` | User rule title |
|---|---|
| `writing-style.mdc` | Writing Style |
| `agent-skills.mdc` | Agent Skills Routing |
| `communication-style.mdc` | Communication Style |

`cursor-playbook.mdc` is deliberately **not** synced. It is guidance for working
on the `.cursor` folder itself, so workspace scope is correct for it.

When the user adds a new rule file, ask whether it should be global. If yes, add
a row to the table above as part of the sync.

## Procedure

1. Read every file listed in the table.

2. Strip the YAML frontmatter from each one. Everything between the opening
   `---` and the closing `---` is Cursor project-rule metadata. User rules have
   no frontmatter, so it must not be copied. Sync the body only, starting at the
   first line after the closing `---`.

   Trim blank lines from the start and the end of the body. Keep every newline
   inside it. Collapsing the inner newlines is the most common sync mistake and
   it makes numbered lists run together into one paragraph.

3. List the current user rules:

   - server: `cursor-app-control`
   - tool: `cursor_dialog`
   - arguments: `{"item": "rule", "scope": "user", "action": "list"}`

4. For each row in the table, compare the file body to the user rule with that
   title:

   - Title exists and content differs, use `action: "update"` with the `id` from
     the list, the title, and the file body as `content`.
   - Title is missing, use `action: "add"` with the title and the file body.
   - Content already matches, do nothing and say so.

5. Report any user rule that is **not** in the table. Do not delete it without
   asking. It may be something the user added on purpose in the UI.

6. Re-run the list and confirm each synced rule matches its file.

## Verification

The sync worked when both of these are true:

- Every title in the table appears in the user rules list.
- Each user rule body is identical to its file body with the frontmatter removed.

To check a single file body from the shell, print it without the frontmatter:

```bash
awk 'f{print} /^---$/{c++; if(c==2) f=1}' ~/.cursor/rules/writing-style.mdc
```

Compare that output to the `content` field returned by the list call.

## Notes

- User rules apply to Agent chat only. They are not used by Tab or by inline
  edit with Cmd+K.
- Rule precedence is Team Rules, then Project Rules, then User Rules.
- User rules are not included in Cursor profile exports. Keeping the files in git
  is what makes this setup portable to a new machine. Run this skill after
  cloning the `.cursor` repo somewhere new.
- Inside the `~/.cursor` workspace the synced rules load twice, once as project
  rules and once as user rules. That is expected and harmless.
