#!/bin/bash
# UserPromptSubmit hook: instant /siuuu — plays the celebration on the chat terminal
# with zero model latency, then blocks the prompt (no model turn, no tokens).
# Any other prompt: exits silently and the prompt proceeds as normal.
set -u

input=$(cat)
if command -v jq >/dev/null 2>&1; then
  prompt=$(printf '%s' "$input" | jq -r '.prompt // empty' 2>/dev/null)
else
  prompt=''
  case "$input" in
    *'"prompt":"/siuuu"'*) prompt='/siuuu' ;;
    *'"prompt":"siuuu"'*) prompt='siuuu' ;;
  esac
fi

case "$prompt" in
  /siuuu|siuuu|SIUUU|/SIUUU)
    dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
    bash "$dir/siuuu.sh" --chat >/dev/null 2>&1
    printf '{"decision":"block","reason":"SIUUUUUUUUUU! 🐐⚽"}\n'
    ;;
esac
exit 0
