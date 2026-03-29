---
name: flash
description: Generate Anki flashcards from the current conversation. Analyzes what was learned and creates simple fill-in-the-blank cards, lets the user review/edit/delete them interactively, then uploads to Anki via AnkiConnect.
allowed-tools: Bash, Read, Write
user-invocable: true
argument-hint: "[--deck <deck_name>] [--set-default-deck <deck_name>]"
---

# /flash — Anki flashcard generator

You are creating Anki flashcards from the current conversation.

## Arguments

- `--deck <name>` — target Anki deck (overrides default)
- `--set-default-deck <name>` — save a default deck to `~/.claude/flash_config.json` and exit

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

Analyze the **full conversation** above this /flash invocation. Identify every distinct concept, fact, term, command, API, pattern, or technique that was discussed or learned.

**Card style — keep it simple:**
- The **back** should almost always be a **single word or very short phrase** (1–4 words max).
- The **front** should be a sentence or question with a blank (`___`) where the answer goes.
- Each card tests exactly ONE thing (atomic). If a question has two parts, split it into two cards.
- Prefer fill-in-the-blank over open-ended questions.
- **Never** use yes/no questions — they are a "question smell." Refactor into a specific fill-in-the-blank.
- Cover breadth: make cards for all distinct concepts, not just the main topic.
- **No orphan cards**: create clusters of 2–3+ related cards per concept. A single isolated card about a topic decays quickly. If a concept isn't worth 2+ cards, skip it.
- If something discussed was uncertain or debatable, frame it as a claim: "According to X, the recommended approach is ___" rather than stating it as fact.

**Examples of good cards:**
| Front | Back |
|---|---|
| The Anki plugin that exposes a REST API on localhost is called ___ | AnkiConnect |
| AnkiConnect listens on port ___ | 8765 |
| The AnkiConnect add-on code for Anki's add-on installer is ___ | 2055492159 |
| `uv tool install` installs a Python CLI tool into an isolated ___ | environment |

**Examples of BAD cards (don't do this):**
- Back is a full sentence or paragraph
- Front asks "Explain how X works" (too vague)
- Card tests multiple things at once
- Yes/no question like "Is AnkiConnect a REST API?" (refactor to fill-in-the-blank)
- A single orphan card about a topic with no related cards

Use your judgment on card count — cover everything that was discussed.

## Step 5: Interactive review

1. Generate a unique suffix for this run: `SUFFIX=$(date +%s)_$$`
2. Write the cards as JSON to `/tmp/flash_cards_input_${SUFFIX}.json`:
   ```json
   [{"front": "...", "back": "..."}, ...]
   ```
3. Run the review script:
   ```bash
   python3 ${CLAUDE_SKILL_DIR}/flash_review.py /tmp/flash_cards_input_${SUFFIX}.json /tmp/flash_cards_reviewed_${SUFFIX}.json
   ```
   This is an **interactive terminal UI** — the user will review each card, edit or delete as needed, and confirm upload. Let it run without timeout constraints.
4. Read `/tmp/flash_cards_reviewed_${SUFFIX}.json` for the final set.

## Step 6: Upload to Anki

Write a short inline Python script that reads the reviewed JSON file and uploads each card via AnkiConnect. This avoids shell escaping issues with backticks, quotes, and special characters in card text.

```bash
python3 -c "
import json, urllib.request, sys

deck = 'DECK_NAME'
with open('REVIEWED_JSON_PATH') as f:
    cards = json.load(f)

ok = 0
for card in cards:
    payload = json.dumps({'action': 'addNote', 'version': 6, 'params': {'note': {'deckName': deck, 'modelName': 'Basic', 'fields': {'Front': card['front'], 'Back': card['back']}}}})
    req = urllib.request.Request('http://localhost:8765', data=payload.encode(), headers={'Content-Type': 'application/json'})
    resp = json.loads(urllib.request.urlopen(req).read())
    if resp.get('error'):
        print(f'FAILED: {card[\"front\"][:50]}... — {resp[\"error\"]}', file=sys.stderr)
    else:
        ok += 1
print(f'{ok}/{len(cards)} cards added to {deck}')
"
```

Replace `DECK_NAME` and `REVIEWED_JSON_PATH` with the actual values.

Report the result to the user: how many cards were added and to which deck.

### Code in cards

Anki renders HTML. When card text contains inline code (commands, function names, etc.), wrap it in `<code>` tags instead of backticks. For example:

- Front: `The command <code>uv tool install</code> installs a CLI into an isolated ___`
- Back: `environment`
