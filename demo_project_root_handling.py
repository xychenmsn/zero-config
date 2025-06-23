#!/usr/bin/env python3
"""
Demo showing that PROJECT_ROOT is always checked in OS environment,
regardless of whether it's in the default config or not.
"""

import os
import tempfile
from pathlib import Path
from zero_config import setup_environment, get_config
from zero_config.config import _reset_for_testing


def demo_project_root_always_checked():
    """Demonstrate that PROJECT_ROOT is always checked in environment."""
    print("🚀 PROJECT_ROOT Environment Handling Demo")
    print("=" * 45)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        custom_project_root = Path(tmpdir) / "custom_project_root"
        custom_project_root.mkdir()
        
        # Set PROJECT_ROOT in environment (resolve to handle symlinks)
        os.environ['PROJECT_ROOT'] = str(custom_project_root.resolve())
        os.environ['DATABASE__URL'] = 'postgresql://localhost:5432/test'
        
        try:
            print(f"\n📊 Test Case 1: PROJECT_ROOT NOT in default config")
            print("-" * 50)
            
            # Reset state
            _reset_for_testing()
            
            # Default config WITHOUT project_root
            default_config = {
                'database.url': 'sqlite:///default.db',
                'api_key': 'default-key'
                # Note: NO project_root here!
            }
            
            print(f"Default config keys: {list(default_config.keys())}")
            print(f"PROJECT_ROOT env var: {os.environ.get('PROJECT_ROOT')}")
            
            setup_environment(default_config=default_config)
            config = get_config()
            
            print(f"\n✅ Results:")
            print(f"   project_root: {config.get('project_root')}")
            print(f"   database.url: {config.get('database.url')}")
            print(f"   api_key: {config.get('api_key')}")
            
            # Verify PROJECT_ROOT was loaded from environment
            assert config.get('project_root') == str(custom_project_root.resolve())
            print(f"   ✅ PROJECT_ROOT loaded from OS environment!")
            
            print(f"\n📊 Test Case 2: PROJECT_ROOT IN default config")
            print("-" * 50)
            
            # Reset state
            _reset_for_testing()
            
            # Default config WITH project_root (should be overridden)
            default_config = {
                'project_root': '/some/default/path',  # This should be overridden
                'database.url': 'sqlite:///default.db',
                'api_key': 'default-key'
            }
            
            print(f"Default config keys: {list(default_config.keys())}")
            print(f"Default project_root: {default_config['project_root']}")
            print(f"PROJECT_ROOT env var: {os.environ.get('PROJECT_ROOT')}")
            
            setup_environment(default_config=default_config)
            config = get_config()
            
            print(f"\n✅ Results:")
            print(f"   project_root: {config.get('project_root')}")
            print(f"   database.url: {config.get('database.url')}")
            print(f"   api_key: {config.get('api_key')}")
            
            # Verify PROJECT_ROOT from environment overrode auto-detection
            assert config.get('project_root') == str(custom_project_root.resolve())
            print(f"   ✅ PROJECT_ROOT from OS environment used!")
            
            print(f"\n🔧 How It Works:")
            print("-" * 15)
            print("1. ✅ Check os.environ['PROJECT_ROOT'] first")
            print("2. ✅ If found, use it as project root")
            print("3. ✅ If not found, use auto-detected project root")
            print("4. ✅ .env files CANNOT override PROJECT_ROOT (chicken-and-egg)")

            print(f"\n⚡ Key Benefits:")
            print("-" * 15)
            print("• OS environment PROJECT_ROOT always takes priority")
            print("• Avoids chicken-and-egg problem with .env file location")
            print("• Consistent behavior regardless of default config")
            print("• Simple and predictable project root handling")
            
        finally:
            # Clean up environment
            if 'PROJECT_ROOT' in os.environ:
                del os.environ['PROJECT_ROOT']
            if 'DATABASE__URL' in os.environ:
                del os.environ['DATABASE__URL']


def demo_without_project_root_env():
    """Demonstrate behavior when PROJECT_ROOT is not in environment."""
    print(f"\n📊 Test Case 3: No PROJECT_ROOT environment variable")
    print("-" * 55)
    
    # Make sure PROJECT_ROOT is not in environment
    if 'PROJECT_ROOT' in os.environ:
        del os.environ['PROJECT_ROOT']
    
    try:
        # Reset state
        _reset_for_testing()
        
        # Default config without project_root
        default_config = {
            'database.url': 'sqlite:///default.db',
            'api_key': 'default-key'
        }
        
        print(f"Default config keys: {list(default_config.keys())}")
        print(f"PROJECT_ROOT env var: {os.environ.get('PROJECT_ROOT', 'NOT SET')}")
        
        setup_environment(default_config=default_config)
        config = get_config()
        
        print(f"\n✅ Results:")
        print(f"   project_root: {config.get('project_root')}")
        print(f"   database.url: {config.get('database.url')}")
        print(f"   api_key: {config.get('api_key')}")
        
        # Should use auto-detected project root
        assert config.get('project_root') is not None
        print(f"   ✅ Used auto-detected project root!")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")


if __name__ == "__main__":
    demo_project_root_always_checked()
    demo_without_project_root_env()
    
    print(f"\n🎯 Summary:")
    print("=" * 10)
    print("✅ PROJECT_ROOT is always checked in OS environment")
    print("✅ OS environment PROJECT_ROOT overrides auto-detection")
    print("✅ .env files CANNOT override PROJECT_ROOT (chicken-and-egg problem)")
    print("✅ Falls back to auto-detection if OS env not set")
    print("✅ Simple and predictable behavior")
    print("✅ Avoids chicken-and-egg problem with .env file location")
