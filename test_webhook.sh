#!/bin/bash
#
# Test the webhook server
#

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Default values
HOST=${1:-localhost}
PORT=${2:-5000}
BASE_URL="http://$HOST:$PORT"

echo -e "${YELLOW}Testing webhook server at $BASE_URL${NC}\n"

# Test 1: Health check
echo -n "Test 1: Health check... "
if curl -s -f "$BASE_URL/health" > /dev/null; then
    echo -e "${GREEN}PASSED${NC}"
    curl -s "$BASE_URL/health" | python3 -m json.tool
else
    echo -e "${RED}FAILED${NC}"
    exit 1
fi

echo

# Test 2: Index page
echo -n "Test 2: Index page... "
if curl -s -f "$BASE_URL/" > /dev/null; then
    echo -e "${GREEN}PASSED${NC}"
    curl -s "$BASE_URL/" | python3 -m json.tool
else
    echo -e "${RED}FAILED${NC}"
    exit 1
fi

echo

# Test 3: Webhook endpoint (should fail without proper signature)
echo -n "Test 3: Webhook endpoint (expects 403)... "
response=$(curl -s -w "\n%{http_code}" -X POST \
    -H "Content-Type: application/json" \
    -H "X-GitHub-Event: push" \
    -d '{"repository":{"full_name":"naokiiida/libft"}}' \
    "$BASE_URL/webhook")

status_code=$(echo "$response" | tail -n1)
if [ "$status_code" == "403" ]; then
    echo -e "${GREEN}PASSED (correctly rejected invalid signature)${NC}"
else
    echo -e "${RED}FAILED (expected 403, got $status_code)${NC}"
fi

echo

# Test 4: Invalid event type
echo -n "Test 4: Invalid event type (expects 200)... "
response=$(curl -s -w "\n%{http_code}" -X POST \
    -H "Content-Type: application/json" \
    -H "X-GitHub-Event: issues" \
    -d '{"repository":{"full_name":"naokiiida/libft"}}' \
    "$BASE_URL/webhook")

status_code=$(echo "$response" | tail -n1)
if [ "$status_code" == "200" ]; then
    echo -e "${GREEN}PASSED (correctly ignored non-push event)${NC}"
else
    echo -e "${RED}FAILED (expected 200, got $status_code)${NC}"
fi

echo
echo -e "${GREEN}All tests completed!${NC}"
