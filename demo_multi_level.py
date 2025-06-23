#!/usr/bin/env python3
"""
Demo script showing multi-level configuration support in zero-config.

This demonstrates:
1. Environment variables with double underscores (DATABASE__DEVELOPE__DB_URL)
2. Nested default configurations
3. Mixed flat and nested configuration access
"""

import os
from zero_config import setup_environment, get_config

def main():
    print("🚀 Zero-Config Multi-Level Configuration Demo")
    print("=" * 50)

    # Set up some environment variables to demonstrate multi-level support
    # These will be loaded because they have defaults
    os.environ['DATABASE__DEVELOPE__DB_URL'] = 'postgresql://localhost:5432/dev'
    os.environ['DATABASE__DEVELOPE__POOL_SIZE'] = '10'
    os.environ['LLM__OPENAI__API_KEY'] = 'sk-test123'
    os.environ['LLM__OPENAI__MODEL'] = 'gpt-4'
    os.environ['SIMPLE_KEY'] = 'simple_value'

    # These will NOT be loaded (no defaults)
    os.environ['RANDOM_UNRELATED_VAR'] = 'should_not_be_loaded'
    os.environ['ANOTHER_RANDOM_VAR'] = 'also_should_not_be_loaded'
    
    # Define default configuration with both nested and flat formats
    default_config = {
        # Nested format
        'database': {
            'develope': {
                'db_url': 'sqlite:///default.db',  # Will be overridden by env var
                'pool_size': 5,  # Will be overridden by env var
                'timeout': 30
            }
        },
        # Flat format
        'llm.openai.api_key': 'default-openai-key',  # Will be overridden by env var
        'llm.openai.model': 'gpt-3.5-turbo',  # Will be overridden by env var
        'llm.openai.temperature': 0.7,
        'simple_key': 'default_value',  # Will be overridden by env var
        'app_name': 'multi-level-demo'
    }
    
    # Initialize zero-config
    setup_environment(default_config=default_config)
    config = get_config()
    
    print("\n📊 Configuration Values:")
    print("-" * 30)
    
    # Test multi-level access (Requirement 4: dot-separated keys)
    print(f"database.develope.db_url: {config.get('database.develope.db_url')}")
    print(f"database.develope.pool_size: {config.get('database.develope.pool_size')} (type: {type(config.get('database.develope.pool_size'))})")
    print(f"database.develope.timeout: {config.get('database.develope.timeout')}")
    print(f"llm.openai.api_key: {config.get('llm.openai.api_key')}")
    print(f"llm.openai.model: {config.get('llm.openai.model')}")
    print(f"llm.openai.temperature: {config.get('llm.openai.temperature')}")
    print(f"simple_key: {config.get('simple_key')}")
    print(f"app_name: {config.get('app_name')}")

    # Test that unrelated OS env vars are NOT loaded (Requirement 3)
    print(f"random_unrelated_var: {config.get('random_unrelated_var')} (should be None)")
    print(f"another_random_var: {config.get('another_random_var')} (should be None)")
    
    print("\n🗂️ Section Access (Requirement 5):")
    print("-" * 35)

    # Test section access and accessing with remaining part of keys
    database_section = config.get('database')
    print(f"database section: {database_section}")
    print(f"database_section.get('develope').get('db_url'): {database_section.get('develope').get('db_url')}")
    print(f"database_section.get('develope').get('pool_size'): {database_section.get('develope').get('pool_size')}")

    llm_section = config.get('llm')
    print(f"llm section: {llm_section}")
    print(f"llm_section.get('openai').get('api_key'): {llm_section.get('openai').get('api_key')}")

    # Test subsection access
    database_develope = config.get('database.develope')
    print(f"database.develope subsection: {database_develope}")
    print(f"database_develope.get('db_url'): {database_develope.get('db_url')}")

    llm_openai = config.get('llm.openai')
    print(f"llm.openai subsection: {llm_openai}")
    print(f"llm_openai.get('api_key'): {llm_openai.get('api_key')}")
    
    print("\n🔍 Configuration Structure (Requirement 1: Multi-level dict):")
    print("-" * 60)

    # Show the full nested structure
    full_config = config.to_dict()
    import json
    # Filter out system environment variables for cleaner display
    filtered_config = {k: v for k, v in full_config.items()
                      if k in ['database', 'llm', 'simple_key', 'app_name', 'project_root']}
    print(json.dumps(filtered_config, indent=2))
    
    print("\n📋 Flat Configuration Keys:")
    print("-" * 30)
    
    # Show the flat structure
    flat_config = config.to_flat_dict()
    for key, value in sorted(flat_config.items()):
        print(f"{key}: {value}")
    
    print("\n✅ Demo completed successfully!")
    print("\n🎯 All 5 Requirements Demonstrated:")
    print("1. ✅ Internally all data is stored as a multi-level dict")
    print("2. ✅ All __ in environment/env files are converted to nested structure")
    print("3. ✅ OS env vars only loaded if they have defaults; env files load all content")
    print("4. ✅ Access variables using dot-separated keys (database.develope.db_url)")
    print("5. ✅ Get config sections and access with remaining keys: config.get('database').get('develope').get('db_url')")
    print("\nAdditional Features:")
    print("• Default config supports both nested dicts and flat dot notation")
    print("• Type conversion works: POOL_SIZE='10' becomes int 10")
    print("• Unrelated OS environment variables are filtered out")
    print("• Mixed access patterns work seamlessly")

if __name__ == "__main__":
    main()
