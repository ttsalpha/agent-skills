---
name: commit
description: Execute git commits with conventional commit message analysis and generation. Use when the user asks to commit changes, write a commit message, or review staged changes. Supports auto-detecting type/scope from diff, generating messages, and staging files intelligently.
---

# Commit

use this skill whenever the user asks to:

- commit changes (staged or unstaged)
- write or improve a commit message
- review changes for commit readiness

## Commit Message Format

```text
<type>(<optional scope>): <description>

[optional body]

[optional footer(s)]
```

rules:

- all commit messages must be in English (type, scope, description, body, footer)
- use `(scope)` only when needed; keep it lowercase (e.g. `(auth)`, `(api)`, `(ui)`, `(deps)`, `(config)`)
- `description`: mostly lowercase, imperative mood (`add` not `added`), no trailing period, <= 72 chars
- keep technical identifiers in their real casing (e.g. `Button`, `React`, `TypeScript`, `iOS`)
- always one blank line between description and body; one blank line between body and footer
- wrap body lines at 72 characters
- reference issues when applicable (`Closes #123`, `Refs #456`)
- keep one logical change per commit; if multiple concerns exist, choose the dominant one or split commits

### Types

Core types (prefer these):

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

If none fit, use a more specific type (e.g. `vendor`, `cleanup`, `release`, `config`). Choose the most precise match — don't force a core type when a specific one is clearer.

### Breaking Changes

```text
feat(api)!: change response shape

BREAKING CHANGE: response now returns `data` wrapper
```

## Body

### When to write

**skip body when:**

- type + scope + description already communicate the full intent
- rule of thumb: if removing the body loses no information, skip it

**write a short body (1–2 sentences) when:**

- diff is small but impact is non-obvious (workaround, subtle invariant, side effect)
- a `fix` that patches a non-trivial root cause
- a `perf` change where the why isn't self-evident

**write a full body when:**

- diff touches multiple areas or has many moving parts
- `feat` or `refactor` with architectural significance
- `BREAKING CHANGE` — always requires body regardless of diff size

**self-check before writing body:**

1. does type + scope + description already communicate the full intent? → skip body
2. does the change have a side effect, workaround, or impact beyond the visible diff? → needs body
3. is there a `BREAKING CHANGE`? → always write body

**natural language overrides:**

- user says "short" / "just the title" → title-only, no body
- user says "detailed" / "explain more" → full body

### Style

- keep body text mostly lowercase; preserve real casing for technical names
- use imperative and concise wording
- use `-` bullets when listing multiple concrete changes; one space after bullet marker
- leave a blank line between bullet groups when readability improves

## Workflow

### 1. Analyze diff

```bash
git diff --staged   # if files are staged
git diff            # only if nothing is staged
```

**fast path** (trivial commits — reduces token usage):

- if diff is small AND intent is self-evident from the diff:
  → generate title-only commit immediately, skip further analysis
- do NOT run all three of `git status` + `git diff` + `git diff --staged` unless needed

**codegraph impact check** (only for small `fix`/`refactor` diffs):

- call `codegraph_impact` or `codegraph_callers` on the changed symbol
- broad callers/impact → high impact → write body
- narrow/isolated impact → skip body
- skip entirely when diff is obviously trivial

### 2. Stage files (if needed)

```bash
git add path/to/file
git add src/components/*
```

Never commit secrets (`.env`, credentials, private keys).

### 3. Generate message

Apply Body Decision, then execute:

```bash
# title-only
git commit -m "<type>(<optional scope>): <description>"

# with body/footer
git commit -m "$(cat <<'EOF'
<type>(<optional scope>): <description>

<body>

Closes #123
EOF
)"
```

## Examples

core types:

```text
feat(auth): add OAuth2 login flow
fix(api): resolve null pointer on empty response
style(button): update loading state indicator
refactor: rename btn component to Button
build(deps): upgrade dependencies to latest
chore: remove unused imports
```

extended types:

```text
vendor: upgrade react to 19
config: update eslint rules
cleanup: remove legacy order flow
release: bump version to 2.1.0
```

title-only (no body needed):

```text
style(button): adjust padding on primary button
chore: remove commented-out debug logs
docs(readme): fix typo in setup instructions
```

short body (small diff, non-obvious impact):

```text
fix(auth): handle token expiry on refresh

refresh flow silently swallowed the 401 — callers assumed
token was always valid after first login.
```

full body + bullets:

```text
refactor(user-service): simplify user service

the service had too many responsibilities before.
now it only handles user data operations.

- extract validation to separate validator class
- remove duplicate email checking logic
- improve error messages for better ux
```

## Git Safety Protocol

- NEVER update git config
- NEVER run destructive commands (`--force`, hard reset) without explicit request
- NEVER skip hooks (`--no-verify`) unless user explicitly asks
- NEVER force push to `main`/`master`
- NEVER add `Co-Authored-By` trailer to commit messages
- if commit fails due to hooks, fix the issue and create a new commit
