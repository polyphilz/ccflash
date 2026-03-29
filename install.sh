#!/bin/bash
# Install ccflash — Anki flashcard skill for Claude Code
#
# For local development (clone + symlink):
#   git clone https://github.com/polyphilz/ccflash.git ~/projects/ccflash
#   cd ~/projects/ccflash && ./install.sh
#
# Requires: Anki running with AnkiConnect add-on (code 2055492159)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILLS_DIR="$HOME/.claude/skills"
SCRIPTS_DIR="$HOME/.claude/scripts"

echo "Installing ccflash..."

# Create target directories
mkdir -p "$SKILLS_DIR" "$SCRIPTS_DIR"

# Remove existing flash skill/script if present
if [ -e "$SKILLS_DIR/flash" ] || [ -L "$SKILLS_DIR/flash" ]; then
    rm -rf "$SKILLS_DIR/flash"
    echo "  Removed existing ~/.claude/skills/flash"
fi
if [ -e "$SCRIPTS_DIR/flash_review.py" ] || [ -L "$SCRIPTS_DIR/flash_review.py" ]; then
    rm -f "$SCRIPTS_DIR/flash_review.py"
    echo "  Removed existing ~/.claude/scripts/flash_review.py"
fi

# Symlink skill directory and review script
ln -s "$SCRIPT_DIR/skill" "$SKILLS_DIR/flash"
echo "  Linked skill -> $SKILLS_DIR/flash"

ln -s "$SCRIPT_DIR/scripts/flash_review.py" "$SCRIPTS_DIR/flash_review.py"
echo "  Linked script -> $SCRIPTS_DIR/flash_review.py"

# Check AnkiConnect reachability
if curl -s -o /dev/null -w '%{http_code}' http://localhost:8765 2>/dev/null | grep -q 200; then
    echo "  AnkiConnect is reachable on localhost:8765"
else
    echo ""
    echo "  WARNING: AnkiConnect not reachable on localhost:8765."
    echo "  Make sure Anki is running with the AnkiConnect add-on installed."
    echo "  Install it in Anki: Tools > Add-ons > Get Add-ons > code 2055492159"
fi

echo ""
echo "Done! Restart Claude Code, then use /flash in any conversation."
