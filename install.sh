#!/usr/bin/env bash
set -euo pipefail

REPO_URL="https://github.com/inzexg-coder/ameni-vs-kernel"
INSTALL_DIR="${AMENI_HOME:-$HOME/.local/share/ameni-vs-kernel}"
BIN_DIR="$HOME/.local/bin"
AMENI_LINK="$BIN_DIR/ameni"

PURPLE='\033[38;5;141m'
TEAL='\033[38;5;92m'
LAVENDER='\033[38;5;147m'
RESET='\033[0m'

echo -e "\n  ${PURPLE}━━ ameni vs kernel — installer ━━${RESET}\n"

if [ -d "$INSTALL_DIR/.git" ]; then
    echo -e "  ${TEAL}◈ Updating existing installation...${RESET}"
    cd "$INSTALL_DIR"
    git pull --ff-only 2>/dev/null || echo -e "  ${LAVENDER}◈ Already up to date${RESET}"
else
    echo -e "  ${TEAL}◈ Cloning to ${INSTALL_DIR}...${RESET}"
    git clone --depth=1 "$REPO_URL" "$INSTALL_DIR"
fi

mkdir -p "$BIN_DIR"
ln -sf "$INSTALL_DIR/.ameni/bin/ameni" "$AMENI_LINK"
chmod +x "$INSTALL_DIR/.ameni/bin/ameni"

echo -e "  ${TEAL}◈ Installed: ${AMENI_LINK}${RESET}"

if ! echo ":$PATH:" | grep -q ":$BIN_DIR:"; then
    echo ""
    echo -e "  ${PURPLE}⚠ ${BIN_DIR} is not in PATH${RESET}"
    echo -e "  ${LAVENDER}Add this to your ~/.bashrc or ~/.zshrc:${RESET}"
    echo ""
    echo -e "  ${TEAL}export PATH=\"\$HOME/.local/bin:\$PATH\"${RESET}"
    echo ""
fi

echo -e "  ${PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}\n"
echo -e "  ${TEAL}Run:${RESET}  ameni monitor"
echo -e "  ${TEAL}Help:${RESET} ameni help"
echo ""
