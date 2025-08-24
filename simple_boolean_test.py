#!/usr/bin/env python3
"""
Simple test to isolate zero-config boolean parsing issues.
"""

import os
import sys

# Add zero-config to path
sys.path.insert(0, '.')

from zero_config import setup_environment, get_config


def test_simple_boolean():
    """Simple boolean test to isolate the issue."""
    
    print("🔍 SIMPLE ZERO-CONFIG BOOLEAN TEST")
    print("=" * 40)
    
    # Clean environment
    for key in list(os.environ.keys()):
        if key.startswith('SIMPLE__'):
            del os.environ[key]
    
    # Test 1: Basic true/false
    print("\n1️⃣  Testing basic true/false:")
    
    # Set environment variables
    os.environ['SIMPLE__BOOL_TRUE'] = 'false'
    os.environ['SIMPLE__BOOL_FALSE'] = 'true'
    
    # Setup config
    config_dict = {
        'simple.bool_true': True,
        'simple.bool_false': False,
    }
    
    setup_environment(config_dict)
    config = get_config()
    
    # Check results
    result_true = config.get('simple.bool_true')
    result_false = config.get('simple.bool_false')
    
    print(f"Config: simple.bool_true = True (default)")
    print(f"Env: SIMPLE__BOOL_TRUE = 'false'")
    print(f"Result: {result_true} (type: {type(result_true)})")
    print(f"Expected: False")
    print(f"Status: {'✅ PASS' if result_true == False else '❌ FAIL'}")
    
    print()
    print(f"Config: simple.bool_false = False (default)")
    print(f"Env: SIMPLE__BOOL_FALSE = 'true'")
    print(f"Result: {result_false} (type: {type(result_false)})")
    print(f"Expected: True")
    print(f"Status: {'✅ PASS' if result_false == True else '❌ FAIL'}")
    
    # Test 2: Check if environment variables are being read at all
    print("\n2️⃣  Testing if environment variables are read:")
    
    os.environ['SIMPLE__STRING_TEST'] = 'from_env'
    
    config_dict2 = {'simple.string_test': 'default_value'}
    setup_environment(config_dict2)
    config2 = get_config()
    
    string_result = config2.get('simple.string_test')
    print(f"Config: simple.string_test = 'default_value'")
    print(f"Env: SIMPLE__STRING_TEST = 'from_env'")
    print(f"Result: '{string_result}'")
    print(f"Status: {'✅ ENV READ' if string_result == 'from_env' else '❌ ENV NOT READ'}")
    
    # Test 3: Direct smart_convert test
    print("\n3️⃣  Testing smart_convert function directly:")
    
    from zero_config.config import smart_convert
    
    test_cases = [
        ('true', True, True),
        ('false', True, False),
        ('True', False, True),
        ('False', False, False),
    ]
    
    for str_val, default, expected in test_cases:
        result = smart_convert(str_val, default)
        status = '✅ PASS' if result == expected else '❌ FAIL'
        print(f"smart_convert('{str_val}', {default}) → {result} (expected: {expected}) {status}")
    
    # Clean up
    for key in list(os.environ.keys()):
        if key.startswith('SIMPLE__'):
            del os.environ[key]


if __name__ == "__main__":
    test_simple_boolean()
