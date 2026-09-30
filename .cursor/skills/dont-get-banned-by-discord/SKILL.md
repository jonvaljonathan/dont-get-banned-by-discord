---
name: dont-get-banned-by-discord
description: >-
  Stops a coding agent from contacting Discord, attaching to the Discord
  client, or automating a user account. Use when a task mentions Discord,
  a bot token, OAuth, Update Permissions, Authorize, self-bot, user token,
  discord.com, or the Discord desktop app.
---

# Don't get banned by Discord

Discord permits automation only through the documented **bot API** and **OAuth2**. Automating a normal user account (a self-bot) is forbidden and can terminate the account. A desktop or browser session token is a login token, not a bot token.

The hook denies the request. This skill tells you what not to build. Do not look for a bypass.

## What you must not do

- Send any request to `discord.com`, `discordapp.com`, `discord.gg` (the Gateway), `discord.media`, or `discordapp.net`. Shell, browser, MCP, and bot-token curls are all included.
- Launch Discord with a debug port, attach CDP, or read `Discord.app`, Discord Canary, Discord PTB, or their Application Support folders.
- Read, store, log, or reuse a user session token. Do not scrape client storage.
- Call the OAuth authorize URL as the user, or click Authorize / Update Permissions for them.
- Add a self-bot, a user-token client, `TokenType.User`, or `loginAsUserAccount`.
- Pretend to be the official Discord client, scrape Discord, or evade rate limits.
- Ask anyone for a Discord password or session token.

## What you may do

- Write app code that uses a **bot token** (`Authorization: Bot …`) inside the running process, on documented bot routes, within published rate limits. You do not execute those calls yourself.
- Write OAuth that opens Discord’s authorize page for a **human** and handles the documented callback. You never finish that grant with a stolen session.
- Tell the human what to click in the Discord app or the Developer Portal.

## If the task needs a live Discord action

Stop. Say which click only the human can make. Do not attempt the call.

## Install

User-level hook (all projects): copy `hooks/block-discord-requests.py` to `~/.cursor/hooks/` and merge `hooks.fragment.json` into `~/.cursor/hooks.json` with `"failClosed": true`.

Copy `rules/discord-no-user-automation.mdc` to `~/.cursor/rules/`.

Copy this skill folder to `~/.cursor/skills/dont-get-banned-by-discord/`.
