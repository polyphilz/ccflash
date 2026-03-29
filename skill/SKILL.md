---
name: flash
description: Generate Anki flashcards from the current conversation. Analyzes what was learned and creates simple single-principle cards, lets the user review/edit/delete them interactively, then uploads to Anki via AnkiConnect.
allowed-tools: Bash, Read, Write
user-invocable: true
argument-hint: "[--deck <deck_name>] [--set-default-deck <deck_name>] [light|medium|heavy]"
---

# /flash — Anki flashcard generator

You are creating Anki flashcards from the current conversation.

## Arguments

- `--deck <name>` — target Anki deck (overrides default)
- `--set-default-deck <name>` — save a default deck to `~/.claude/flash_config.json` and exit
- `light` / `L` — only the most essential concepts, ~5-15 cards (default)
- `medium` / `M` — solid coverage, ~15-40 cards
- `heavy` / `H` — comprehensive, card everything discussed, 40+ cards

## Step 1: Check AnkiConnect is reachable

Run:
```bash
curl -s -o /dev/null -w '%{http_code}' http://localhost:8765
```

If the result is NOT `200`, stop and tell the user:
> Anki doesn't appear to be running (nothing on localhost:8765). Please open Anki with the AnkiConnect add-on installed (code 2055492159), then try /flash again.

Do NOT proceed with card generation if AnkiConnect is unreachable.

## Step 2: Handle `--set-default-deck`

If the user passed `--set-default-deck <name>`, write `{"default_deck": "<name>"}` to `~/.claude/flash_config.json` and confirm. Done — do not generate cards.

## Step 3: Determine the target deck

Priority order:
1. `--deck` argument
2. `default_deck` from `~/.claude/flash_config.json` (if it exists)
3. If neither, ask the user which deck to use. Also ask if they'd like to save it as the default.

## Step 4: Generate flashcards

Determine the density level from the arguments. Accept `light`, `L`, `medium`, `M`, `heavy`, or `H` (case-insensitive). **Default is light.**

| Level | Target | What to card |
|-------|--------|--------------|
| light | ~5-15 cards | Only the most important takeaways — things you'd be embarrassed to forget |
| medium | ~15-40 cards | Solid coverage of all major concepts, skip minor details |
| heavy | 40+ cards | Comprehensive — card everything discussed, including details and edge cases |

Analyze the **full conversation** above this /flash invocation. Identify concepts, facts, terms, commands, APIs, patterns, or techniques that were discussed or learned, filtered by the density level above.

**Card style — keep it simple:**
- The **back** should almost always be a **single word or very short phrase** (1–4 words max).
- The **front** should be a sentence or question with a blank (`___`) where the answer goes.
- Each card tests exactly ONE thing (atomic). If a question has two parts, split it into two cards.
- Prefer fill-in-the-blank over open-ended questions. **Never** use multiple choice — seeing wrong answers creates false memories.
- **Never** use yes/no questions — they are a "question smell." Refactor into a specific fill-in-the-blank.
- Keep cards concrete and factual. Don't try to test abstract reasoning or complex conceptual understanding — the spacing effect weakens sharply with high conceptual difficulty.
- Cover breadth: make cards for all distinct concepts, not just the main topic.
- **No orphan cards**: create clusters of 2–3+ related cards per concept. A single isolated card about a topic decays quickly. If a concept isn't worth 2+ cards, skip it.
- If something discussed was uncertain or debatable, frame it as a claim: "According to X, the recommended approach is ___" rather than stating it as fact.

**Precision — one defensible answer per blank:**
Every blank must have exactly ONE correct answer. If multiple words could fit, the card is imprecise and will train you to memorize the sentence pattern rather than the concept (Bjornstad's "overfitting" problem). Fix by adding context to disambiguate.

| BAD (ambiguous) | GOOD (precise) |
|---|---|
| Claude Code skills are defined in a ___ file | Claude Code skills are defined in a file named ___ (SKILL.md) |
| The Articles of Confederation had no power to regulate ___ | The Articles of Confederation's lack of power to regulate ___ between states was a key weakness (commerce) |

**Cache your insights:**
Don't just card facts that were explicitly stated — also card deductions and connections that emerged during the conversation. The insight you arrived at is often more valuable than the raw fact.

**Examples of good cards:**
| Front | Back |
|---|---|
| The Anki plugin that exposes a REST API on localhost is called ___ | AnkiConnect |
| AnkiConnect listens on port ___ | 8765 |
| The AnkiConnect add-on code for Anki's add-on installer is ___ | 2055492159 |
| `uv tool install` installs a Python CLI tool into an isolated ___ | environment |
| Using direct curl to AnkiConnect instead of an MCP server avoids ___ bloat | context |

**Examples of BAD cards (don't do this):**
- Back is a full sentence or paragraph
- Front asks "Explain how X works" (too vague)
- Card tests multiple things at once
- Yes/no question like "Is AnkiConnect a REST API?" (refactor to fill-in-the-blank)
- A single orphan card about a topic with no related cards
- Ambiguous blank where multiple answers fit — add more context

Respect the density level — be selective at `light`, thorough at `heavy`.

## Step 5: Conversational review

Present all cards in a numbered table so the user can see them at a glance. Then ask the user to review — they can:
- Say "upload" or "looks good" to upload all cards
- Say "delete 3, 7, 12" to remove specific cards
- Say "edit 4 front to ..." or "edit 4 back to ..." to modify a card
- Make multiple edits before uploading

Wait for the user's explicit confirmation before uploading. Do NOT upload without approval.

## Step 6: Upload to Anki

Once the user approves, write the final cards as JSON to `/tmp/flash_cards_<SUFFIX>.json` (use `SUFFIX=$(date +%s)_$$` for uniqueness):

```json
[{"front": "...", "back": "..."}, ...]
```

Then upload via the upload script:

```bash
python3 ${CLAUDE_SKILL_DIR}/flash_upload.py /tmp/flash_cards_<SUFFIX>.json "DECK_NAME"
```

Report the result to the user: how many cards were added and to which deck.

### Code in cards

Anki renders HTML. When card text contains inline code (commands, function names, etc.), wrap it in `<code>` tags instead of backticks. For example:

- Front: `The command <code>uv tool install</code> installs a CLI into an isolated ___`
- Back: `environment`
