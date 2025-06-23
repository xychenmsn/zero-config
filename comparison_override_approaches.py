#!/usr/bin/env python3
"""
Comparison of override approaches: Current vs Your Better Approach
"""

import os
from typing import Dict, Any


def demonstrate_current_approach():
    """Current approach: Work with flattened config throughout."""
    print("🔄 Current Approach: Flattened Config Override")
    print("=" * 50)
    
    # Start with nested config
    original_nested = {
        'database': {
            'develope': {
                'db_url': 'sqlite:///default.db',
                'pool_size': 10
            }
        },
        'llm': {
            'openai': {
                'api_key': 'default-key'
            }
        }
    }
    
    # Step 1: Flatten the config (what we currently do)
    flattened_config = {
        'database.develope.db_url': 'sqlite:///default.db',
        'database.develope.pool_size': 10,
        'llm.openai.api_key': 'default-key'
    }
    
    print("📊 Flattened config:")
    for key, value in flattened_config.items():
        print(f"   {key}: {value}")
    
    # Step 2: Apply environment variables (current way)
    env_vars = {
        'DATABASE__DEVELOPE__DB_URL': 'postgresql://localhost:5432/dev',
        'DATABASE__DEVELOPE__POOL_SIZE': '20'
    }
    
    print("\n🔄 Applying environment variables...")
    for env_var, env_value in env_vars.items():
        # Convert env var to dot notation
        config_key = '.'.join([part.lower() for part in env_var.split('__')])
        if config_key in flattened_config:
            old_value = flattened_config[config_key]
            flattened_config[config_key] = int(env_value) if isinstance(old_value, int) else env_value
            print(f"   ✅ {env_var} → {config_key}: {old_value} → {flattened_config[config_key]}")
    
    print("\n📊 Final flattened config:")
    for key, value in flattened_config.items():
        print(f"   {key}: {value}")
    
    # Step 3: Problem - We need to rebuild nested structure for final use
    print("\n❌ Problem: Need to rebuild nested structure from flat keys")
    print("   This is complex and error-prone!")
    
    return flattened_config


def demonstrate_your_approach():
    """Your approach: Keep nested structure, direct override."""
    print("\n🚀 Your Better Approach: Direct Nested Override")
    print("=" * 50)
    
    # Start with nested config (keep it nested!)
    nested_config = {
        'database': {
            'develope': {
                'db_url': 'sqlite:///default.db',
                'pool_size': 10
            }
        },
        'llm': {
            'openai': {
                'api_key': 'default-key'
            }
        }
    }
    
    print("📊 Original nested config:")
    import json
    print(json.dumps(nested_config, indent=2))
    
    # Step 1: Create mapping from ENV_VAR to path in nested structure
    def create_env_mapping(nested_dict, path=[]):
        """Create mapping from ENV_VAR format to nested path."""
        mapping = {}
        for key, value in nested_dict.items():
            current_path = path + [key]
            env_key = '__'.join([p.upper() for p in current_path])
            
            if isinstance(value, dict):
                # Recursively process nested dicts
                mapping.update(create_env_mapping(value, current_path))
            else:
                # Store the path to this value
                mapping[env_key] = current_path
        return mapping
    
    env_mapping = create_env_mapping(nested_config)
    print(f"\n📋 Environment variable mapping:")
    for env_var, path in env_mapping.items():
        print(f"   {env_var} → {'.'.join(path)}")
    
    # Step 2: Apply environment variables directly to nested structure
    env_vars = {
        'DATABASE__DEVELOPE__DB_URL': 'postgresql://localhost:5432/dev',
        'DATABASE__DEVELOPE__POOL_SIZE': '20'
    }
    
    print(f"\n🔄 Applying environment variables...")
    for env_var, env_value in env_vars.items():
        if env_var in env_mapping:
            path = env_mapping[env_var]
            
            # Navigate to the nested location
            current = nested_config
            for key in path[:-1]:
                current = current[key]
            
            # Get old value for type conversion
            old_value = current[path[-1]]
            
            # Override directly in nested structure
            current[path[-1]] = int(env_value) if isinstance(old_value, int) else env_value
            
            print(f"   ✅ {env_var} → {'.'.join(path)}: {old_value} → {current[path[-1]]}")
    
    print(f"\n📊 Final nested config:")
    print(json.dumps(nested_config, indent=2))
    
    print(f"\n✅ Advantages:")
    print(f"   • Direct override in nested structure")
    print(f"   • No need to rebuild from flat keys")
    print(f"   • Cleaner, more intuitive")
    print(f"   • Preserves original data structure")
    
    return nested_config


def demonstrate_access_patterns(nested_config):
    """Show how access patterns work with nested config."""
    print(f"\n🎯 Access Patterns with Nested Config")
    print("=" * 40)
    
    # Direct nested access
    print(f"Direct access: nested_config['database']['develope']['db_url']")
    print(f"   Result: {nested_config['database']['develope']['db_url']}")
    
    # Section access
    print(f"\nSection access: nested_config['database']")
    database_section = nested_config['database']
    print(f"   Result: {database_section}")
    print(f"   Then: database_section['develope']['db_url']")
    print(f"   Result: {database_section['develope']['db_url']}")
    
    # Dot notation helper (can be implemented)
    def get_nested(config, dot_path, default=None):
        """Helper to access nested config with dot notation."""
        parts = dot_path.split('.')
        current = config
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return default
        return current
    
    print(f"\nDot notation helper: get_nested(config, 'database.develope.db_url')")
    print(f"   Result: {get_nested(nested_config, 'database.develope.db_url')}")
    
    print(f"\nDot notation helper: get_nested(config, 'llm.openai.api_key')")
    print(f"   Result: {get_nested(nested_config, 'llm.openai.api_key')}")


def main():
    """Compare both approaches."""
    print("🔍 Environment Variable Override Approaches Comparison")
    print("=" * 60)
    
    # Set up test environment
    os.environ['DATABASE__DEVELOPE__DB_URL'] = 'postgresql://localhost:5432/dev'
    os.environ['DATABASE__DEVELOPE__POOL_SIZE'] = '20'
    
    try:
        # Demonstrate current approach
        flattened_result = demonstrate_current_approach()
        
        # Demonstrate your better approach
        nested_result = demonstrate_your_approach()
        
        # Show access patterns
        demonstrate_access_patterns(nested_result)
        
        print(f"\n🎯 Conclusion:")
        print(f"   Your approach is better because:")
        print(f"   1. ✅ Direct override in original data structure")
        print(f"   2. ✅ No complex reconstruction needed")
        print(f"   3. ✅ Preserves natural nested access patterns")
        print(f"   4. ✅ Cleaner separation of concerns")
        print(f"   5. ✅ More intuitive and maintainable")
        
    finally:
        # Clean up environment
        for var in ['DATABASE__DEVELOPE__DB_URL', 'DATABASE__DEVELOPE__POOL_SIZE']:
            if var in os.environ:
                del os.environ[var]


if __name__ == "__main__":
    main()
