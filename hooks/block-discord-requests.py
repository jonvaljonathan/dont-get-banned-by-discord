#!/usr/bin/env python3
"""Fail-closed: block agent traffic to Discord and Discord client attach.

Discord allows automation only through the documented bot API and OAuth2.
A user session token is not either of those. This hook stops the agent
from sending the request. It does not stop a human using the Discord app,
and it does not stop your own application process from using a bot token.
"""
from __future__ import annotations

import json
import re
import sys

DENY_MSG = (
    "BLOCKED: Agent must not contact Discord or attach to the Discord client. "
    "Discord forbids automating a normal user account outside the documented "
    "OAuth2 and bot APIs, and forbids collecting login or access tokens. "
    "Humans use the Discord UI. A running app may use a bot token in-process. "
    "Incident 2026-09-28."
)

# Hosts the agent must not touch. gateway.discord.gg is the Gateway;
# a discord.com-only check misses it.
_HOST = (
    r"(?:[a-z0-9-]+\.)*"
    r"(?:discord\.com|discordapp\.com|discord\.gg|discord\.media|discordapp\.net)"
)

PATTERNS: list[re.Pattern[str]] = [
    re.compile(rf"(?is)\b{_HOST}\b"),
    re.compile(
        r"(?is)(browser_navigate|WebFetch|page\.goto|connectOverCDP)"
        r".{0,200}discord"
    ),
    re.compile(
        r"(?is)(discord\.app|discord|Discord\.app).{0,400}remote-debugging-port"
    ),
    re.compile(
        r"(?is)remote-debugging-port.{0,400}"
        r"(discord\.app|Discord\.app|discord)"
    ),
    re.compile(r"(?is)webSocketDebuggerUrl.{0,300}(discord|Authorization)"),
    re.compile(r"(?is)Discord(?: PTB| Canary)?\.app\b"),
    re.compile(r"(?is)/Applications/Discord(?: PTB| Canary)?\.app"),
    re.compile(
        r"(?is)Application Support[/\\]+discord(?:ptb|canary)?\b"
    ),
    re.compile(r"(?is)\.asar\b.{0,80}discord|discord.{0,80}\.asar\b"),
    re.compile(r"(?is)discord-user-token"),
    re.compile(r"(?is)\bself[-_ ]?bot\b"),
    re.compile(r"(?is)loginAsUserAccount"),
    re.compile(r"(?is)TokenType\.User"),
    # Desktop client storage marker. Presence means a scrape, not a bot token.
    re.compile(r"(?is)dQw4w9WgXcQ:"),
]


def _blob(data: dict) -> str:
    parts: list[str] = []
    for key in (
        "command",
        "tool_input",
        "tool_name",
        "arguments",
        "input",
        "url",
        "server",
        "toolName",
    ):
        val = data.get(key)
        if val is None:
            continue
        if isinstance(val, (dict, list)):
            parts.append(json.dumps(val))
        else:
            parts.append(str(val))
    tool_input = data.get("tool_input")
    if isinstance(tool_input, dict):
        for key in (
            "command",
            "contents",
            "content",
            "new_string",
            "newString",
            "old_string",
            "path",
            "arguments",
            "code",
            "expression",
            "url",
        ):
            if key in tool_input and tool_input[key] is not None:
                v = tool_input[key]
                parts.append(
                    json.dumps(v) if isinstance(v, (dict, list)) else str(v)
                )
    elif isinstance(tool_input, str):
        parts.append(tool_input)
    for nest_key in ("arguments", "input", "params"):
        nested = data.get(nest_key)
        if isinstance(nested, dict):
            parts.append(json.dumps(nested))
        elif isinstance(nested, str):
            parts.append(nested)
    return "\n".join(parts)


def decide(data: dict) -> dict:
    text = _blob(data)
    for rx in PATTERNS:
        if rx.search(text):
            return {
                "permission": "deny",
                "user_message": DENY_MSG,
                "agent_message": DENY_MSG,
            }
    return {"permission": "allow"}


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        print(
            json.dumps(
                {
                    "permission": "deny",
                    "user_message": DENY_MSG + " (hook input invalid)",
                    "agent_message": DENY_MSG + " (hook input invalid)",
                }
            )
        )
        return
    if not isinstance(data, dict):
        print(
            json.dumps(
                {
                    "permission": "deny",
                    "user_message": DENY_MSG + " (hook input invalid)",
                    "agent_message": DENY_MSG + " (hook input invalid)",
                }
            )
        )
        return
    print(json.dumps(decide(data)))


if __name__ == "__main__":
    main()
