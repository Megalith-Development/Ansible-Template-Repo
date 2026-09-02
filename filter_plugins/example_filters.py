#!/usr/bin/env python3
"""
Example custom Ansible filter plugins

This module demonstrates the structure and testing requirements for custom filters.
Each filter function MUST have corresponding unit tests in tests/unit/test_example_filters.py
"""

from ansible.errors import AnsibleFilterError


class FilterModule:
    """Ansible filter plugin class"""

    def filters(self):
        """Return dictionary of filter names to functions"""
        return {
            'uppercase': self.uppercase,
            'add_prefix': self.add_prefix,
            'safe_divide': self.safe_divide,
        }

    @staticmethod
    def uppercase(value):
        """
        Convert string to uppercase

        Args:
            value (str): The string to convert

        Returns:
            str: Uppercase version of the input

        Raises:
            AnsibleFilterError: If value is not a string

        Example:
            {{ "hello" | uppercase }}  # Returns "HELLO"
        """
        if not isinstance(value, str):
            raise AnsibleFilterError(f'uppercase filter requires string input, got {type(value).__name__}')

        if not value:
            raise AnsibleFilterError('uppercase filter requires non-empty string')

        return value.upper()

    @staticmethod
    def add_prefix(value, prefix='prefix'):
        """
        Add a prefix to a string

        Args:
            value (str): The string to prefix
            prefix (str): The prefix to add (default: 'prefix')

        Returns:
            str: Prefixed string

        Raises:
            AnsibleFilterError: If value or prefix is not a string

        Example:
            {{ "world" | add_prefix("hello_") }}  # Returns "hello_world"
        """
        if not isinstance(value, str):
            raise AnsibleFilterError(f'add_prefix filter requires string value, got {type(value).__name__}')

        if not isinstance(prefix, str):
            raise AnsibleFilterError(f'add_prefix filter requires string prefix, got {type(prefix).__name__}')

        return f"{prefix}{value}"

    @staticmethod
    def safe_divide(numerator, denominator, default=0):
        """
        Safely divide two numbers, returning a default value on division by zero

        Args:
            numerator (int|float): The numerator
            denominator (int|float): The denominator
            default (int|float): Value to return if denominator is zero (default: 0)

        Returns:
            int|float: Result of division or default value

        Raises:
            AnsibleFilterError: If inputs are not numeric

        Example:
            {{ 10 | safe_divide(2) }}     # Returns 5
            {{ 10 | safe_divide(0, -1) }} # Returns -1
        """
        try:
            numerator = float(numerator)
            denominator = float(denominator)
            default = float(default)
        except (TypeError, ValueError) as e:
            raise AnsibleFilterError(f'safe_divide filter requires numeric inputs: {e}')

        if denominator == 0:
            return default

        return numerator / denominator
