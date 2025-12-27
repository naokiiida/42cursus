#!/bin/bash
#
# Setup GitHub webhooks for all submodule repositories
# Requires: GitHub CLI (gh) to be installed and authenticated
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if gh is installed
if ! command -v gh &> /dev/null; then
    echo -e "${RED}Error: GitHub CLI (gh) is not installed${NC}"
    echo "Install it from: https://cli.github.com/"
    exit 1
fi

# Check if authenticated
if ! gh auth status &> /dev/null; then
    echo -e "${RED}Error: Not authenticated with GitHub CLI${NC}"
    echo "Run: gh auth login"
    exit 1
fi

# Get webhook URL
read -p "Enter your webhook URL (e.g., https://your-server.com/webhook): " WEBHOOK_URL

if [ -z "$WEBHOOK_URL" ]; then
    echo -e "${RED}Error: Webhook URL is required${NC}"
    exit 1
fi

# Get webhook secret
read -sp "Enter your webhook secret: " WEBHOOK_SECRET
echo

if [ -z "$WEBHOOK_SECRET" ]; then
    echo -e "${RED}Error: Webhook secret is required${NC}"
    exit 1
fi

# List of repositories (owner/repo format)
REPOS=(
    "naokiiida/libft"
    "naokiiida/get_next_line"
    "naokiiida/ft_printf"
    "naokiiida/born2beroot"
    "naokiiida/push_swap"
    "naokiiida/minitalk"
    "naokiiida/fractol"
    "naokiiida/pipex"
    "naokiiida/minishell"
    "naokiiida/philosophers"
    "naokiiida/cub3d"
    "Shunpei0902/ft_irc"
    "naokiiida/inception"
    "naokiiida/cpp00"
    "naokiiida/cpp01"
    "naokiiida/cpp02"
    "naokiiida/cpp03"
    "naokiiida/cpp04"
    "naokiiida/cpp05"
    "naokiiida/cpp06"
)

echo -e "\n${YELLOW}Setting up webhooks for ${#REPOS[@]} repositories...${NC}\n"

SUCCESS_COUNT=0
FAIL_COUNT=0
SKIPPED_COUNT=0

for repo in "${REPOS[@]}"; do
    echo -n "Setting up webhook for $repo... "

    # Check if user has access to the repository
    if ! gh repo view "$repo" &> /dev/null; then
        echo -e "${YELLOW}SKIPPED (no access)${NC}"
        ((SKIPPED_COUNT++))
        continue
    fi

    # Create webhook using gh API
    response=$(gh api \
        --method POST \
        -H "Accept: application/vnd.github+json" \
        "/repos/$repo/hooks" \
        -f name='web' \
        -f "config[url]=$WEBHOOK_URL" \
        -f "config[content_type]=json" \
        -f "config[secret]=$WEBHOOK_SECRET" \
        -f "config[insecure_ssl]=0" \
        -F "events[]=push" \
        -F "active=true" 2>&1) || {

        # Check if webhook already exists
        if echo "$response" | grep -q "Hook already exists"; then
            echo -e "${YELLOW}SKIPPED (already exists)${NC}"
            ((SKIPPED_COUNT++))
        else
            echo -e "${RED}FAILED${NC}"
            echo "  Error: $response"
            ((FAIL_COUNT++))
        fi
        continue
    }

    echo -e "${GREEN}SUCCESS${NC}"
    ((SUCCESS_COUNT++))
done

# Summary
echo -e "\n${YELLOW}Summary:${NC}"
echo -e "  ${GREEN}Success: $SUCCESS_COUNT${NC}"
echo -e "  ${YELLOW}Skipped: $SKIPPED_COUNT${NC}"
echo -e "  ${RED}Failed: $FAIL_COUNT${NC}"

if [ $FAIL_COUNT -eq 0 ]; then
    echo -e "\n${GREEN}All webhooks configured successfully!${NC}"
else
    echo -e "\n${YELLOW}Some webhooks failed. Please check the errors above.${NC}"
fi
