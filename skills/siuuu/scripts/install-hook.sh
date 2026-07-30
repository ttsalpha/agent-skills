#!/bin/bash
# One-time, idempotent setup: register the instant-siuuu UserPromptSubmit hook in
# ~/.claude/settings.json so typing "siuuu" plays the celebration with zero model
# latency. JSON is edited with python3 only (never raw bash — a broken settings.json
# silently disables all settings); backs up first, prints manual instructions if
# python3 is missing. Re-running is a no-op.
set -u

SETTINGS="$HOME/.claude/settings.json"
HOOK_CMD='bash ~/.claude/skills/siuuu/scripts/hook.sh'

if [ -f "$SETTINGS" ] && grep -q 'siuuu/scripts/hook.sh' "$SETTINGS" 2>/dev/null; then
  echo 'siuuu hook already registered — nothing to do'
  exit 0
fi

if ! command -v python3 >/dev/null 2>&1; then
  cat <<EOF
python3 not found — add this to "hooks" in ~/.claude/settings.json yourself:
  "UserPromptSubmit": [
    { "hooks": [ { "type": "command", "command": "$HOOK_CMD",
                   "timeout": 10, "statusMessage": "SIUUU!" } ] }
  ]
then open /hooks once (or restart claude) to activate.
EOF
  exit 1
fi

mkdir -p "$HOME/.claude"
[ -f "$SETTINGS" ] || printf '{}\n' > "$SETTINGS"
cp "$SETTINGS" "$SETTINGS.siuuu-backup"

if ! python3 - "$SETTINGS" "$HOOK_CMD" <<'EOF'
import json, sys

path, cmd = sys.argv[1], sys.argv[2]
with open(path) as f:
  settings = json.load(f)

hook = {'type': 'command', 'command': cmd, 'timeout': 10, 'statusMessage': 'SIUUU!'}
settings.setdefault('hooks', {}).setdefault('UserPromptSubmit', []).append({'hooks': [hook]})

with open(path, 'w') as f:
  json.dump(settings, f, indent=2, ensure_ascii=False)
  f.write('\n')
EOF
then
  echo 'python3 edit failed — restore from settings.json.siuuu-backup if needed'
  exit 1
fi

echo 'siuuu hook registered (backup: settings.json.siuuu-backup)'
echo 'activate: open /hooks once (or restart claude) — then typing "siuuu" plays instantly'
