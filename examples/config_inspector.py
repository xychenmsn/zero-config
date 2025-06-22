#!/usr/bin/env python3
"""
Configuration inspector for zero_config.

This script helps you inspect and debug your zero_config setup.
"""

import argparse
import json
import sys
from pathlib import Path
from zero_config import setup_environment, get_config


def inspect_config(show_all=False, show_defaults=False, format_json=False):
    """Inspect the current configuration."""
    
    try:
        setup_environment()
        config = get_config()
    except Exception as e:
        print(f"❌ Error setting up configuration: {e}", file=sys.stderr)
        return 1
    
    if show_defaults:
        print("📋 Default Configuration:")
        print("=" * 50)
        print("Zero Config uses no built-in defaults - configuration comes from environment variables and .env.zero_config files.")
        return 0
    else:
        print("📋 Current Configuration:")
        print("=" * 50)
        data = config.to_dict()
        if not data:
            print("No configuration values found. Try setting environment variables or creating a .env.zero_config file.")
            return 0
    
    if format_json:
        # JSON output
        print(json.dumps(data, indent=2, default=str))
    else:
        # Human-readable output
        for key, value in sorted(data.items()):
            if not show_all and 'key' in key.lower() and value:
                # Mask API keys for security unless show_all is True
                masked_value = f"{str(value)[:10]}..." if len(str(value)) > 10 else "[masked]"
                print(f"{key:25} = {masked_value}")
            else:
                print(f"{key:25} = {value}")
    
    return 0


def check_environment():
    """Check environment variables and files."""
    
    print("🔍 Environment Check:")
    print("=" * 50)
    
    # Check for API keys
    import os
    api_keys = ['OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 'GOOGLE_API_KEY']
    
    print("\n🔑 API Keys:")
    for key in api_keys:
        value = os.getenv(key)
        if value:
            print(f"  ✅ {key}: Set ({len(value)} chars)")
        else:
            print(f"  ❌ {key}: Not set")
    
    # Check for uppercase environment variables
    print("\n⚙️  Uppercase Environment Variables:")
    uppercase_vars = [k for k in os.environ.keys() if k.isupper() and not k.startswith('_')]
    if uppercase_vars:
        # Show first 10 to avoid spam
        for var in sorted(uppercase_vars)[:10]:
            value = os.environ[var]
            if len(value) > 50:
                value = value[:47] + "..."
            print(f"  ✅ {var}: {value}")
        if len(uppercase_vars) > 10:
            print(f"  ... and {len(uppercase_vars) - 10} more")
    else:
        print("  ❌ No uppercase environment variables found")
    
    # Check for .env.zero_config file
    print("\n📄 Configuration Files:")
    try:
        setup_environment()
        config = get_config()
        project_root = Path(config._project_root)
        
        env_file = project_root / ".env.zero_config"
        if env_file.exists():
            print(f"  ✅ .env.zero_config: Found at {env_file}")
            print(f"     Size: {env_file.stat().st_size} bytes")
        else:
            print(f"  ❌ .env.zero_config: Not found in {project_root}")
        
        # Check for example file
        example_file = project_root / ".env.zero_config.example"
        if example_file.exists():
            print(f"  ℹ️  .env.zero_config.example: Found at {example_file}")
        
    except Exception as e:
        print(f"  ❌ Error checking files: {e}")
    
    return 0


def main():
    """Main CLI function."""
    
    parser = argparse.ArgumentParser(
        description="Inspect zero_config configuration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    # Show current config (masked API keys)
  %(prog)s --all              # Show all config including full API keys
  %(prog)s --defaults         # Show default configuration
  %(prog)s --json             # Output in JSON format
  %(prog)s --check            # Check environment and files
        """
    )
    
    parser.add_argument(
        '--all', 
        action='store_true',
        help='Show all configuration values including full API keys'
    )
    
    parser.add_argument(
        '--defaults',
        action='store_true', 
        help='Show default configuration instead of current'
    )
    
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output configuration in JSON format'
    )
    
    parser.add_argument(
        '--check',
        action='store_true',
        help='Check environment variables and configuration files'
    )
    
    args = parser.parse_args()
    
    if args.check:
        return check_environment()
    else:
        return inspect_config(
            show_all=args.all,
            show_defaults=args.defaults,
            format_json=args.json
        )


if __name__ == "__main__":
    sys.exit(main())
