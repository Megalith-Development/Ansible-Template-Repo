#!/usr/bin/env python3
"""
Unit tests for example_filters.py

This file demonstrates the testing requirements for custom Ansible filter plugins.
ALL filter functions MUST have comprehensive test coverage including:
- Normal operation test cases
- Edge cases
- Error handling
"""

import pytest
import sys
from pathlib import Path

# Add filter_plugins to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from example_filters import FilterModule
from ansible.errors import AnsibleFilterError


@pytest.fixture
def filter_module():
    """Fixture to provide FilterModule instance"""
    return FilterModule()


class TestUppercase:
    """Test uppercase filter"""

    def test_uppercase_normal(self, filter_module):
        """Test normal uppercase conversion"""
        result = filter_module.uppercase('hello')
        assert result == 'HELLO'

    def test_uppercase_already_uppercase(self, filter_module):
        """Test string already in uppercase"""
        result = filter_module.uppercase('WORLD')
        assert result == 'WORLD'

    def test_uppercase_mixed_case(self, filter_module):
        """Test mixed case string"""
        result = filter_module.uppercase('HeLLo WoRLd')
        assert result == 'HELLO WORLD'

    def test_uppercase_with_numbers(self, filter_module):
        """Test string with numbers"""
        result = filter_module.uppercase('hello123')
        assert result == 'HELLO123'

    def test_uppercase_with_special_chars(self, filter_module):
        """Test string with special characters"""
        result = filter_module.uppercase('hello-world_test')
        assert result == 'HELLO-WORLD_TEST'

    def test_uppercase_empty_string(self, filter_module):
        """Test with empty string raises error"""
        with pytest.raises(AnsibleFilterError, match='requires non-empty string'):
            filter_module.uppercase('')

    def test_uppercase_non_string(self, filter_module):
        """Test with non-string input raises error"""
        with pytest.raises(AnsibleFilterError, match='requires string input'):
            filter_module.uppercase(123)

    def test_uppercase_none(self, filter_module):
        """Test with None raises error"""
        with pytest.raises(AnsibleFilterError, match='requires string input'):
            filter_module.uppercase(None)


class TestAddPrefix:
    """Test add_prefix filter"""

    def test_add_prefix_default(self, filter_module):
        """Test with default prefix"""
        result = filter_module.add_prefix('world')
        assert result == 'prefixworld'

    def test_add_prefix_custom(self, filter_module):
        """Test with custom prefix"""
        result = filter_module.add_prefix('world', 'hello_')
        assert result == 'hello_world'

    def test_add_prefix_empty_prefix(self, filter_module):
        """Test with empty prefix"""
        result = filter_module.add_prefix('test', '')
        assert result == 'test'

    def test_add_prefix_empty_value(self, filter_module):
        """Test with empty value"""
        result = filter_module.add_prefix('', 'prefix_')
        assert result == 'prefix_'

    def test_add_prefix_special_chars(self, filter_module):
        """Test with special characters"""
        result = filter_module.add_prefix('test', '@@_')
        assert result == '@@_test'

    def test_add_prefix_non_string_value(self, filter_module):
        """Test with non-string value raises error"""
        with pytest.raises(AnsibleFilterError, match='requires string value'):
            filter_module.add_prefix(123, 'prefix_')

    def test_add_prefix_non_string_prefix(self, filter_module):
        """Test with non-string prefix raises error"""
        with pytest.raises(AnsibleFilterError, match='requires string prefix'):
            filter_module.add_prefix('test', 123)

    def test_add_prefix_none_value(self, filter_module):
        """Test with None value raises error"""
        with pytest.raises(AnsibleFilterError, match='requires string value'):
            filter_module.add_prefix(None, 'prefix_')


class TestSafeDivide:
    """Test safe_divide filter"""

    def test_safe_divide_normal(self, filter_module):
        """Test normal division"""
        result = filter_module.safe_divide(10, 2)
        assert result == 5.0

    def test_safe_divide_float_result(self, filter_module):
        """Test division with float result"""
        result = filter_module.safe_divide(10, 3)
        assert abs(result - 3.333333) < 0.00001

    def test_safe_divide_by_zero_default(self, filter_module):
        """Test division by zero returns default value"""
        result = filter_module.safe_divide(10, 0)
        assert result == 0

    def test_safe_divide_by_zero_custom_default(self, filter_module):
        """Test division by zero returns custom default"""
        result = filter_module.safe_divide(10, 0, -1)
        assert result == -1

    def test_safe_divide_negative_numbers(self, filter_module):
        """Test division with negative numbers"""
        result = filter_module.safe_divide(-10, 2)
        assert result == -5.0

    def test_safe_divide_float_inputs(self, filter_module):
        """Test division with float inputs"""
        result = filter_module.safe_divide(10.5, 2.5)
        assert result == 4.2

    def test_safe_divide_string_numbers(self, filter_module):
        """Test division with string numbers (should convert)"""
        result = filter_module.safe_divide('10', '2')
        assert result == 5.0

    def test_safe_divide_non_numeric_numerator(self, filter_module):
        """Test with non-numeric numerator raises error"""
        with pytest.raises(AnsibleFilterError, match='requires numeric inputs'):
            filter_module.safe_divide('abc', 2)

    def test_safe_divide_non_numeric_denominator(self, filter_module):
        """Test with non-numeric denominator raises error"""
        with pytest.raises(AnsibleFilterError, match='requires numeric inputs'):
            filter_module.safe_divide(10, 'xyz')

    def test_safe_divide_none_inputs(self, filter_module):
        """Test with None inputs raises error"""
        with pytest.raises(AnsibleFilterError, match='requires numeric inputs'):
            filter_module.safe_divide(None, 2)
