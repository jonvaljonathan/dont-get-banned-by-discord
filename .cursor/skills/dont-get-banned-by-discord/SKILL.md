---
name: dont-get-banned-by-discord
description: >-
  Best practices for coding agents building or testing Discord apps, plus a
  hard stop on contacting Discord, attaching to the Discord client, or
  automating a user account. Use when a task mentions Discord, a bot, OAuth,
  interactions, webhooks, a test server, Update Permissions, Authorize, a
  self-bot, a user token, discord.com, or the Discord desktop app.
---

# Don't get banned by Discord

Discord permits automation only through the documented **bot API** and **OAuth2**. Automating a normal user account (a self-bot) is forbidden and can suspend or terminate the account. A desktop or browser session token is a login token, not a bot token.

The hook denies the request. This skill is how you build and test anyway. Do not look for a bypass.

## Build

- One **bot user**, authenticated with the bot token from the Developer Portal (`Authorization: Bot …`). Documented routes only. Published rate limits only. On `429`, back off with Discord’s `Retry-After`. Do not rotate tokens, proxies, or clients to get more quota.
- Least privilege. Ask only for the permissions and intents the feature uses. Privileged intents stay off until Discord has approved them.
- Interactions: verify the Ed25519 signature, ack within Discord’s response window, and defer when the work is slower than that window. A missing permission (`50013`) or missing access (`50001`) is a failure the user can see. Do not treat it as success.
- OAuth starts when a **human** opens Discord’s authorize page. Handle the documented callback. Never complete that grant with a user session.
- Keep the bot token and client secret in the environment the app process reads. Never in the repo, a fixture, a log, or the chat.
- Use a private test server the human owns, and a separate test application from production when they have one. The agent never invites the bot and never clicks Authorize.

## Test

You write and run tests that never touch Discord’s network. A green run is not proof the bot is online.

1. **Fixtures, not the live API.** Build tests from payload shapes in Discord’s docs (interactions, webhook bodies, `429`, `401`, `50013`, `50001`). Do not record them by scraping the client or calling Discord.
2. **Mock the HTTP boundary.** Assert the code would call a documented path with `Authorization: Bot`, and that it stops on `401`, `429`, `50013`, and `50001`. Assert it does not retry in a loop.
3. **Signatures locally.** Verify Ed25519 with a test keypair against a fixture. Do not ask Discord whether a signature is valid.
4. **Idempotency.** Deliver the same interaction twice and assert the side effect happens once.
5. **No user credentials in tests.** No user token, password, desktop client, or “log in as me to click the button.”
6. **No Discord hosts.** If a test needs `discord.com`, `discord.gg`, or the other Discord hosts, it is the wrong test. Hit your own localhost endpoint with a signed fixture instead.

Live smoke is a checklist you hand the human. You do not run it.

```
Human smoke (you run this, the agent does not):
- [ ] Private test server you own. Production not used.
- [ ] You invited the bot from Discord’s authorize page.
- [ ] One command or button does the thing.
- [ ] A missing-permission case looks like a failure.
```

The human may start the app, which uses the bot token in-process. You still do not curl Discord to “see if it worked.”

## What you must not do

- Send any request to `discord.com`, `discordapp.com`, `discord.gg` (the Gateway), `discord.media`, or `discordapp.net`. Shell, browser, MCP, and bot-token curls are all included.
- Launch Discord with a debug port, attach CDP, or read `Discord.app`, Discord Canary, Discord PTB, or their Application Support folders.
- Read, store, log, or reuse a user session token. Do not scrape client storage.
- Call the OAuth authorize URL as the user, or click Authorize / Update Permissions for them.
- Add a self-bot, a user-token client, `TokenType.User`, or `loginAsUserAccount`.
- Pretend to be the official Discord client, scrape Discord, or evade rate limits.
- Ask anyone for a Discord password or session token.

## If the task needs a live Discord action

Stop. Say which click only the human can make. Do not attempt the call.

## Install

User-level hook (all projects): copy `hooks/block-discord-requests.py` to `~/.cursor/hooks/` and merge `hooks.fragment.json` into `~/.cursor/hooks.json` with `"failClosed": true`.

Copy `rules/discord-no-user-automation.mdc` to `~/.cursor/rules/`.

Copy this skill folder to `~/.cursor/skills/dont-get-banned-by-discord/`.
