# Install

These files are meant to live in your user Cursor config so they apply in every project. A rule alone will not stop the request. The hook will.

## 1. Hook

```bash
mkdir -p ~/.cursor/hooks
cp hooks/block-discord-requests.py ~/.cursor/hooks/block-discord-requests.py
chmod +x ~/.cursor/hooks/block-discord-requests.py
```

Merge this into `~/.cursor/hooks.json`. If that file already has a `"hooks"` object, add these three entries inside it. Do not remove hooks you already rely on.

```json
{
  "version": 1,
  "hooks": {
    "preToolUse": [
      {
        "command": "python3 ./hooks/block-discord-requests.py",
        "matcher": "Shell|CallDynamicTool",
        "failClosed": true
      }
    ],
    "beforeShellExecution": [
      {
        "command": "python3 ./hooks/block-discord-requests.py",
        "failClosed": true
      }
    ],
    "beforeMCPExecution": [
      {
        "command": "python3 ./hooks/block-discord-requests.py",
        "failClosed": true
      }
    ]
  }
}
```

User hooks run from `~/.cursor/`, so the path `./hooks/block-discord-requests.py` is correct there.

`"failClosed": true` means a crash, a timeout, or bad output blocks the action.

## 2. Rule

```bash
mkdir -p ~/.cursor/rules
cp rules/discord-no-user-automation.mdc ~/.cursor/rules/
```

## 3. Skill

```bash
mkdir -p ~/.cursor/skills
cp -R .cursor/skills/dont-get-banned-by-discord ~/.cursor/skills/
```

## 4. Prove it

```bash
python3 scripts/self-test.py
```

Expect `all passed`. Then start a new agent chat and ask it to `curl` Discord. The hook should deny it.

## What stays allowed

- You, in the official Discord app or the Developer Portal.
- Your application process, using a bot token, on documented routes, within published rate limits.

The agent does not get to send those requests for you.
