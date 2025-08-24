#!/usr/bin/env python3
"""
Comprehensive test suite for zero-config boolean parsing.

This test verifies that zero-config correctly handles boolean environment variables
with various formats and cases.
"""

import os
import sys
from typing import Dict, Any, List, Tuple

# Add zero-config to path
sys.path.insert(0, '.')

from zero_config import setup_environment, get_config


def run_boolean_test(env_key: str, env_value: str, config_key: str, default_value: bool, test_id: int) -> Tuple[str, bool, bool, str]:
    """
    Run a single boolean parsing test.

    Returns:
        (env_value, expected_result, actual_result, status)
    """
    # Use unique keys to avoid caching issues
    unique_env_key = f"{env_key}_{test_id}"
    unique_config_key = f"{config_key}_{test_id}"

    # Clean environment
    for key in list(os.environ.keys()):
        if key.startswith('TEST__'):
            del os.environ[key]

    # Set test environment variable
    os.environ[unique_env_key] = env_value

    # Setup test configuration
    test_config = {unique_config_key: default_value}
    setup_environment(test_config)
    config = get_config()

    # Get result
    result = config.get(unique_config_key)
    
    # Determine expected result based on boolean parsing rules
    str_lower = env_value.lower()
    if str_lower in ('true', '1', 'yes', 'on', 'enabled'):
        expected = True
    elif str_lower in ('false', '0', 'no', 'off', 'disabled'):
        expected = False
    else:
        expected = default_value  # Should keep default for invalid values
    
    # Check if result matches expectation
    status = "✅ PASS" if result == expected else "❌ FAIL"
    
    return env_value, expected, result, status


def test_zero_config_boolean_parsing():
    """Comprehensive test suite for zero-config boolean parsing."""
    
    print("🧪 COMPREHENSIVE ZERO-CONFIG BOOLEAN PARSING TESTS")
    print("=" * 60)
    
    # Test cases: (env_value, description)
    test_cases = [
        # Standard boolean strings
        ('true', 'lowercase true'),
        ('false', 'lowercase false'),
        ('True', 'capitalized True'),
        ('False', 'capitalized False'),
        ('TRUE', 'uppercase TRUE'),
        ('FALSE', 'uppercase FALSE'),
        
        # Numeric boolean values
        ('1', 'numeric 1 (true)'),
        ('0', 'numeric 0 (false)'),
        
        # Alternative boolean words
        ('yes', 'yes (true)'),
        ('no', 'no (false)'),
        ('on', 'on (true)'),
        ('off', 'off (false)'),
        ('enabled', 'enabled (true)'),
        ('disabled', 'disabled (false)'),
        
        # Invalid/edge cases
        ('invalid', 'invalid string (should keep default)'),
        ('2', 'numeric 2 (should keep default)'),
        ('maybe', 'maybe (should keep default)'),
        ('', 'empty string (should keep default)'),
    ]
    
    # Test with default = True
    print("\n1️⃣  Testing with default = True:")
    print("-" * 40)
    print(f"{'Value':<12} {'Expected':<8} {'Actual':<8} {'Status':<10} {'Description'}")
    print("-" * 60)
    
    results_true_default = []
    for i, (env_value, description) in enumerate(test_cases):
        env_value_str, expected, actual, status = run_boolean_test(
            'TEST__BOOL_TRUE', env_value, 'test.bool_true', True, i
        )
        results_true_default.append((env_value_str, expected, actual, status))
        print(f"{env_value:<12} {str(expected):<8} {str(actual):<8} {status:<10} {description}")
    
    # Test with default = False
    print("\n2️⃣  Testing with default = False:")
    print("-" * 40)
    print(f"{'Value':<12} {'Expected':<8} {'Actual':<8} {'Status':<10} {'Description'}")
    print("-" * 60)
    
    results_false_default = []
    for i, (env_value, description) in enumerate(test_cases):
        env_value_str, expected, actual, status = run_boolean_test(
            'TEST__BOOL_FALSE', env_value, 'test.bool_false', False, i + 100
        )
        results_false_default.append((env_value_str, expected, actual, status))
        print(f"{env_value:<12} {str(expected):<8} {str(actual):<8} {status:<10} {description}")
    
    # Test type consistency
    print("\n3️⃣  Testing type consistency:")
    print("-" * 40)
    
    type_test_cases = [('true', True), ('false', False), ('1', True), ('0', False)]
    for i, (env_value, default) in enumerate(type_test_cases):
        _, _, result, _ = run_boolean_test('TEST__TYPE', env_value, 'test.type', default, i + 200)
        result_type = type(result)
        type_status = "✅ PASS" if result_type == bool else "❌ FAIL"
        print(f"Value: {env_value:<6} → Result: {result} (type: {result_type}) {type_status}")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY:")
    
    # Count results
    true_default_passes = sum(1 for _, _, _, status in results_true_default if "PASS" in status)
    true_default_total = len(results_true_default)
    
    false_default_passes = sum(1 for _, _, _, status in results_false_default if "PASS" in status)
    false_default_total = len(results_false_default)
    
    total_passes = true_default_passes + false_default_passes
    total_tests = true_default_total + false_default_total
    
    print(f"Default = True:  {true_default_passes}/{true_default_total} tests passed")
    print(f"Default = False: {false_default_passes}/{false_default_total} tests passed")
    print(f"Overall:         {total_passes}/{total_tests} tests passed")
    
    if total_passes == total_tests:
        print("\n🎉 ALL TESTS PASSED! Zero-config boolean parsing is working correctly.")
    else:
        print(f"\n❌ {total_tests - total_passes} TESTS FAILED! Zero-config boolean parsing has issues.")
        
        # Show failed tests
        print("\nFailed tests:")
        for env_val, expected, actual, status in results_true_default + results_false_default:
            if "FAIL" in status:
                print(f"  {env_val} → Expected: {expected}, Got: {actual}")
    
    # Clean up
    for key in list(os.environ.keys()):
        if key.startswith('TEST__'):
            del os.environ[key]


if __name__ == "__main__":
    test_zero_config_boolean_parsing()
