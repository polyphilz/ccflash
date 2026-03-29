#!/usr/bin/env python3
"""Upload flashcards to Anki via AnkiConnect."""

import json
import sys
import urllib.request

ANKI_URL = "http://localhost:8765"


def anki_request(action: str, **params) -> dict:
    payload = json.dumps({"action": action, "version": 6, "params": params})
    req = urllib.request.Request(
        ANKI_URL,
        data=payload.encode(),
        headers={"Content-Type": "application/json"},
    )
    return json.loads(urllib.request.urlopen(req).read())


def find_basic_model() -> str:
    """Find a note type with Front and Back fields."""
    resp = anki_request("modelNames")
    models = resp.get("result", [])

    def is_reversed(name: str) -> bool:
        return "reversed" in name.lower()

    # Find models with Front and Back fields, preferring:
    # 1. Exact "Basic" (case-insensitive)
    # 2. Non-reversed Basic variant
    # 3. Any non-reversed model with Front/Back
    # 4. Last resort: reversed model with Front/Back
    candidates = []
    for m in models:
        fields_resp = anki_request("modelFieldNames", modelName=m)
        fields = fields_resp.get("result", [])
        if "Front" in fields and "Back" in fields:
            candidates.append(m)

    for c in candidates:
        if c.lower() == "basic":
            return c
    for c in candidates:
        if c.lower().startswith("basic") and not is_reversed(c):
            return c
    for c in candidates:
        if not is_reversed(c):
            return c
    if candidates:
        return candidates[0]

    print("Error: No note type with Front/Back fields found.", file=sys.stderr)
    print(f"Available models: {models}", file=sys.stderr)
    sys.exit(1)


def upload_cards(cards_path: str, deck: str) -> None:
    with open(cards_path) as f:
        cards = json.load(f)

    if not cards:
        print("No cards to upload.")
        sys.exit(1)

    model = find_basic_model()
    print(f"Using note type: {model}")

    ok = 0
    failed = []
    for card in cards:
        try:
            resp = anki_request(
                "addNote",
                note={
                    "deckName": deck,
                    "modelName": model,
                    "fields": {
                        "Front": card["front"],
                        "Back": card["back"],
                    },
                },
            )
            if resp.get("error"):
                failed.append((card["front"][:60], resp["error"]))
            else:
                ok += 1
        except Exception as e:
            failed.append((card["front"][:60], str(e)))

    print(f"{ok}/{len(cards)} cards added to {deck}")
    for front, err in failed:
        print(f"  FAILED: {front}... — {err}", file=sys.stderr)

    sys.exit(0 if not failed else 1)


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <cards.json> <deck_name>", file=sys.stderr)
        sys.exit(2)

    upload_cards(sys.argv[1], sys.argv[2])


if __name__ == "__main__":
    main()
