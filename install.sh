#!/bin/bash
# Install ccflash — Anki flashcard skill for Claude Code
#
# Remote install (download files):
#   curl -fsSL https://raw.githubusercontent.com/polyphilz/ccflash/main/install.sh | bash
#
# Local dev install (clone + symlink):
#   git clone https://github.com/polyphilz/ccflash.git ~/projects/ccflash
#   cd ~/projects/ccflash && ./install.sh
#
# Requires: Anki running with AnkiConnect add-on (code 2055492159)

set -euo pipefail

GITHUB_REPO="polyphilz/ccflash"
REPO_RAW="https://raw.githubusercontent.com/${GITHUB_REPO}/main"
SKILLS_DIR="$HOME/.claude/skills"
SCRIPTS_DIR="$HOME/.claude/scripts"

is_local_clone() {
    # Check if the script is running from a local clone (not piped)
    local script_dir
    script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd)" || return 1
    [ -f "$script_dir/skill/SKILL.md" ] && [ -f "$script_dir/scripts/flash_review.py" ]
}

echo "Installing ccflash..."

# Create target directories
mkdir -p "$SKILLS_DIR/flash" "$SCRIPTS_DIR"

# Remove existing flash skill/script if present
if [ -e "$SKILLS_DIR/flash" ] || [ -L "$SKILLS_DIR/flash" ]; then
    rm -rf "$SKILLS_DIR/flash"
    echo "  Removed existing ~/.claude/skills/flash"
fi
if [ -e "$SCRIPTS_DIR/flash_review.py" ] || [ -L "$SCRIPTS_DIR/flash_review.py" ]; then
    rm -f "$SCRIPTS_DIR/flash_review.py"
    echo "  Removed existing ~/.claude/scripts/flash_review.py"
fi

if is_local_clone; then
    # --- Local dev: symlink ---
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

    ln -s "$SCRIPT_DIR/skill" "$SKILLS_DIR/flash"
    echo "  Linked skill -> $SKILLS_DIR/flash"

    ln -s "$SCRIPT_DIR/scripts/flash_review.py" "$SCRIPTS_DIR/flash_review.py"
    echo "  Linked script -> $SCRIPTS_DIR/flash_review.py"
else
    # --- Remote: download files ---
    mkdir -p "$SKILLS_DIR/flash"
    curl -fsSL "$REPO_RAW/skill/SKILL.md" -o "$SKILLS_DIR/flash/SKILL.md"
    echo "  Downloaded SKILL.md -> $SKILLS_DIR/flash/SKILL.md"

    curl -fsSL "$REPO_RAW/scripts/flash_review.py" -o "$SCRIPTS_DIR/flash_review.py"
    chmod +x "$SCRIPTS_DIR/flash_review.py"
    echo "  Downloaded flash_review.py -> $SCRIPTS_DIR/flash_review.py"
fi

# Check AnkiConnect reachability
if curl -s -o /dev/null -w '%{http_code}' http://localhost:8765 2>/dev/null | grep -q 200; then
    echo "  AnkiConnect is reachable on localhost:8765"
else
    echo ""
    echo "  NOTE: AnkiConnect not reachable on localhost:8765."
    echo "  Make sure Anki is running with the AnkiConnect add-on installed."
    echo "  Install it in Anki: Tools > Add-ons > Get Add-ons > code 2055492159"
fi

echo ""
echo "Done! Restart Claude Code, then use /flash in any conversation."
