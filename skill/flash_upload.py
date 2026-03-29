#!/usr/bin/env python3
"""Upload flashcards to Anki via AnkiConnect."""

import json
import sys
import urllib.request


def upload_cards(cards_path: str, deck: str) -> None:
    with open(cards_path) as f:
        cards = json.load(f)

    if not cards:
        print("No cards to upload.")
        sys.exit(1)

    ok = 0
    failed = []
    for card in cards:
        payload = json.dumps({
            "action": "addNote",
            "version": 6,
            "params": {
                "note": {
                    "deckName": deck,
                    "modelName": "Basic",
                    "fields": {
                        "Front": card["front"],
                        "Back": card["back"],
                    },
                }
            },
        })
        req = urllib.request.Request(
            "http://localhost:8765",
            data=payload.encode(),
            headers={"Content-Type": "application/json"},
        )
        try:
            resp = json.loads(urllib.request.urlopen(req).read())
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
