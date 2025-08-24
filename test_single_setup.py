#!/usr/bin/env python3
"""
Test zero-config with single setup_environment call.
"""

import os
import sys

# Add zero-config to path
sys.path.insert(0, '.')

from zero_config import setup_environment, get_config


def test_single_setup():
    """Test zero-config with single setup call."""
    
    print("🔍 TESTING SINGLE SETUP_ENVIRONMENT CALL")
    print("=" * 45)
    
    # Clean environment
    for key in list(os.environ.keys()):
        if key.startswith('SINGLE__'):
            del os.environ[key]
    
    # Set environment variables BEFORE setup
    os.environ['SINGLE__BOOL_TRUE'] = 'false'
    os.environ['SINGLE__BOOL_FALSE'] = 'true'
    os.environ['SINGLE__STRING_VALUE'] = 'from_env'
    os.environ['SINGLE__NUMBER_VALUE'] = '999'
    
    print("Environment variables set BEFORE setup:")
    print("  SINGLE__BOOL_TRUE = 'false'")
    print("  SINGLE__BOOL_FALSE = 'true'")
    print("  SINGLE__STRING_VALUE = 'from_env'")
    print("  SINGLE__NUMBER_VALUE = '999'")
    
    # Setup config (SINGLE CALL)
    config_dict = {
        'single.bool_true': True,      # Default True, env 'false' → should be False
        'single.bool_false': False,    # Default False, env 'true' → should be True
        'single.string_value': 'default',  # Default 'default', env 'from_env' → should be 'from_env'
        'single.number_value': 42,     # Default 42, env '999' → should be 999
    }
    
    print(f"\nConfig defaults:")
    for key, value in config_dict.items():
        print(f"  {key}: {value}")
    
    print(f"\n🔄 Calling setup_environment() once...")
    setup_environment(config_dict)
    config = get_config()
    
    # Check results
    print(f"\n📊 Results:")
    results = {}
    for key in config_dict.keys():
        result = config.get(key)
        results[key] = result
        print(f"  {key}: {result} (type: {type(result)})")
    
    # Expected vs actual
    print(f"\n🎯 Expected vs Actual:")
    expected = {
        'single.bool_true': False,     # 'false' → False
        'single.bool_false': True,     # 'true' → True
        'single.string_value': 'from_env',  # 'from_env' → 'from_env'
        'single.number_value': 999,    # '999' → 999
    }
    
    all_correct = True
    for key, expected_val in expected.items():
        actual_val = results[key]
        status = "✅" if actual_val == expected_val else "❌"
        if actual_val != expected_val:
            all_correct = False
        print(f"  {key}: Expected {expected_val}, Got {actual_val} {status}")
    
    print(f"\n🎉 Overall: {'✅ ALL CORRECT' if all_correct else '❌ SOME FAILED'}")
    
    # Clean up
    for key in list(os.environ.keys()):
        if key.startswith('SINGLE__'):
            del os.environ[key]
    
    return all_correct


if __name__ == "__main__":
    success = test_single_setup()
    if success:
        print("\n✅ CONCLUSION: Zero-config works correctly with single setup")
        print("   The issue is likely multiple setup_environment() calls")
    else:
        print("\n❌ CONCLUSION: Zero-config has fundamental environment variable issues")
