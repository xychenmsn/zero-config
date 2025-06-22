#!/usr/bin/env python3
"""
Safety demonstration for zero_config.

This example shows how zero_config safely handles comma-containing values
and provides explicit, predictable type conversion.
"""

import os
from zero_config import setup_environment, get_config


def main():
    """Demonstrate zero_config safety features."""
    
    print("🛡️  Zero Config Safety Demonstration")
    print("=" * 50)
    
    # Configuration that might contain commas
    default_config = {
        # Database connections often have comma-separated hosts
        'database_url': '',
        'redis_cluster': '',
        
        # Natural language often contains commas
        'welcome_message': '',
        'error_message': '',
        
        # API endpoints might have comma-separated query params
        'api_endpoint': '',
        'search_url': '',
        
        # CSV-like data that should stay as string
        'allowed_extensions': '',
        'csv_headers': '',
        
        # Lists that should be explicit
        'models': [],
        'servers': [],
        'features': [],
        
        # Numbers and booleans
        'port': 8000,
        'timeout': 30.0,
        'debug': False,
        'enabled': True,
    }
    
    # Set up problematic environment variables
    os.environ.update({
        # Comma-containing strings that should stay as strings
        'DATABASE_URL': 'postgresql://host1,host2,host3:5432/mydb',
        'REDIS_CLUSTER': 'redis://node1:6379,node2:6379,node3:6379',
        'WELCOME_MESSAGE': 'Hello, welcome to our app!',
        'ERROR_MESSAGE': 'Error: Invalid input, please try again.',
        'API_ENDPOINT': 'https://api.com/search?q=item1,item2&format=json',
        'SEARCH_URL': 'https://search.com/api?tags=red,blue,green&limit=10',
        'ALLOWED_EXTENSIONS': 'jpg,png,gif,pdf,doc,docx',
        'CSV_HEADERS': 'name,age,city,country',
        
        # Explicit JSON lists
        'MODELS': '["gpt-4", "claude-3", "gemini-pro"]',
        'SERVERS': '["web1.example.com", "web2.example.com"]',
        'FEATURES': '["auth", "payments", "analytics"]',
        
        # Numbers and booleans
        'PORT': '3000',
        'TIMEOUT': '45.5',
        'DEBUG': 'true',
        'ENABLED': 'false',
    })
    
    setup_environment(default_config=default_config)
    config = get_config()
    
    print("\n🔍 Comma-Containing Strings (Stay Safe as Strings):")
    print("-" * 55)
    
    comma_strings = [
        ('database_url', 'Database URL'),
        ('redis_cluster', 'Redis Cluster'),
        ('welcome_message', 'Welcome Message'),
        ('error_message', 'Error Message'),
        ('api_endpoint', 'API Endpoint'),
        ('search_url', 'Search URL'),
        ('allowed_extensions', 'Allowed Extensions'),
        ('csv_headers', 'CSV Headers'),
    ]
    
    for key, label in comma_strings:
        value = config.get(key)
        print(f"{label:18}: {repr(value)}")
        print(f"{'Type':18}: {type(value).__name__}")
        print()
    
    print("📋 Explicit JSON Lists (Converted to Lists):")
    print("-" * 45)
    
    list_configs = [
        ('models', 'Models'),
        ('servers', 'Servers'),
        ('features', 'Features'),
    ]
    
    for key, label in list_configs:
        value = config.get(key)
        print(f"{label:10}: {value}")
        print(f"{'Type':10}: {type(value).__name__}")
        print()
    
    print("🔢 Numbers and Booleans (Type Converted):")
    print("-" * 42)
    
    typed_configs = [
        ('port', 'Port'),
        ('timeout', 'Timeout'),
        ('debug', 'Debug'),
        ('enabled', 'Enabled'),
    ]
    
    for key, label in typed_configs:
        value = config.get(key)
        print(f"{label:8}: {value} ({type(value).__name__})")
    
    print("\n✅ Safety Summary:")
    print("-" * 18)
    print("• Comma-containing strings are preserved as strings")
    print("• Only explicit JSON arrays become lists")
    print("• Numbers are converted with safe fallback")
    print("• Booleans support multiple formats")
    print("• No unexpected list splitting!")
    
    print("\n🚫 What Other Libraries Might Do Wrong:")
    print("-" * 40)
    print("• database_url → ['postgresql://host1', 'host2', 'host3:5432/mydb'] ❌")
    print("• welcome_message → ['Hello', 'welcome to our app!'] ❌")
    print("• api_endpoint → ['https://api.com/search?q=item1', 'item2&format=json'] ❌")
    
    print("\n✅ What Zero Config Does Right:")
    print("-" * 32)
    print("• database_url → 'postgresql://host1,host2,host3:5432/mydb' ✅")
    print("• welcome_message → 'Hello, welcome to our app!' ✅")
    print("• models → ['gpt-4', 'claude-3', 'gemini-pro'] ✅ (explicit JSON)")


if __name__ == "__main__":
    main()
