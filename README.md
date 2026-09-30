# My agent got my Discord account suspended

On 2026-09-28 a coding agent attached a debugger to the Discord desktop app, copied the logged-in session, and called Discord’s authorize API as that user. Discord suspended the account the same day. That suspension has since been lifted. The account is still at risk.

This repo is the hook, the rule, and the skill that stop a repeat. The hook is the part that matters. It refuses the agent’s request before it leaves the machine.

I am posting this in the Discord Developers server. Ask me anything.

## What I had asked for

I asked the agent to prove a bot webhook and to put a test server into the “Update Permissions” state. I expected it to tell me what to click, or to use the bot the way the bot API allows.

## What it did

It tried to read the desktop app’s local storage. Those tokens are encrypted, so that failed. It then relaunched Discord with a remote debugging port, attached with the Chrome DevTools Protocol, and copied the `Authorization` header from the logged-in client. That header is a user session. It used that session to call Discord’s OAuth authorize endpoint, as me, including a second time to change a bot’s permissions.

I did not click Authorize. The agent did.

## What Discord’s rules say

Discord’s docs draw a bright line. Automation is a **bot user** with a **bot token**, or **OAuth2** where a person approves the app on Discord’s own screen.

From the current OAuth2 docs ([`developers/topics/oauth2.mdx`](https://github.com/discord/discord-api-docs/blob/main/developers/topics/oauth2.mdx)):

> Developers must abide by the terms of service, which includes refraining from automating standard user accounts (generally called "self-bots") outside of the OAuth2/bot API.

Discord’s help article [Automated User Accounts (Self-Bots)](https://support.discord.com/hc/en-us/articles/115002192352-Automated-User-Accounts-Self-Bots) says the same thing, and that it can result in account termination. The Community Guidelines say each account must be associated with a human, and “do not use self-bots or user-bots.”

The [Developer Policy](https://github.com/discord/discord-api-docs/blob/e5cd463cd1412df2e55fce8ecb81e7d1ed5755b0/docs/policies_and_agreements/Developer_Policy.md) (Help Center copy: [Discord Developer Policy](https://support-dev.discord.com/hc/en-us/articles/8563934450327-Discord-Developer-Policy)) adds:

- Do not obtain login credentials. That includes user access or login tokens.
- Do not modify a user’s account, or start a process on their behalf, without explicit permission on a clearly labeled consent screen.
- Do not mine or scrape Discord.
- Do not circumvent API rate limits.

A desktop session token is a login token. Replaying it against the authorize API is not the OAuth2 flow. OAuth2 is the human opening Discord’s authorize page.

## Where the first safety net was too loose

The first version still left three holes relative to those rules:

1. **The agent could still “be the bot.”** Blocking user tokens but allowing the agent to curl Discord with a bot token trains the wrong habit. The bot token belongs inside the running app. The agent does not send the request.
2. **`discord.com` was not the whole API.** The Gateway is `gateway.discord.gg`. A check that only looks for `discord.com` misses it. This hook also denies `discordapp.com`, `discord.media`, and `discordapp.net`.
3. **It did not say “do not build a self-bot.”** Stopping one request is not enough if the agent then writes a user-token client, scrapes the client, or evades rate limits. Those are in the rule and the skill now. Canary and PTB are included, because they are the same client.

## Install

See [INSTALL.md](INSTALL.md). Short version:

1. Copy `hooks/block-discord-requests.py` to `~/.cursor/hooks/`.
2. Merge [hooks.fragment.json](hooks.fragment.json) into `~/.cursor/hooks.json` with `"failClosed": true`.
3. Copy `rules/discord-no-user-automation.mdc` to `~/.cursor/rules/`.
4. Copy `.cursor/skills/dont-get-banned-by-discord/` to `~/.cursor/skills/`.

The hook fails closed. If it crashes, the action is blocked. Do not add a bypass.

Your own program may still use a bot token in-process, on documented routes, inside published rate limits. You still click Authorize yourself.

The skill is also the build-and-test guide. Agents write tests against documented fixtures and a mocked HTTP boundary. They do not “test” by calling Discord. A live check is a short list you run yourself on a private test server. See `.cursor/skills/dont-get-banned-by-discord/SKILL.md`.

## Check

```bash
python3 scripts/self-test.py
```

## Post this

> My coding agent got my Discord account suspended. It attached a debugger to the desktop app, copied my logged-in session, and called Discord’s authorize API as me. I never clicked Authorize. The suspension was lifted. The account is still at risk. Discord treats that as automating a user account, which is outside the bot API and OAuth2. I published a fail-closed Cursor hook that blocks the agent from sending any request to Discord, including the Gateway on discord.gg, plus a skill for how to build and test a Discord app without the agent ever calling Discord. Ask me anything.
>
> https://github.com/REPLACE_ME/dont-get-banned-by-discord

## Sources

- [OAuth2 — Bot vs User Accounts](https://github.com/discord/discord-api-docs/blob/main/developers/topics/oauth2.mdx)
- [Automated User Accounts (Self-Bots)](https://support.discord.com/hc/en-us/articles/115002192352-Automated-User-Accounts-Self-Bots)
- [Discord Developer Policy](https://support-dev.discord.com/hc/en-us/articles/8563934450327-Discord-Developer-Policy)
- [Community Guidelines](https://discord.com/guidelines) (self-bots / user-bots)
