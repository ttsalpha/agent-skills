---
name: commit
description: Execute git commits with conventional commit message analysis and generation. Use when the user asks to commit changes, write a commit message, or review staged changes. Follows the repo's existing commit convention, auto-detects type/scope from the diff, stages surgically, splits unrelated changes, and verifies the result. Never pushes or opens PRs.
---

# Commit

does: analyze diff → stage → write message → commit → verify.
does NOT: `git push`, open PRs, change git config, or run rebase/reset/revert itself.

- commit only when the user asked to commit; if they only asked for a message, draft it and stop
- budget: the common case finishes in **3 bash calls or fewer** (preflight, diff, commit+verify).
  every step marked optional runs only when its trigger fires

## Workflow

### 1. Preflight — one call

```bash
git status --short; git branch --show-current; git log --oneline -10
```

- clean tree → say "nothing to commit" and stop; mid-merge/rebase (`UU`, `AA`) → stop, say so
- no commits yet → this is the initial commit; skip the convention check below
- on `main`/`master` → note it in **one line** of your reply and carry on; don't ask, don't branch
- read `git log` for the convention in use (conventional / gitmoji / ticket-prefixed / free-form).
  **the repo's convention wins over the defaults below.** only if the log is mixed, spend one
  more call on `commitlint.config.*`, `.commitlintrc*`, `.czrc`, `.gitmessage`

### 2. Read the diff

```bash
git diff --staged --stat   # something is staged
git diff --stat            # nothing staged
```

`--stat` first tells you the size; then read the full diff (`git diff --staged` / `git diff`,
or `git diff -- <path>` per file when it's large).

**untracked files don't show up in `git diff` at all** — `git status` is the only place they
appear. read new files directly before writing the message.

**fast path:** small diff + self-evident intent → skip the analysis (not the staging or the
verify) and write a title-only commit.

body needed? judge from the diff alone: file count, public API/signature changes,
config/migration/dependency changes.

### 3. Stage

- something already staged → commit **exactly that**, add nothing (the user chose it)
- nothing staged → stage the relevant files **by name**: `git add src/auth/session.ts`
- never `git add -A`, `git add .`, or a broad glob — you'd commit what you didn't read
- `.env*`, keys, certs, credentials, build/generated output in `git status` → don't stage, say so

### 4. Split — optional, only for unrelated concerns

default is **one commit**. when the diff mixes genuinely unrelated concerns (bug fix +
dependency bump + reformat), propose a split and **wait for confirmation** — never split alone.

- pure formatting gets its own commit; a file with both logic and formatting stays with the logic
- tests ride with the code they test; dependency/config bumps are their own commit
- per group: stage by name → commit → `git status --short` → next. end with a clean tree
- unsure how to group → ask

### 5. Commit and verify — one call

```bash
# title-only
git commit -m "<type>(<scope>): <description>" && git log -1 --oneline && git status --short

# with body/footer
git commit -m "$(cat <<'EOF'
<type>(<scope>): <description>

<body>

Closes #123
EOF
)" && git log -1 --oneline && git status --short
```

- heredoc or repeated `-m` — never a literal `\n`, never an interactive editor
- verify with `--oneline`, not `--stat`; the file list is noise
- the message is public: no customer names, emails, ticket contents, or secrets — describe
  the technical symptom

### 6. When the commit isn't clean

- hook **failed** → read the error, fix the cause, re-stage, make a **new** commit
- hook **passed but rewrote files** → `git status --short` shows them; report which files
  changed and ask before staging the follow-up
- nothing got committed → say so and stop

### 7. Amend — optional, on explicit request only

only when the user says so ("fix the last commit", "reword the last message").

- already pushed (`git status -sb`; no upstream means nothing was pushed) → warn that it
  needs a force push and stop for them to decide
- last commit's author isn't `git config user.name` → stop, it isn't yours to rewrite

## Message Format

```text
<type>(<optional scope>): <description>

[optional body]

[optional footer(s)]
```

- English only, every part (type, scope, description, body, footer)
- `(scope)` only when it adds information; lowercase (`(auth)`, `(api)`, `(ui)`, `(deps)`)
- `description`: imperative (`add` not `added`), mostly lowercase, no trailing period, <= 72 chars
- keep technical identifiers in their real casing (`Button`, `React`, `TypeScript`, `iOS`)
- blank line between description and body, and between body and footer; wrap body at 72 chars
- reference issues when applicable (`Closes #123`, `Refs #456`); one logical change per commit

### Types

| Type       | When to use                                |
| ---------- | ------------------------------------------ |
| `feat`     | New feature or visible behavior change     |
| `fix`      | Bug fix                                    |
| `refactor` | Code restructuring without behavior change |
| `style`    | UI/visual changes, no logic change         |
| `perf`     | Measurable performance improvement         |
| `test`     | Adding or updating tests                   |
| `docs`     | Documentation only                         |
| `build`    | Build system, tooling, or CI changes       |
| `chore`    | Maintenance, housekeeping, config tweaks   |
| `revert`   | Reverting a previous commit                |

If none fit, use a more precise one (`vendor`, `cleanup`, `release`, `config`) rather than
forcing a core type.

### Breaking changes

```text
feat(api)!: change response shape

BREAKING CHANGE: response now returns `data` wrapper
```

## Body

| Situation                                                                | Body          |
| ----------------------------------------------------------------------- | ------------- |
| type + scope + description already carry the full intent                 | none          |
| small diff, non-obvious impact (workaround, invariant, side effect)      | 1–2 sentences |
| `fix` with non-trivial root cause, or `perf` where the why isn't evident | 1–2 sentences |
| many files, public API change, config/migration/dependency change        | full body     |
| architecturally significant `feat` or `refactor`                         | full body     |
| `BREAKING CHANGE`                                                        | always full   |

rule of thumb: if removing the body loses no information, skip it.
overrides: "short" / "just the title" → title-only; "detailed" / "explain more" → full body.

style: mostly lowercase, imperative, concise; `-` bullets for multiple concrete changes.

## Examples

```text
style(button): adjust padding on primary button
docs(readme): fix typo in setup instructions
vendor: upgrade react to 19
```

```text
fix(auth): handle token expiry on refresh

refresh flow silently swallowed the 401 — callers assumed
token was always valid after first login.
```

```text
refactor(user-service): simplify user service

the service had too many responsibilities before.
now it only handles user data operations.

- extract validation to separate validator class
- remove duplicate email checking logic
```

## Safety

- NEVER push, open a PR, or update git config
- NEVER run destructive commands (`--force`, hard reset) without an explicit request
- NEVER skip hooks (`--no-verify`) or auto-`--amend` after a hook rewrote files
- NEVER amend a commit that's pushed or that you didn't author
- NEVER `git add -A` / `git add .`
- NEVER commit secrets (`.env`, credentials, private keys)
- NEVER add a `Co-Authored-By` trailer
