#!/usr/bin/env python3
"""
Advanced features example for zero_config.

This example demonstrates:
1. Dynamic path helpers (Ruby on Rails style)
2. Section headers for organized configuration
"""

from zero_config import setup_environment, get_config


def main():
    """Demonstrate advanced zero_config features."""
    
    print("🚀 Zero Config Advanced Features")
    print("=" * 50)
    
    # Example configuration with section headers
    default_config = {
        # Simple configuration
        'debug': False,
        'port': 8000,
        
        # LLM section
        'llm.models': ['gpt-4o-mini'],
        'llm.temperature': 0.0,
        'llm.max_tokens': 1024,
        'llm.timeout': 30,
        
        # Database section
        'database.host': 'localhost',
        'database.port': 5432,
        'database.name': 'myapp',
        'database.ssl': True,
        
        # Cache section
        'cache.redis_url': 'redis://localhost:6379',
        'cache.ttl': 3600,
        'cache.enabled': True,
    }
    
    print("\n📋 Default Configuration:")
    print("-" * 30)
    for key, value in default_config.items():
        print(f"{key}: {value}")
    
    # Initialize configuration
    setup_environment(default_config=default_config)
    config = get_config()
    
    print("\n⚙️  Current Configuration (after env vars):")
    print("-" * 45)
    for key, value in sorted(config.to_dict().items()):
        print(f"{key}: {value}")
    
    print("\n🏗️  Section Header Examples:")
    print("-" * 32)
    print("Set these environment variables to override:")
    print("  export LLM__MODELS='[\"gpt-4\", \"claude-3\"]'  # JSON array")
    print("  export LLM__TEMPERATURE='0.7'                  # Float")
    print("  export DATABASE__HOST='remote.db.com'          # String")
    print("  export DATABASE__PORT='3306'                   # Int")
    print("  export CACHE__ENABLED='false'                  # Bool")
    
    print(f"\nLLM Models: {config.get('llm.models')}")
    print(f"LLM Temperature: {config.get('llm.temperature')}")
    print(f"Database Host: {config.get('database.host')}")
    print(f"Database Port: {config.get('database.port')}")
    print(f"Cache Enabled: {config.get('cache.enabled')}")

    print("\n📦 Section Configuration Access:")
    print("-" * 35)
    print("Get entire sections with config.get_section('section_name'):")

    llm_section = config.get_section('llm')
    print(f"LLM Section: {llm_section}")

    database_section = config.get_section('database')
    print(f"Database Section: {database_section}")

    cache_section = config.get_section('cache')
    print(f"Cache Section: {cache_section}")

    # Show that it returns clean keys without section prefix
    print(f"\nLLM models from section: {llm_section.get('models')}")
    print(f"Database host from section: {database_section.get('host')}")

    print("\n🛤️  Dynamic Path Helpers (Ruby on Rails Style):")
    print("-" * 52)
    
    # Demonstrate dynamic path helpers
    paths_to_demo = [
        ('cache_path', 'session.json'),
        ('models_path', 'gpt4.bin'),
        ('uploads_path', 'document.pdf'),
        ('exports_path', 'data.csv'),
        ('backups_path', 'backup.tar.gz'),
        ('assets_path', 'logo.png'),
        ('temp_path', 'processing.tmp'),
        ('logs_path', 'app.log'),  # Built-in
        ('data_path', 'database.db'),  # Built-in
    ]
    
    for path_method, filename in paths_to_demo:
        # Get the path helper function dynamically
        path_func = getattr(config, path_method)
        
        # Call with and without filename
        dir_path = path_func()
        file_path = path_func(filename)
        
        print(f"config.{path_method}():")
        print(f"  Directory: {dir_path}")
        print(f"  File:      {file_path}")
    
    print("\n🔧 How Dynamic Paths Work:")
    print("-" * 30)
    print("1. You call: config.cache_path('file.txt')")
    print("2. Python calls: config.__getattr__('cache_path')")
    print("3. Zero Config detects '_path' suffix")
    print("4. Extracts 'cache' as directory name")
    print("5. Returns function that creates /project/cache/* paths")
    print("6. Function is called with 'file.txt'")
    print("7. Result: /project/cache/file.txt")
    
    print("\n✨ This works for ANY directory name:")
    print("-" * 40)
    print("config.my_custom_dir_path('file.txt')  # /project/my_custom_dir/file.txt")
    print("config.user_uploads_path()             # /project/user_uploads/")
    print("config.ml_models_path('model.pkl')     # /project/ml_models/model.pkl")
    
    # Demonstrate it actually works
    custom_path = config.my_custom_dir_path('test.txt')
    print(f"\nActual example: {custom_path}")


if __name__ == "__main__":
    main()
