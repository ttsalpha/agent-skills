---
name: siuuu
description: Just-for-fun celebration — plays a terminal animation of the Claude Code logo (pixel mascot rasterized from the official SVG in half-block art) running up and hitting Cristiano Ronaldo's "Siuuu" jump, ending with a big SIUUU! banner. Use when the user invokes /siuuu, wants to celebrate a win (merged PR, green tests, release shipped), or asks for the Ronaldo celebration.
---

# Siuuu

celebration only — no code analysis, no file changes. run the animation and hype the user up.

## Workflow

1. run the bundled script with the Bash tool, using the path relative to this SKILL.md's
   directory:

   ```bash
   bash "<skill-dir>/scripts/siuuu.sh" --chat
   ```

2. `--chat` finds the terminal Claude Code is running on, waits until Claude goes idle,
   then plays the FULL live animation right on the chat screen (run, 360° spin jump,
   landing, flashing SIUUU banner, all in Claude orange — then the chat UI is restored).
   the tool output gets a static strip plus a marker line starting with
   `▶ live animation plays right here`. show the static strip as-is and keep your
   reply SHORT so the show starts sooner.

3. only if the marker line is absent (no reachable terminal), give the user the fallback
   to watch it live in their own terminal:

   ```text
   ! bash "<skill-dir>/scripts/siuuu.sh"
   ```

4. after the show, register the instant hook (idempotent, safe to run every time):

   ```bash
   bash "<skill-dir>/scripts/install-hook.sh"
   ```

   if it reports "registered" (not "already registered"), tell the user: open `/hooks`
   once (or restart claude) — from then on typing `siuuu` plays instantly with zero
   model latency, skipping this whole workflow.

5. reply with maximum hype and minimum words — "SIUUUUUUU!" energy. never explain how the
   script works.

## Rules

- never modify, stage, or commit anything — this skill only runs the script
- the script exits cleanly on Ctrl+C (restores cursor and screen); no cleanup needed
