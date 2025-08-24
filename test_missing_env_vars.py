#!/usr/bin/env python3
"""
Test how zero-config handles missing environment variables.
"""

import os
import sys

# Add zero-config to path
sys.path.insert(0, '.')

from zero_config import setup_environment, get_config


def test_missing_env_vars():
    """Test how missing environment variables affect config."""
    
    print("🔍 TESTING MISSING ENVIRONMENT VARIABLES")
    print("=" * 50)
    
    # Clean ALL test environment variables
    for key in list(os.environ.keys()):
        if key.startswith('MISSING__'):
            del os.environ[key]
    
    print("✅ Confirmed: No MISSING__* environment variables exist")
    
    # Test 1: Config with defaults, no env vars
    print("\n1️⃣  Test: Config defaults with NO environment variables")
    print("-" * 50)
    
    config_dict = {
        'missing.bool_true': True,
        'missing.bool_false': False,
        'missing.string_value': 'default_string',
        'missing.number_value': 42,
    }
    
    setup_environment(config_dict)
    config = get_config()
    
    # Check all values
    bool_true_result = config.get('missing.bool_true')
    bool_false_result = config.get('missing.bool_false')
    string_result = config.get('missing.string_value')
    number_result = config.get('missing.number_value')
    
    print(f"missing.bool_true: {bool_true_result} (type: {type(bool_true_result)}) - Expected: True")
    print(f"missing.bool_false: {bool_false_result} (type: {type(bool_false_result)}) - Expected: False")
    print(f"missing.string_value: '{string_result}' (type: {type(string_result)}) - Expected: 'default_string'")
    print(f"missing.number_value: {number_result} (type: {type(number_result)}) - Expected: 42")
    
    # Check if defaults are preserved
    defaults_preserved = (
        bool_true_result == True and
        bool_false_result == False and
        string_result == 'default_string' and
        number_result == 42
    )
    
    print(f"\n📊 Result: {'✅ DEFAULTS PRESERVED' if defaults_preserved else '❌ DEFAULTS CORRUPTED'}")
    
    # Test 2: Add some env vars, leave others missing
    print("\n2️⃣  Test: Some env vars present, others missing")
    print("-" * 50)
    
    # Set only SOME environment variables
    os.environ['MISSING__BOOL_TRUE'] = 'false'  # Override default True → False
    os.environ['MISSING__STRING_VALUE'] = 'from_env'  # Override default
    # Leave MISSING__BOOL_FALSE and MISSING__NUMBER_VALUE unset
    
    print("Set environment variables:")
    print("  MISSING__BOOL_TRUE = 'false'")
    print("  MISSING__STRING_VALUE = 'from_env'")
    print("  (MISSING__BOOL_FALSE and MISSING__NUMBER_VALUE not set)")
    
    # Setup config again
    setup_environment(config_dict)
    config2 = get_config()
    
    # Check results
    bool_true_result2 = config2.get('missing.bool_true')
    bool_false_result2 = config2.get('missing.bool_false')
    string_result2 = config2.get('missing.string_value')
    number_result2 = config2.get('missing.number_value')
    
    print(f"\nResults:")
    print(f"missing.bool_true: {bool_true_result2} (type: {type(bool_true_result2)}) - Expected: False (from env)")
    print(f"missing.bool_false: {bool_false_result2} (type: {type(bool_false_result2)}) - Expected: False (default)")
    print(f"missing.string_value: '{string_result2}' (type: {type(string_result2)}) - Expected: 'from_env' (from env)")
    print(f"missing.number_value: {number_result2} (type: {type(number_result2)}) - Expected: 42 (default)")
    
    # Check if behavior is correct
    correct_behavior = (
        bool_true_result2 == False and  # Overridden by env
        bool_false_result2 == False and  # Default preserved
        string_result2 == 'from_env' and  # Overridden by env
        number_result2 == 42  # Default preserved
    )
    
    print(f"\n📊 Result: {'✅ CORRECT BEHAVIOR' if correct_behavior else '❌ INCORRECT BEHAVIOR'}")
    
    # Test 3: Check if missing env vars cause None values
    print("\n3️⃣  Test: Do missing env vars cause None values?")
    print("-" * 50)
    
    none_values = []
    if bool_false_result2 is None:
        none_values.append('missing.bool_false')
    if number_result2 is None:
        none_values.append('missing.number_value')
    
    if none_values:
        print(f"❌ PROBLEM: These values are None: {none_values}")
        print("   Missing environment variables are causing None values!")
    else:
        print("✅ GOOD: No None values found")
        print("   Missing environment variables preserve defaults correctly")
    
    # Clean up
    for key in list(os.environ.keys()):
        if key.startswith('MISSING__'):
            del os.environ[key]
    
    print("\n" + "=" * 50)
    print("🎯 CONCLUSION:")
    if defaults_preserved and correct_behavior and not none_values:
        print("✅ Zero-config handles missing environment variables correctly")
        print("✅ Missing env vars preserve default values (no None corruption)")
    else:
        print("❌ Zero-config has issues with missing environment variables")
        print("❌ Missing env vars may cause None values or other problems")


if __name__ == "__main__":
    test_missing_env_vars()
