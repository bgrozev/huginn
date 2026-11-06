"""Summarize a claude-code-action execution file: turns, tokens, blocked tool calls.

Usage: python3 scripts/usage.py <execution_file.json>   (prints Markdown, for $GITHUB_STEP_SUMMARY)

The execution file is the JSON list of SDK messages the action writes. Token counts are summed
from the final result message when it has `usage`, otherwise from each assistant message.
"""
import json
import sys

KEYS = ("input_tokens", "output_tokens", "cache_creation_input_tokens", "cache_read_input_tokens")


def main():
    with open(sys.argv[1]) as f:
        messages = json.load(f)
    result = next((m for m in reversed(messages) if m.get("type") == "result"), {})
    usage = result.get("usage")
    if not usage:
        usage = dict.fromkeys(KEYS, 0)
        for m in messages:
            u = (m.get("message") or {}).get("usage") if m.get("type") == "assistant" else None
            for k in KEYS:
                usage[k] += (u or {}).get(k) or 0
    print("### Claude usage\n")
    print("| | |\n|---|---|")
    print(f"| Turns | {result.get('num_turns', '?')} |")
    print(f"| Duration | {round((result.get('duration_ms') or 0) / 1000)} s |")
    for k in KEYS:
        print(f"| {k.replace('_', ' ')} | {usage.get(k, 0):,} |")
    if result.get("total_cost_usd") is not None:
        print(f"| API-price estimate (not billed on a subscription) | ${result['total_cost_usd']:.2f} |")
    denials = result.get("permission_denials") or []
    if denials:
        print("\n**Blocked tool calls**\n")
        for d in denials:
            print(f"- `{d.get('tool_name')}`: `{json.dumps(d.get('tool_input'))[:200]}`")


if __name__ == "__main__":
    main()
