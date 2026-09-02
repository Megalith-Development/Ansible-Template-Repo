# Filter Plugin Tests

This directory contains tests for custom Ansible filter plugins.

## Overview

ALL custom Python filter plugins in this repository MUST have corresponding unit tests. This ensures code quality, prevents regressions, and provides documentation for filter behavior.

## Requirements

Per AGENTS.md:

- Each filter plugin MUST have a corresponding test file in `unit/`
- Test files MUST follow naming convention: `test_<filter_name>.py`
- Each filter function MUST have test coverage for:
  - Normal operation
  - Edge cases (empty strings, None values, boundary conditions)
  - Error handling (invalid inputs, type errors)
- Tests MUST use pytest framework
- Tests SHOULD achieve 95%+ code coverage

## Directory Structure

```
filter_plugins/tests/
├── README.md              # This file
├── pytest.ini             # Pytest configuration
├── requirements.txt       # Python test dependencies
├── run_tests.sh          # Test runner script (recommended)
├── unit/                 # Unit tests
│   ├── test_example_filters.py
│   └── test_<your_filter>.py
├── fixtures/             # Optional: test data
└── coverage_html/        # Generated: HTML coverage reports
```

## Running Tests

### Quick Start

```bash
# Run all tests (recommended)
./filter_plugins/tests/run_tests.sh

# Run unit tests only
./filter_plugins/tests/run_tests.sh unit

# Generate coverage report
./filter_plugins/tests/run_tests.sh coverage

# Run code quality checks
./filter_plugins/tests/run_tests.sh lint

# Clean test artifacts
./filter_plugins/tests/run_tests.sh clean
```

The test runner automatically:
- Creates a Python virtual environment
- Installs all dependencies
- Runs tests with coverage reporting
- Manages cleanup

### Manual Execution

If you prefer to run tests manually:

```bash
# Install dependencies
pip install -r filter_plugins/tests/requirements.txt

# Run all unit tests
python3 -m pytest filter_plugins/tests/unit/ -v

# Run specific test file
python3 -m pytest filter_plugins/tests/unit/test_example_filters.py -v

# Run with coverage
python3 -m pytest filter_plugins/tests/unit/ \
    --cov=filter_plugins \
    --cov-report=term-missing \
    --cov-report=html:filter_plugins/tests/coverage_html
```

## Adding New Tests

When creating a new filter plugin:

1. **Create the filter**: `filter_plugins/my_new_filters.py`
2. **Create the test file**: `filter_plugins/tests/unit/test_my_new_filters.py`
3. **Write comprehensive tests**: Cover normal operation, edge cases, and errors
4. **Run the tests**: `./filter_plugins/tests/run_tests.sh`
5. **Check coverage**: View `filter_plugins/tests/coverage_html/index.html`

### Test Template

```python
#!/usr/bin/env python3
"""Unit tests for my_new_filters.py"""

import pytest
import sys
from pathlib import Path

# Add filter_plugins to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from my_new_filters import FilterModule
from ansible.errors import AnsibleFilterError


@pytest.fixture
def filter_module():
    """Fixture to provide FilterModule instance"""
    return FilterModule()


class TestMyFilter:
    """Test my_filter function"""

    def test_normal_operation(self, filter_module):
        """Test normal operation"""
        result = filter_module.my_filter('input')
        assert result == 'expected_output'

    def test_edge_case_empty(self, filter_module):
        """Test with empty input"""
        with pytest.raises(AnsibleFilterError):
            filter_module.my_filter('')

    def test_error_handling(self, filter_module):
        """Test error handling"""
        with pytest.raises(AnsibleFilterError, match='specific error message'):
            filter_module.my_filter(None)
```

## Example Test Coverage

The `test_example_filters.py` file demonstrates comprehensive testing:

- **TestUppercase**: 8 test cases
  - Normal conversion, already uppercase, mixed case
  - Numbers, special characters
  - Empty string, non-string input, None value

- **TestAddPrefix**: 8 test cases
  - Default prefix, custom prefix, empty prefix
  - Empty value, special characters
  - Type validation, None handling

- **TestSafeDivide**: 10 test cases
  - Normal division, float results
  - Division by zero with default/custom values
  - Negative numbers, float inputs
  - String number conversion
  - Error handling for non-numeric inputs

**Total**: 26 test cases covering all functions and edge cases

## Coverage Goals

- **Target**: 95%+ code coverage
- **View coverage**: Open `filter_plugins/tests/coverage_html/index.html` after running tests

## Continuous Integration

The GitHub Actions workflow (`.github/workflows/validate.yml`) automatically runs filter plugin tests on every push and pull request.

## Troubleshooting

### Virtual Environment Issues

```bash
# Clean and recreate virtual environment
./filter_plugins/tests/run_tests.sh cleanvenv
./filter_plugins/tests/run_tests.sh
```

### Import Errors

```bash
# Ensure virtual environment is activated
source filter_plugins/tests/.venv/bin/activate

# Or set PYTHONPATH manually
export PYTHONPATH="${PYTHONPATH}:${PWD}/filter_plugins"
```

### Permission Denied

```bash
# Make test runner executable
chmod +x filter_plugins/tests/run_tests.sh
```

## Best Practices

1. **Test Independence**: Each test should be independent and not rely on others
2. **Descriptive Names**: Use clear test names that explain what is being tested
3. **Assert Messages**: Include helpful messages in assertions
4. **Edge Cases**: Always test boundary conditions, empty values, None, invalid types
5. **Documentation**: Add docstrings to test classes and methods
6. **Coverage**: Aim for 95%+ code coverage but focus on meaningful tests

## Reference Implementation

This test structure is based on the production implementation at:
`/Users/bgrimmet/Nextcloud/Projects/Ansible-Certificate-Renewal/tests`

## Questions?

See the main project README or AGENTS.md for more information.
