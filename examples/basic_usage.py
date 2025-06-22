#!/usr/bin/env python3
"""
Basic usage example for zero_config.

This example demonstrates how to use zero_config in a typical application.
"""

import os
from zero_config import setup_environment, get_config


def main():
    """Demonstrate basic zero_config usage."""

    print("🚀 Zero Config Example")
    print("=" * 50)

    # Example default configuration (optional)
    default_config = {
        'temperature': 0.0,
        'max_tokens': 1024,
        'timeout': 30,
        'debug': False,
        'models': ['gpt-4o-mini'],
    }

    # Initialize configuration with defaults (call this once at startup)
    setup_environment(default_config=default_config)

    # Get the global configuration object
    config = get_config()
    
    print("\n📋 Configuration Values:")
    print("-" * 30)
    
    # Access configuration values (from defaults, env vars, or .env.zero_config)
    print(f"Temperature: {config.get('temperature')}")
    print(f"Max Tokens: {config.get('max_tokens')}")
    print(f"Timeout: {config.get('timeout')}")
    print(f"Debug: {config.get('debug')}")
    print(f"Models: {config.get('models')}")
    
    # Check API keys
    print(f"\n🔑 API Keys:")
    print("-" * 15)
    
    openai_key = config.get('openai_api_key')
    if openai_key:
        print(f"OpenAI API Key: {openai_key[:10]}..." if len(openai_key) > 10 else "OpenAI API Key: [short key]")
    else:
        print("OpenAI API Key: Not configured")
    
    anthropic_key = config.get('anthropic_api_key')
    if anthropic_key:
        print(f"Anthropic API Key: {anthropic_key[:10]}..." if len(anthropic_key) > 10 else "Anthropic API Key: [short key]")
    else:
        print("Anthropic API Key: Not configured")
    
    # Show configured values
    print(f"\n⚙️  Configured Values:")
    print("-" * 22)
    config_dict = config.to_dict()
    if config_dict:
        for key, value in sorted(config_dict.items()):
            if 'key' in key.lower() and value:
                # Mask API keys for security
                print(f"{key}: {str(value)[:10]}..." if len(str(value)) > 10 else f"{key}: [masked]")
            else:
                print(f"{key}: {value}")
    else:
        print("No configuration values set. Try setting some environment variables!")
    
    # Demonstrate dynamic path helpers (Ruby on Rails style)
    print(f"\n📁 Dynamic Path Helpers:")
    print("-" * 25)
    print(f"Data Directory: {config.data_path()}")
    print(f"Database Path: {config.data_path('app.db')}")
    print(f"Logs Directory: {config.logs_path()}")
    print(f"Log File Path: {config.logs_path('app.log')}")
    print(f"Cache Directory: {config.cache_path()}")
    print(f"Cache File: {config.cache_path('session.json')}")
    print(f"Temp Directory: {config.temp_path()}")
    print(f"Models File: {config.models_path('gpt4.bin')}")
    print(f"Uploads Directory: {config.uploads_path()}")
    print(f"Static File: {config.static_path('style.css')}")
    
    # Show configuration sources
    print(f"\n🔧 Configuration Tips:")
    print("-" * 22)
    print("1. Set API keys via environment variables:")
    print("   export OPENAI_API_KEY='sk-your-key-here'")
    print("   export ANTHROPIC_API_KEY='sk-ant-your-key-here'")
    print()
    print("2. Override settings with uppercase environment variables:")
    print("   export TEMPERATURE='0.7'")
    print("   export MAX_TOKENS='2048'")
    print("   export DEBUG='true'")
    print("   export MODELS='[\"gpt-4\", \"claude-3\"]'  # JSON array (only format)")
    print("   export DATABASE_URL='host1,host2,host3'   # Stays as string (safe!)")
    print("   export WELCOME='Hello, world!'            # Stays as string (safe!)")
    print()
    print("3. Create .env.zero_config file in project root:")
    print("   temperature=0.2")
    print("   max_tokens=1500")
    print("   debug=true")
    print('   models=["gpt-4", "claude-3"]  # JSON array (only format)')
    print('   database_url=postgresql://host1,host2,host3/db  # Safe string')
    print('   welcome_message=Hello, welcome!  # Safe string')
    
    # Show all configuration (for debugging)
    if os.getenv('SHOW_ALL_CONFIG'):
        print(f"\n🔍 All Configuration (DEBUG):")
        print("-" * 32)
        all_config = config.to_dict()
        for key, value in sorted(all_config.items()):
            if 'key' in key.lower() and value:
                # Mask API keys for security
                print(f"{key}: {str(value)[:10]}..." if len(str(value)) > 10 else f"{key}: [masked]")
            else:
                print(f"{key}: {value}")


if __name__ == "__main__":
    main()
