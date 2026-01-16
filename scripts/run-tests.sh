#!/bin/bash
# Script to run Home Assistant automation tests

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}Home Assistant Automation Testing${NC}"
echo "===================================="
echo ""

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo -e "${GREEN}Activating virtual environment...${NC}"
    source venv/bin/activate
fi

# Check if dependencies are installed
if ! python -c "import pytest" 2>/dev/null; then
    echo -e "${BLUE}Installing test dependencies...${NC}"
    pip install -r requirements-test.txt
fi

echo ""
echo -e "${BLUE}Running tests...${NC}"
echo ""

# Run pytest with arguments passed to script, or default arguments
if [ $# -eq 0 ]; then
    pytest tests/ -v --cov --cov-report=term-missing
else
    pytest "$@"
fi

exit_code=$?

echo ""
if [ $exit_code -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
else
    echo -e "${RED}✗ Some tests failed${NC}"
fi

exit $exit_code
