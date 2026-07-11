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

## Skill Structure

Each skill contains:

- `SKILL.md` — Instructions for the agent

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
