#!/usr/bin/env python3
"""Interactive flashcard review TUI for Claude Code /flash skill."""

import json
import sys
import os
import readline  # noqa: F401 — enables input() line editing


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def print_divider():
    try:
        cols = os.get_terminal_size().columns
    except OSError:
        cols = 80
    print("\033[90m" + "─" * cols + "\033[0m")


def review_cards(cards: list[dict]) -> list[dict]:
    reviewed = []
    total = len(cards)
    i = 0

    while i < total:
        card = cards[i]
        clear()
        print(f"\033[1mCard {i + 1} / {total}\033[0m")
        print_divider()
        print(f"\033[1mFront:\033[0m {card['front']}")
        print(f"\033[1mBack:\033[0m  {card['back']}")
        print_divider()
        print(
            "\033[36m[enter]\033[0m keep  "
            "\033[33m[e]\033[0m edit  "
            "\033[31m[d]\033[0m delete  "
            "\033[90m[q]\033[0m quit"
        )

        choice = input("> ").strip().lower()

        if choice in ("", "k"):
            reviewed.append(card)
            i += 1
        elif choice == "e":
            print()
            new_front = input(f"  Front [{card['front']}]: ").strip()
            new_back = input(f"  Back  [{card['back']}]: ").strip()
            card["front"] = new_front if new_front else card["front"]
            card["back"] = new_back if new_back else card["back"]
            reviewed.append(card)
            i += 1
        elif choice == "d":
            print(f"\033[31m  Deleted.\033[0m")
            i += 1
        elif choice == "q":
            print("\nAborted. No cards will be uploaded.")
            sys.exit(1)
        else:
            continue  # unrecognized, redraw

    # Summary
    clear()
    print(f"\033[1mReview complete: {len(reviewed)} / {total} cards kept.\033[0m")
    print_divider()
    for j, c in enumerate(reviewed, 1):
        print(f"  {j}. {c['front']}")
        print(f"     \033[90m-> {c['back']}\033[0m")
    print_divider()

    if not reviewed:
        print("No cards to upload.")
        sys.exit(1)

    confirm = input(f"\nUpload {len(reviewed)} cards? [y/n]: ").strip().lower()
    if confirm != "y":
        print("Cancelled.")
        sys.exit(1)

    return reviewed


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <input.json> <output.json>", file=sys.stderr)
        sys.exit(2)

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    with open(input_path) as f:
        cards = json.load(f)

    if not cards:
        print("No cards to review.")
        sys.exit(1)

    reviewed = review_cards(cards)

    with open(output_path, "w") as f:
        json.dump(reviewed, f, indent=2)

    print(f"\n\033[32m{len(reviewed)} cards ready for upload.\033[0m")


if __name__ == "__main__":
    main()
