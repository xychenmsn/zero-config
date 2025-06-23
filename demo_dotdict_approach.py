#!/usr/bin/env python3
"""
Demo showing the simplified DotDict approach for environment variable matching.

Your approach:
1. Flatten config keys to ENV_VAR format (DATABASE__DEVELOPE__DB_URL)
2. Loop through flattened keys and directly check os.environ[key]
3. If found, parse key back to dot format and use config[dot_key] = value

The underlying dict natively supports dot notation for get/set operations.
"""

import os
from zero_config import setup_environment, get_config


def main():
    print("🚀 DotDict Approach Demo - Your Simplified Method")
    print("=" * 55)
    
    # Set up environment variables
    os.environ['DATABASE__DEVELOPE__DB_URL'] = 'postgresql://localhost:5432/dev'
    os.environ['DATABASE__DEVELOPE__POOL_SIZE'] = '25'
    os.environ['LLM__OPENAI__API_KEY'] = 'sk-dotdict-test'
    os.environ['UNRELATED_VAR'] = 'should_not_be_loaded'
    
    try:
        # Default config with nested structure
        default_config = {
            'database': {
                'develope': {
                    'db_url': 'sqlite:///default.db',
                    'pool_size': 10,
                    'timeout': 30
                }
            },
            'llm': {
                'openai': {
                    'api_key': 'default-key',
                    'model': 'gpt-3.5-turbo'
                }
            },
            'simple_key': 'default_value'
        }
        
        setup_environment(default_config=default_config)
        config = get_config()
        
        print("\n📊 Your Approach in Action:")
        print("-" * 30)
        print("1. ✅ Flatten config keys to ENV_VAR format:")
        print("   database.develope.db_url → DATABASE__DEVELOPE__DB_URL")
        print("   database.develope.pool_size → DATABASE__DEVELOPE__POOL_SIZE")
        print("   llm.openai.api_key → LLM__OPENAI__API_KEY")
        
        print("\n2. ✅ Loop through ENV_VAR keys and check os.environ:")
        print("   os.environ['DATABASE__DEVELOPE__DB_URL'] ✓ Found!")
        print("   os.environ['DATABASE__DEVELOPE__POOL_SIZE'] ✓ Found!")
        print("   os.environ['LLM__OPENAI__API_KEY'] ✓ Found!")
        print("   os.environ['UNRELATED_VAR'] ❌ Not in our config keys")
        
        print("\n3. ✅ Parse back to dot notation and set directly:")
        print("   config['database.develope.db_url'] = 'postgresql://localhost:5432/dev'")
        print("   config['database.develope.pool_size'] = 25")
        print("   config['llm.openai.api_key'] = 'sk-dotdict-test'")
        
        print("\n🎯 Results:")
        print("-" * 10)
        print(f"database.develope.db_url: {config.get('database.develope.db_url')}")
        print(f"database.develope.pool_size: {config.get('database.develope.pool_size')} (type: {type(config.get('database.develope.pool_size'))})")
        print(f"database.develope.timeout: {config.get('database.develope.timeout')} (unchanged)")
        print(f"llm.openai.api_key: {config.get('llm.openai.api_key')}")
        print(f"llm.openai.model: {config.get('llm.openai.model')} (unchanged)")
        print(f"simple_key: {config.get('simple_key')}")
        print(f"unrelated_var: {config.get('unrelated_var')} (should be None)")
        
        print("\n🗂️ Native Dot Notation Support:")
        print("-" * 35)
        
        # Show that the underlying dict supports dot notation natively
        print("✅ Native get: config['database.develope.db_url']")
        print("✅ Native set: config['new.nested.key'] = 'value'")
        print("✅ Section access: config['database'] returns entire section")
        print("✅ Subsection access: config['database.develope'] returns subsection")
        
        # Demonstrate section access
        database_section = config.get('database')
        print(f"\nDatabase section: {database_section}")
        
        # Show that we can access nested parts naturally
        develope_section = config.get('database.develope')
        print(f"Develope subsection: {develope_section}")
        
        print("\n⚡ Performance Benefits:")
        print("-" * 25)
        print("• Only loop through config keys (not all env vars)")
        print("• Direct os.environ lookup: O(1) per config key")
        print("• Native dot notation: no complex parsing needed")
        print("• Simple and intuitive: config[dot_key] = value")
        
        print("\n✅ Your Approach Advantages:")
        print("-" * 30)
        print("1. 🎯 Efficient: Only check env vars that matter")
        print("2. 🔧 Simple: Native dict operations with dot notation")
        print("3. 🚀 Fast: Direct lookup instead of iteration")
        print("4. 🧠 Intuitive: Straightforward key conversion")
        print("5. 🛠️ Maintainable: Clean, readable code")
        
    finally:
        # Clean up environment
        for var in ['DATABASE__DEVELOPE__DB_URL', 'DATABASE__DEVELOPE__POOL_SIZE', 
                    'LLM__OPENAI__API_KEY', 'UNRELATED_VAR']:
            if var in os.environ:
                del os.environ[var]


if __name__ == "__main__":
    main()
