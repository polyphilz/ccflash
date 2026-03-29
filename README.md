<div align="center">

<img src="assets/clawd-shimmer.gif" width="200" alt="Clawd">
<h1>ccflash</h1>

A Claude Code skill that turns any conversation into Anki flashcards.
Claude analyzes what you discussed, generates simple fill-in-the-blank cards, lets you review and edit them, then uploads directly to Anki.

<a href="https://apps.ankiweb.net/" target="_blank"><img src="https://img.shields.io/badge/Anki-236bc5?style=flat&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCI+PHRleHQgeT0iMjAiIGZvbnQtc2l6ZT0iMjAiPvCfk6Y8L3RleHQ+PC9zdmc+&logoColor=white" alt="Anki"></a>
<a href="https://www.python.org/" target="_blank"><img src="https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white" alt="Python"></a>
<a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="License: MIT"></a>

<br>

![demo](assets/ccflash-demo.gif)

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
| `/flash` | Generate cards at light density (default) |
| `/flash M` | Medium density (~15-40 cards) |
| `/flash H` | Heavy density (40+ cards) |
| `/flash --deck "My Deck"` | Target a specific deck |
| `/flash M --deck "My Deck"` | Combine density + deck |
| `/flash --set-default-deck "My Deck"` | Save a default deck for future use |

Density levels: `light`/`L` (~5-15 cards, default), `medium`/`M` (~15-40), `heavy`/`H` (40+).

### Card review

Claude presents all cards in a numbered table. You can:
- Say **"upload"** or **"looks good"** to upload all cards
- Say **"delete 3, 7, 12"** to remove specific cards
- Say **"edit 4 front to ..."** to modify a card

Nothing is uploaded until you explicitly confirm.

### Example cards

| Front | Back |
|-------|------|
| The Anki plugin that exposes a REST API on localhost is called ___ | AnkiConnect |
| AnkiConnect listens on port ___ | 8765 |
| In Claude Code, MCP servers are configured in the ___ file | .mcp.json |

## Card methodology

Card design draws from several foundational works on spaced repetition and memory:

<details>
<summary><strong>Atomicity</strong> — each card tests exactly one idea (<a href="https://augmentingcognition.com/ltm.html">Nielsen</a>, <a href="https://super-memory.com/articles/20rules.htm">Wozniak</a>)</summary>
<br>

If a question has two parts, it becomes two cards. Nielsen demonstrated that breaking compound questions into atomic pieces turns cards you routinely get wrong into cards you routinely get right. This is Wozniak's "minimum information principle" — the most important rule in his [20 Rules of Formulating Knowledge](https://super-memory.com/articles/20rules.htm).
</details>

<details>
<summary><strong>Fill-in-the-blank over other formats</strong> — cloze deletion triggers the generation effect (<a href="https://gwern.net/spaced-repetition">Gwern</a>)</summary>
<br>

Fronts are a sentence with a blank (`___`), backs are a single word or short phrase. Producing an answer creates stronger memory than recognizing one. Multiple choice is actively avoided because seeing wrong answers creates "negative suggestion effects" that make false information more memorable.
</details>

<details>
<summary><strong>Precision</strong> — every blank has exactly one defensible answer (<a href="https://controlaltbackspace.org/precise/">Bjornstad</a>)</summary>
<br>

Bjornstad frames imprecise cards as an [overfitting](https://en.wikipedia.org/wiki/Overfitting) problem: if the blank is ambiguous, you end up memorizing the sentence pattern rather than the underlying concept. Since ccflash generates cards from conversation text (rather than hand-crafting them), this risk is elevated — the skill adds context to disambiguate wherever multiple answers could fit.
</details>

<details>
<summary><strong>No orphan cards</strong> — clusters of 2-3+ cards per concept (<a href="https://augmentingcognition.com/ltm.html">Nielsen</a>)</summary>
<br>

A single isolated card about a topic decays quickly. Cards are generated in clusters of 2-3+ per concept. If a concept isn't worth multiple cards, it's skipped entirely.
</details>

<details>
<summary><strong>Insight caching</strong> — card your deductions, not just stated facts (<a href="https://borretti.me/article/effective-spaced-repetition">Borretti</a>)</summary>
<br>

Cards aren't limited to facts explicitly stated in conversation. Borretti's "insight caching" principle: the deductions and connections you arrive at while learning are often more valuable than the raw facts. The skill also generates cards for insights that emerged during discussion.
</details>

<details>
<summary><strong>Concrete over abstract</strong> — spacing effect weakens with conceptual difficulty (<a href="https://gwern.net/spaced-repetition">Gwern</a>)</summary>
<br>

Cards stay factual and concrete. The spacing effect [weakens sharply](https://gwern.net/spaced-repetition#complexity) with high conceptual difficulty — abstract reasoning questions don't benefit from spaced repetition the way factual recall does.
</details>

<details>
<summary><strong>Additional rules</strong></summary>
<br>

- **No yes/no questions** — these are a "question smell" (Nielsen). Refactored into specific fill-in-the-blank.
- **Claims, not facts** — when something discussed was uncertain or debatable, cards frame it as "According to X, the approach is ___" rather than stating it as settled fact.
- **No multiple choice** — never used. Seeing wrong options creates false memories (Gwern).
</details>

## How it works

1. `/flash` triggers a Claude Code [skill](https://docs.anthropic.com/en/docs/claude-code/skills) that prompts Claude to analyze the conversation
2. Claude generates flashcards and presents them in a numbered table for review
3. You edit or delete cards conversationally, then confirm upload
4. A Python script uploads approved cards to Anki via [AnkiConnect's](https://foosoft.net/projects/anki-connect/) REST API on `localhost:8765`

Anki must be running with AnkiConnect installed — the skill checks this before generating cards and warns you if it's not reachable.

## License

MIT
