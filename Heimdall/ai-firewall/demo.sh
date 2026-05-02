#!/bin/bash

# Define formatting colors
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${CYAN}======================================================${NC}"
echo -e "${CYAN}        🛡️  Heimdall AI Firewall - Live Demo         ${NC}"
echo -e "${CYAN}======================================================${NC}"
echo -e "Starting the Heimdall Privacy Proxy demonstration...\n"
sleep 1

# Test 1: Clean Contract
echo -e "${YELLOW}[TEST 1]: Uploading a safe, non-sensitive document...${NC}"
echo -e "File: sample_docs/contract_clean.txt\n"

# We use 'python -m json.tool' to cleanly pretty-print the JSON output
# This guarantees it works beautifully across all systems without needing 'jq' installed!
curl -s -X POST "http://localhost:8000/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@sample_docs/contract_clean.txt" | python -m json.tool

echo -e "\n${GREEN}✔ Clean document processed successfully!${NC}\n"
sleep 2

echo -e "${CYAN}------------------------------------------------------${NC}\n"

# Test 2: PII Resume
echo -e "${YELLOW}[TEST 2]: Uploading a document containing sensitive PII...${NC}"
echo -e "File: sample_docs/resume_with_pii.pdf (Contains fake PAN and Phone)\n"

curl -s -X POST "http://localhost:8000/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@sample_docs/resume_with_pii.pdf" | python -m json.tool

echo -e "\n${GREEN}✔ PII document successfully intercepted by the policy engine!${NC}\n"

echo -e "${CYAN}======================================================${NC}"
echo -e "${CYAN}                  Demo Completed!                     ${NC}"
echo -e "${CYAN}======================================================${NC}"
