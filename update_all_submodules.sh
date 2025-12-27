#!/bin/bash
#
# Manually update all submodules to their latest commits
#

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}Updating all submodules to latest commits...${NC}\n"

# Get current branch
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
echo "Current branch: $CURRENT_BRANCH"

# Update all submodules
echo -e "\n${YELLOW}Fetching latest changes...${NC}"
git submodule update --remote --merge

# Check if there are changes
if git diff --quiet; then
    echo -e "\n${GREEN}All submodules are already up to date!${NC}"
    exit 0
fi

# Show changes
echo -e "\n${YELLOW}Changes:${NC}"
git status --short

# Ask for confirmation
read -p "Commit and push these changes? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 1
fi

# Stage changes
git add .

# Create commit
TIMESTAMP=$(date -u +"%Y-%m-%d %H:%M:%S UTC")
git commit -m "Update all submodules

Updated at: $TIMESTAMP
Automated update via update_all_submodules.sh"

# Push
echo -e "\n${YELLOW}Pushing to origin/$CURRENT_BRANCH...${NC}"
git push -u origin "$CURRENT_BRANCH"

echo -e "\n${GREEN}All submodules updated successfully!${NC}"
