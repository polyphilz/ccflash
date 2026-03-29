<div align="center">

<img src="assets/clawd-shimmer.gif" width="200" alt="Clawd">
<h1>ccflash</h1>

A Claude Code skill that turns any conversation into Anki flashcards.
Claude analyzes what you discussed, generates simple fill-in-the-blank cards, lets you review and edit them, then uploads directly to Anki.

<a href="https://apps.ankiweb.net/" target="_blank"><img src="https://img.shields.io/badge/Anki-236bc5?style=flat&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCI+PHRleHQgeT0iMjAiIGZvbnQtc2l6ZT0iMjAiPvCfk6Y8L3RleHQ+PC9zdmc+&logoColor=white" alt="Anki"></a>
<a href="https://www.python.org/" target="_blank"><img src="https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white" alt="Python"></a>
<a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="License: MIT"></a>

</div>

## Features

- **Auto-generates cards** — Claude reads the full conversation and extracts every concept worth remembering
- **Simple card style** — fill-in-the-blank fronts with single-word backs, optimized for recall
- **Interactive review** — step through each card, edit the front/back, or delete cards you don't want
- **Direct upload** — cards go straight to Anki via AnkiConnect, no export files to manage
- **Deck selection** — target any deck with `--deck`, or set a default so you're never asked

## Prerequisites

- [Anki](https://apps.ankiweb.net/) desktop app
- [AnkiConnect](https://ankiweb.net/shared/info/2055492159) add-on — install in Anki: Tools > Add-ons > Get Add-ons > code `2055492159`
- [Claude Code](https://docs.anthropic.com/en/docs/claude-code)

## Quick Start

```bash
curl -fsSL https://raw.githubusercontent.com/polyphilz/ccflash/main/install.sh | bash
```

This downloads the skill into `~/.claude/skills/flash/`. Restart Claude Code to pick up the new skill.

### Local development

If you want to hack on ccflash, clone and install with symlinks instead:

```bash
git clone https://github.com/polyphilz/ccflash.git ~/projects/ccflash
cd ~/projects/ccflash && ./install.sh
```

The install script detects the local clone and symlinks rather than downloading:

```
~/.claude/skills/flash -> ~/projects/ccflash/skill
```

## Usage

After any conversation where you learned something:

```
/flash
```

Claude will analyze the conversation, generate flashcards, and walk you through an interactive review before uploading.

### Options

| Command | Description |
|---------|-------------|
| `/flash` | Generate cards, ask which deck to use |
| `/flash --deck "My Deck"` | Target a specific deck |
| `/flash --set-default-deck "My Deck"` | Save a default deck for future use |

### Card review controls

| Key | Action |
|-----|--------|
| `Enter` | Keep the card |
| `e` | Edit front and/or back |
| `d` | Delete the card |
| `q` | Quit without uploading |

After reviewing all cards, you'll see a summary and a final confirmation before anything is uploaded.

### Example cards

| Front | Back |
|-------|------|
| The Anki plugin that exposes a REST API on localhost is called ___ | AnkiConnect |
| AnkiConnect listens on port ___ | 8765 |
| In Claude Code, MCP servers are configured in the ___ file | .mcp.json |

## How it works

1. `/flash` triggers a Claude Code [skill](https://docs.anthropic.com/en/docs/claude-code/skills) that prompts Claude to analyze the conversation
2. Claude generates flashcards as JSON and writes them to a temp file
3. A Python script presents an interactive terminal UI for reviewing, editing, and deleting cards
4. Approved cards are uploaded to Anki via [AnkiConnect's](https://foosoft.net/projects/anki-connect/) REST API on `localhost:8765`

Anki must be running with AnkiConnect installed — the skill checks this before generating cards and warns you if it's not reachable.

## License

MIT
