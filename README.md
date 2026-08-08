# Snow's Agent Skills

## Installation

```bash
npx skills add ttsalpha/agent-skills
```

## Available Skills

### `/commit`

Generate conventional commit messages with auto-detected type and scope from diff.

**Use when:**

- Committing staged or unstaged changes
- Writing or improving a commit message
- Reviewing changes for commit readiness

### `/siuuu`

Just for fun — the Claude Code logo (pixel mascot, rendered in half-block art from the
official SVG) walks on in the dark, runs across the terminal and hits Ronaldo's "Siuuu"
celebration jump, ending with a big `SIUUU!` banner in Claude orange. Plays live right on the
chat screen. Mute with `SIUUU_SOUND=0`.

**Use when:**

- Celebrating a win (merged PR, green tests, release shipped)
- You just want to see it

**Instant mode:** on first use the skill registers a `UserPromptSubmit` hook in
`~/.claude/settings.json` (idempotent, backup kept, requires `python3`). After
opening `/hooks` once (or restarting), typing `siuuu` plays the celebration instantly —
no model turn, no tokens. Remove it anytime via `/hooks`.

## Skill Structure

Each skill contains:

- `SKILL.md` — Instructions for the agent
- `scripts/` — (optional) executable scripts bundled with the skill

## Adding a new skill

1. Create `skills/<skill-name>/SKILL.md` with frontmatter:

```markdown
---
name: skill-name
description: Short description — helps Claude know when to invoke this skill
---
```

2. Add an entry under **Available Skills** above.
3. Commit and push — team members re-run the install command to update.

## License

[MIT](LICENSE)
