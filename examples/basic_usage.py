#!/usr/bin/env python3
"""
Basic usage example for zero_config.

This example demonstrates how to use zero_config in a typical application.
"""

import os
from zero_config import setup_environment, get_config, data_path, logs_path


def main():
    """Demonstrate basic zero_config usage."""
    
    print("🚀 Zero Config Example")
    print("=" * 50)
    
    # Initialize configuration (call this once at startup)
    setup_environment()
    
    # Get the global configuration object
    config = get_config()
    
    print("\n📋 Configuration Values:")
    print("-" * 30)
    
    # Access configuration values
    print(f"Default Model: {config.get('default_model')}")
    print(f"Temperature: {config.get('temperature')}")
    print(f"Max Tokens: {config.get('max_tokens')}")
    print(f"Timeout: {config.get('timeout')} seconds")
    
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
    
    # Show available models
    print(f"\n🤖 Available Models:")
    print("-" * 20)
    print(f"OpenAI Models: {', '.join(config.get('openai_models', [])[:3])}...")
    print(f"Anthropic Models: {', '.join(config.get('anthropic_models', [])[:2])}...")
    print(f"Google Models: {', '.join(config.get('google_models', [])[:2])}...")
    
    # Demonstrate path helpers
    print(f"\n📁 Path Helpers:")
    print("-" * 16)
    print(f"Data Directory: {data_path()}")
    print(f"Database Path: {data_path('app.db')}")
    print(f"Logs Directory: {logs_path()}")
    print(f"Log File Path: {logs_path('app.log')}")
    
    # Show configuration sources
    print(f"\n🔧 Configuration Tips:")
    print("-" * 22)
    print("1. Set API keys via environment variables:")
    print("   export OPENAI_API_KEY='sk-your-key-here'")
    print("   export ANTHROPIC_API_KEY='sk-ant-your-key-here'")
    print()
    print("2. Override settings with ZERO_CONFIG_ prefix:")
    print("   export ZERO_CONFIG_TEMPERATURE='0.7'")
    print("   export ZERO_CONFIG_MAX_TOKENS='2048'")
    print()
    print("3. Create .env.zero_config file in project root:")
    print("   temperature=0.2")
    print("   max_tokens=1500")
    print("   log_calls=true")
    
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
