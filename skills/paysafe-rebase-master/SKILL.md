---
name: paysafe-rebase-master
description: >-
  Fetches the latest origin/master and rebases the current branch onto it,
  auto-resolving version-only conflicts by fixing gradle.properties and
  CHANGELOG.md, and aborting with a report on any non-version conflict. Use when
  rebasing, syncing, or updating the current branch with master, pulling latest
  master changes, or resolving version / CHANGELOG rebase conflicts in this
  repository.
---

# Paysafe rebase on master

Rebase the current branch onto the latest `origin/master`. Resolve **version-only**
conflicts automatically; for **any other** conflict, **do nothing** (abort the rebase and
report), leaving the branch exactly as it was.

## Conflict policy

- **Auto-resolve** when the conflicted files are only `gradle.properties` and/or
  `CHANGELOG.md`, AND any `gradle.properties` conflict is limited to the `version` line.
  Recompute the version and rebuild `CHANGELOG.md` so both files are correct.
- **Do nothing** (abort + report) when any other file conflicts, or when
  `gradle.properties` conflicts on a non-`version` line (e.g. `group`, `description`). Do
  not attempt resolution; restore the branch and tell the user which files conflicted.

## Preconditions — stop and report if any fail

- Working tree clean: `git status --porcelain` is empty (never risk losing uncommitted work).
- On a real feature branch: not `master`, not detached HEAD.
- No rebase/merge already in progress.

Default target is `origin/master` (this repo's remote default branch).

## Workflow

### 1. Fetch + start rebase

```bash
git status --porcelain                     # must be empty, else stop
CUR=$(git rev-parse --abbrev-ref HEAD)     # current branch name
timeout 120 git fetch origin master
git rebase origin/master
```

- Exit 0 and rebase completes with no stop → clean rebase, go to **Step 4**.
- Stops with `CONFLICT` → go to **Step 2**.

### 2. Classify the conflict

```bash
git diff --name-only --diff-filter=U       # currently conflicted files
```

- Every conflicted file is in `{gradle.properties, CHANGELOG.md}` → if `gradle.properties`
  is among them, read it and confirm the conflict markers wrap only the `version = ...`
  line. If so → **Step 3**.
- Anything else (other files, or a `gradle.properties` conflict on non-`version` lines) →
  **do nothing**:

```bash
git rebase --abort                         # branch restored to pre-rebase state
```

Report: rebase aborted, branch unchanged, list the non-version conflicted files, and
suggest the user rebase manually. **Stop here.**

### 3. Resolve the version-only conflict

Rebase semantics: `HEAD`/`ours` = master, `theirs` = the branch commit being replayed,
`ORIG_HEAD` = branch tip before the rebase.

Compute the new version by applying the branch's own bump component on top of master's
current version:

```bash
ver() { git show "$1:gradle.properties" | sed -n 's/^version = //p' | tr -d '[:space:]'; }
MASTER_VER=$(ver origin/master)
BRANCH_VER=$(ver ORIG_HEAD)
BASE_VER=$(ver "$(git merge-base ORIG_HEAD origin/master)")
IFS=. read -r mX mY mZ <<<"$MASTER_VER"
IFS=. read -r bX bY bZ <<<"$BRANCH_VER"
IFS=. read -r sX sY sZ <<<"$BASE_VER"
if   [ "$bX" != "$sX" ]; then NEW_VER="$((mX+1)).0.0"      # branch did a major bump
elif [ "$bY" != "$sY" ]; then NEW_VER="${mX}.$((mY+1)).0"  # branch did a minor bump
elif [ "$bZ" != "$sZ" ]; then NEW_VER="${mX}.${mY}.$((mZ+1))"  # branch did a patch bump
else NEW_VER="$MASTER_VER"; fi
echo "master=$MASTER_VER branch=$BRANCH_VER base=$BASE_VER -> new=$NEW_VER"
```

Extract the branch's changelog entry (its newest block) and master's changelog body:

```bash
git show ORIG_HEAD:CHANGELOG.md | awk 'BEGIN{n=0}/^### Version /{n++}n==2{exit}n>=1{print}'
git show origin/master:CHANGELOG.md | awk '/^### Version /{p=1}p'
```

**Safety gate:** the branch block's first line must be `### Version $BRANCH_VER`. If it is
not (e.g. the branch added multiple new blocks, or a non-standard layout), take the
**do nothing** path from Step 2 (`git rebase --abort`) and report.

Write both files with the file tools, fully overwriting the conflict-marked versions:

- `gradle.properties`: start from `git show origin/master:gradle.properties`, and set only
  its `version` line to `version = <NEW_VER>`. Keep every other line from master.
- `CHANGELOG.md`: assemble as below — branch block renumbered to `NEW_VER` on top, then
  master's full body. Exactly one blank line between the header and the first block and
  between blocks; no conflict markers remain.

```markdown
# Release Notes

### Version <NEW_VER>
- <branch block bullets, including its Jira URL, verbatim>

### Version <MASTER_VER>
- <master's existing entries, unchanged, down to the end of the file>
```

Stage and continue (avoid the editor):

```bash
git add gradle.properties CHANGELOG.md
GIT_EDITOR=true git rebase --continue
```

- Stops again on a later commit → back to **Step 2**.
- Exit 0 / rebase reports done → **Step 4**.

### 4. Verify + report

```bash
git status                                        # no rebase in progress, tree clean
sed -n 's/^version = //p' gradle.properties       # -> NEW_VER
awk '/^### Version /{print; exit}' CHANGELOG.md    # -> ### Version NEW_VER
git log --oneline origin/master..HEAD             # branch commits replayed onto master
```

Checks:
- `version` in `gradle.properties` equals the top `### Version` in `CHANGELOG.md`.
- `NEW_VER` is strictly greater than `MASTER_VER`, with no duplicate version block.

Report: `CUR` rebased onto `origin/master@<MASTER_VER>`; version `BRANCH_VER → NEW_VER` (or
"no version conflict" for a clean rebase); CHANGELOG merged.

## Notes

- **Never force-push automatically.** The rebase rewrites history; if the branch was already
  pushed, tell the user to run `git push --force-with-lease` themselves.
- If the branch added more than one new CHANGELOG block, or resolution's safety gate fails,
  fall back to the **do nothing** path and let the user resolve manually.
