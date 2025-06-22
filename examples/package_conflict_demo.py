#!/usr/bin/env python3
"""
Demo showing how zero-config prevents package conflicts.

This simulates the scenario where:
1. A main project (like "news app") initializes zero-config first
2. A package dependency (like "united_llm") also tries to initialize zero-config
3. The second initialization is safely ignored to prevent conflicts
"""

from zero_config import setup_environment, get_config, is_initialized, get_initialization_info


def simulate_main_project():
    """Simulate main project initialization."""
    print("🏠 Main Project: Initializing zero-config...")
    
    # Main project defines its configuration
    main_config = {
        'app_name': 'news_app',
        'database.host': 'localhost',
        'database.port': 5432,
        'llm.api_key': 'main-project-key',
        'llm.temperature': 0.5,
        'debug': True
    }
    
    setup_environment(default_config=main_config)
    
    print(f"✅ Main Project: Initialized by {get_initialization_info()}")
    print(f"   Configuration keys: {list(get_config().to_dict().keys())}")
    print()


def simulate_package_dependency():
    """Simulate package dependency trying to initialize."""
    print("📦 Package (united_llm): Attempting to initialize zero-config...")
    
    # Package tries to define its own configuration
    package_config = {
        'llm.temperature': 0.7,  # Different from main project
        'llm.max_tokens': 2048,
        'package_name': 'united_llm',
        'package_version': '1.0.0'
    }
    
    # This call will be ignored because main project already initialized
    setup_environment(default_config=package_config)
    
    print(f"ℹ️  Package: Already initialized by {get_initialization_info()}")
    print(f"   Package can still access main project's config:")
    
    config = get_config()
    print(f"   - app_name: {config.get('app_name')}")
    print(f"   - llm.api_key: {config.get('llm.api_key')}")
    print(f"   - llm.temperature: {config.get('llm.temperature')} (from main project, not package)")
    print(f"   - package_name: {config.get('package_name')} (None - package config ignored)")
    print()


def demonstrate_force_reinit():
    """Demonstrate force re-initialization (not recommended in production)."""
    print("⚠️  Demonstrating force re-initialization (use with caution)...")
    
    force_config = {
        'forced': True,
        'warning': 'This can break package dependencies!'
    }
    
    setup_environment(default_config=force_config, force_reinit=True)
    
    config = get_config()
    print(f"🔄 Force re-initialized by {get_initialization_info()}")
    print(f"   New config: {config.to_dict()}")
    print()


def main():
    """Run the demo."""
    print("🚀 Zero-Config Package Conflict Prevention Demo")
    print("=" * 50)
    print()
    
    # Check initial state
    print(f"Initial state - Is initialized? {is_initialized()}")
    print()
    
    # Simulate main project initialization
    simulate_main_project()
    
    # Simulate package trying to initialize
    simulate_package_dependency()
    
    # Show section access still works
    print("🔍 Section Access Demo:")
    config = get_config()
    llm_section = config.get('llm')
    database_section = config.get('database')
    
    print(f"   LLM section: {llm_section}")
    print(f"   Database section: {database_section}")
    print()
    
    # Demonstrate force reinit (not recommended)
    demonstrate_force_reinit()
    
    print("✅ Demo complete!")
    print()
    print("Key takeaways:")
    print("- Main project initializes zero-config first")
    print("- Package dependencies can't accidentally override configuration")
    print("- Packages can still access the main project's configuration")
    print("- Use force_reinit=True only in special cases (testing, etc.)")


if __name__ == "__main__":
    main()
