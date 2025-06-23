#!/usr/bin/env python3
"""
Alternative implementation of environment variable matching.

This demonstrates your suggested approach of flattening the config dict 
to __ separated keys for direct lookup against environment variables.
"""

import os
from typing import Dict, Any


def _flatten_to_env_format(nested_dict: Dict[str, Any], parent_key: str = '', separator: str = '__') -> Dict[str, str]:
    """
    Flatten a nested dictionary to environment variable format (UPPER__CASE__KEYS).
    
    Args:
        nested_dict: The nested dictionary to flatten
        parent_key: The parent key prefix (used for recursion)
        separator: The separator to use between keys (default: '__')
    
    Returns:
        A dictionary mapping ENV_VAR_FORMAT keys to their dot notation equivalents
    
    Example:
        {'database': {'develop': {'db_url': 'test'}}} 
        -> {'DATABASE__DEVELOP__DB_URL': 'database.develop.db_url'}
    """
    items = []
    for key, value in nested_dict.items():
        # Build the environment variable format key
        env_key = f"{parent_key}{separator}{key.upper()}" if parent_key else key.upper()
        # Build the dot notation key
        dot_key = f"{parent_key.lower().replace('__', '.')}.{key}" if parent_key else key
        
        if isinstance(value, dict):
            # Recursively flatten nested dictionaries
            items.extend(_flatten_to_env_format(value, env_key, separator).items())
        else:
            # Store mapping from ENV_FORMAT -> dot.notation
            items.append((env_key, dot_key))
    
    return dict(items)


def apply_environment_variables_alternative(config: Dict[str, Any]) -> None:
    """
    Alternative implementation: Flatten config to __ format for direct env var lookup.
    
    Your suggested approach:
    1. Flatten the config dict to __ separated keys
    2. Direct lookup of environment variables
    3. Apply matches
    """
    
    # Step 1: Create mapping from ENV_VAR_FORMAT to dot.notation keys
    # We need to reconstruct the nested structure from the flat config first
    nested_config = _reconstruct_nested_from_flat(config)
    env_to_dot_mapping = _flatten_to_env_format(nested_config)
    
    print(f"📋 Environment variable mapping created:")
    for env_key, dot_key in sorted(env_to_dot_mapping.items()):
        print(f"   {env_key} → {dot_key}")
    
    # Step 2: Direct lookup and apply environment variables
    matches_found = 0
    for env_var, env_value in os.environ.items():
        if env_var.isupper():
            # Skip project_root - it's handled separately
            if env_var == 'PROJECT_ROOT':
                continue
                
            # Direct lookup in the mapping
            if env_var in env_to_dot_mapping:
                dot_key = env_to_dot_mapping[env_var]
                if dot_key in config:
                    # Apply the environment variable override
                    old_value = config[dot_key]
                    config[dot_key] = smart_convert_simple(env_value, old_value)
                    matches_found += 1
                    print(f"✅ Applied {env_var} → {dot_key}: {old_value} → {config[dot_key]}")
            else:
                print(f"❌ Skipped {env_var} (no corresponding config key)")
    
    print(f"\n📊 Summary: Applied {matches_found} environment variable overrides")


def _reconstruct_nested_from_flat(flat_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Reconstruct nested dictionary from flat dot notation keys.
    
    This is needed because we start with a flat config dict and need to 
    create the nested structure to then flatten it to __ format.
    """
    nested = {}
    for key, value in flat_config.items():
        if '.' in key:
            parts = key.split('.')
            current = nested
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            current[parts[-1]] = value
        else:
            nested[key] = value
    return nested


def smart_convert_simple(str_value: str, default_value: Any) -> Any:
    """Simplified version of smart_convert for demo purposes."""
    if isinstance(default_value, str):
        return str_value
    elif isinstance(default_value, int):
        try:
            return int(str_value)
        except ValueError:
            return str_value
    elif isinstance(default_value, float):
        try:
            return float(str_value)
        except ValueError:
            return str_value
    elif isinstance(default_value, bool):
        return str_value.lower() in ('true', '1', 'yes', 'on', 'enabled')
    else:
        return str_value


def demonstrate_alternative_approach():
    """Demonstrate the alternative approach with a real example."""
    print("🚀 Alternative Environment Variable Matching Approach")
    print("=" * 55)
    
    # Set up test environment variables
    os.environ['DATABASE__DEVELOPE__DB_URL'] = 'postgresql://localhost:5432/dev'
    os.environ['DATABASE__DEVELOPE__POOL_SIZE'] = '20'
    os.environ['LLM__OPENAI__API_KEY'] = 'sk-alternative-test'
    os.environ['UNRELATED_VAR'] = 'should_not_match'
    
    # Sample flat config (as it would be after flattening defaults)
    config = {
        'database.develope.db_url': 'sqlite:///default.db',
        'database.develope.pool_size': 10,
        'database.develope.timeout': 30,
        'llm.openai.api_key': 'default-key',
        'llm.openai.model': 'gpt-3.5-turbo',
        'simple_key': 'default_value',
        'project_root': '/some/path'
    }
    
    print(f"\n📊 Initial config:")
    for key, value in sorted(config.items()):
        print(f"   {key}: {value}")
    
    print(f"\n🔄 Applying environment variables...")
    apply_environment_variables_alternative(config)
    
    print(f"\n📊 Final config:")
    for key, value in sorted(config.items()):
        print(f"   {key}: {value}")
    
    # Clean up
    for var in ['DATABASE__DEVELOPE__DB_URL', 'DATABASE__DEVELOPE__POOL_SIZE', 
                'LLM__OPENAI__API_KEY', 'UNRELATED_VAR']:
        if var in os.environ:
            del os.environ[var]


if __name__ == "__main__":
    demonstrate_alternative_approach()
