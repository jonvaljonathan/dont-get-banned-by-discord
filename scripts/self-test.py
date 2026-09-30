#!/usr/bin/env python3
"""Prove the hook denies Discord traffic and allows an unrelated command."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOOK_PATH = ROOT / "hooks" / "block-discord-requests.py"


def load_decide():
    spec = importlib.util.spec_from_file_location("block_discord_requests", HOOK_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {HOOK_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.decide


def main() -> int:
    decide = load_decide()
    cases = [
        ("curl discord.com", {"command": "curl https://discord.com/api/v9/users/@me"}, "deny"),
        ("gateway discord.gg", {"command": "websocat wss://gateway.discord.gg/?v=10"}, "deny"),
        ("cdn discordapp", {"command": "curl https://cdn.discordapp.com/embed/avatars/0.png"}, "deny"),
        ("discord.media", {"command": "curl https://cdn.discord.media/x"}, "deny"),
        ("discordapp.net", {"command": "curl https://media.discordapp.net/x"}, "deny"),
        ("debug port", {"command": "open -a Discord --args --remote-debugging-port=9222"}, "deny"),
        ("client data dir", {"command": "ls ~/Library/Application Support/discord"}, "deny"),
        ("canary app", {"command": "ls /Applications/Discord Canary.app"}, "deny"),
        ("self-bot flag", {"command": "npm install some-self-bot"}, "deny"),
        ("unrelated", {"command": "python3 -c 'print(1+1)'"}, "allow"),
    ]
    failed = 0
    for name, payload, expected in cases:
        got = decide(payload)["permission"]
        if got != expected:
            print(f"FAIL {name}: expected {expected}, got {got}")
            failed += 1
        else:
            print(f"ok   {name}: {got}")
    if failed:
        print(f"{failed} failed")
        return 1
    print("all passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
