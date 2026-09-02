#!/usr/bin/env bash
# Test Runner for Ansible Filter Plugins
#
# Usage:
#   ./filter_plugins/tests/run_tests.sh              # Run all tests
#   ./filter_plugins/tests/run_tests.sh unit         # Run unit tests only
#   ./filter_plugins/tests/run_tests.sh coverage     # Run tests with coverage report
#   ./filter_plugins/tests/run_tests.sh lint         # Run code quality checks
#   ./filter_plugins/tests/run_tests.sh clean        # Clean test artifacts
#   ./filter_plugins/tests/run_tests.sh cleanvenv    # Clean virtual environment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"
VENV_DIR="$SCRIPT_DIR/.venv"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Filter Plugin Test Runner${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: python3 is required but not found${NC}"
    exit 1
fi

# Function to setup virtual environment
setup_venv() {
    if [ ! -d "$VENV_DIR" ]; then
        echo -e "${YELLOW}Creating virtual environment at $VENV_DIR...${NC}"
        python3 -m venv "$VENV_DIR"
        echo -e "${GREEN}✓ Virtual environment created${NC}"
    fi

    # Activate virtual environment
    if [ -f "$VENV_DIR/bin/activate" ]; then
        echo -e "${YELLOW}Activating virtual environment...${NC}"
        source "$VENV_DIR/bin/activate"
        echo -e "${GREEN}✓ Virtual environment activated${NC}"
    else
        echo -e "${RED}Error: Virtual environment activation script not found${NC}"
        exit 1
    fi
}

# Function to install test dependencies
install_dependencies() {
    echo -e "${YELLOW}Installing test dependencies...${NC}"
    pip install -q --upgrade pip
    pip install -q -r "$SCRIPT_DIR/requirements.txt"
    echo -e "${GREEN}✓ Dependencies installed${NC}"
    echo ""
}

# Function to run unit tests
run_unit_tests() {
    echo -e "${YELLOW}Running unit tests...${NC}"
    cd "$PROJECT_ROOT"

    python3 -m pytest filter_plugins/tests/unit/ \
        --verbose \
        --tb=short \
        --cov=filter_plugins \
        --cov-report=term-missing \
        --cov-report=html:filter_plugins/tests/coverage_html \
        --cov-report=xml:filter_plugins/tests/coverage.xml

    local exit_code=$?
    if [ $exit_code -eq 0 ]; then
        echo -e "${GREEN}✓ Unit tests passed${NC}"
    else
        echo -e "${RED}✗ Unit tests failed${NC}"
        return $exit_code
    fi
    echo ""
}

# Function to run coverage report
run_coverage() {
    echo -e "${YELLOW}Generating coverage report...${NC}"
    cd "$PROJECT_ROOT"

    python3 -m pytest filter_plugins/tests/unit/ \
        --cov=filter_plugins \
        --cov-report=term-missing \
        --cov-report=html:filter_plugins/tests/coverage_html \
        --cov-report=xml:filter_plugins/tests/coverage.xml

    echo ""
    echo -e "${GREEN}✓ Coverage report generated${NC}"
    echo -e "${BLUE}HTML report: filter_plugins/tests/coverage_html/index.html${NC}"
    echo -e "${BLUE}XML report: filter_plugins/tests/coverage.xml${NC}"
    echo ""
}

# Function to run linting
run_lint() {
    echo -e "${YELLOW}Running code quality checks...${NC}"
    cd "$PROJECT_ROOT"

    if [ -d "filter_plugins" ] && [ "$(ls -A filter_plugins/*.py 2>/dev/null)" ]; then
        echo -e "${BLUE}Running flake8...${NC}"
        python3 -m flake8 filter_plugins/*.py --max-line-length=120 || true

        echo ""
        echo -e "${BLUE}Running pylint...${NC}"
        python3 -m pylint filter_plugins/*.py --max-line-length=120 || true

        echo -e "${GREEN}✓ Linting complete${NC}"
    else
        echo -e "${YELLOW}No filter plugins found to lint${NC}"
    fi
    echo ""
}

# Function to clean test artifacts
clean_artifacts() {
    echo -e "${YELLOW}Cleaning test artifacts...${NC}"
    cd "$PROJECT_ROOT"

    rm -rf filter_plugins/tests/coverage_html
    rm -f filter_plugins/tests/coverage.xml
    rm -rf filter_plugins/tests/.pytest_cache
    rm -rf filter_plugins/tests/__pycache__
    rm -rf filter_plugins/tests/unit/__pycache__
    rm -f .coverage

    echo -e "${GREEN}✓ Test artifacts cleaned${NC}"
    echo ""
}

# Function to clean virtual environment
clean_venv() {
    echo -e "${YELLOW}Cleaning virtual environment...${NC}"
    clean_artifacts
    rm -rf "$VENV_DIR"
    echo -e "${GREEN}✓ Virtual environment removed${NC}"
    echo ""
}

# Main execution
case "${1:-all}" in
    unit)
        setup_venv
        install_dependencies
        run_unit_tests
        ;;
    coverage)
        setup_venv
        install_dependencies
        run_coverage
        ;;
    lint)
        setup_venv
        install_dependencies
        run_lint
        ;;
    clean)
        clean_artifacts
        ;;
    cleanvenv)
        clean_venv
        ;;
    all|*)
        setup_venv
        install_dependencies
        run_unit_tests
        ;;
esac

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Test run complete${NC}"
echo -e "${GREEN}========================================${NC}"
